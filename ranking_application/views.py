from django.shortcuts import render, redirect, HttpResponseRedirect, reverse
from django.db.models import Max
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from .forms import NewProject, EditProject, NewRequirement, EditRequirement, AssignUsers
from .models import project, project_owned_by, app_user, requirement, project_assignees, ranking, assigned_criteria
from django.contrib import messages
import pandas
import math
from . import helpers
from decimal import Decimal
import json


# Todo: Bootstrap & Jquery runterladen

def home(request):
    try:
        active_project = project.objects.get(pk=request.user.app_user.active_project_id)
        # Set project title for indicator
        request.session['active_project'] = active_project.title
    except AttributeError:
        active_project = ''
    if request.user.is_authenticated:
        return render(request, 'ranking_application/home.html', {'active_project': active_project})
    else:
        return redirect('login')


def explanation(request):
    if request.user.is_authenticated:
        return render(request, 'ranking_application/explanation.html', {})
    else:
        return redirect('login')


def projects(request):
    if request.user.is_authenticated:
        if request.user.app_user.active_project_id:
            try:
                active_project = project.objects.get(pk=request.user.app_user.active_project_id)

            except ObjectDoesNotExist:
                active_project = ''
        else:
            active_project = None
        if request.user.app_user.role == 'PM':
            my_projects = project.objects.filter(project_owned_by__project_owner=request.user.app_user.pk)
            return render(request, 'ranking_application/projects.html', {'my_projects': my_projects,
                                                                         'active_project': active_project})
        elif request.user.app_user.role != 'PM':
            my_projects = project.objects.filter(project_assignees__assigned_user=request.user.app_user.pk)
            return render(request, 'ranking_application/projects.html', {'my_projects': my_projects,
                                                                         'active_project': active_project})
    else:
        return redirect('login')


def requirements(request):
    if request.user.is_authenticated:
        project_requirements = requirement.objects.filter(assigned_to_project=request.user.app_user.active_project)
        if request.user.app_user.role == 'PM':
            return render(request, 'ranking_application/requirements.html',
                          {'project_requirements': project_requirements})
        elif request.user.app_user.role != 'PM':
            return render(request, 'ranking_application/ranking.html',
                          {'project_requirements': project_requirements})
    else:
        return redirect('login')


def delete_requirement(request, requirement_id):
    if request.user.is_authenticated and request.user.app_user.role == 'PM':
        requirement.objects.get(pk=requirement_id).delete()
        return redirect('requirements')
    else:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('login')


def edit_requirement(request, requirement_id):
    requirement_editted = requirement.objects.get(pk=requirement_id)
    old_title = requirement_editted.title
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = EditRequirement(request.POST)
        # check whether it's valid:
        if form.is_valid():
            print(form.cleaned_data)
            requirement_editted.title = form.cleaned_data['requirement_title']
            requirement_editted.description = form.cleaned_data['requirement_description']
            requirement_editted.save()
            messages.success(request, 'Successfully altered requirement %s!' % (old_title,))
            return redirect('requirements')
    # if a GET (or any other method) we'll create a blank form
    else:
        form = EditRequirement(initial={'requirement_title': requirement_editted.title,
                                        'requirement_description': requirement_editted.description})
    if request.user.is_authenticated and request.user.app_user.role == 'PM':
        return render(request, 'ranking_application/requirements_edit.html', {'form': form,
                                                                              'requirement_id': requirement_id,
                                                                              'requirement_data': requirement_editted})
    else:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('login')


def users(request):
    try:
        active_project = project.objects.get(pk=request.user.app_user.active_project_id)
    except ObjectDoesNotExist:
        active_project = ''
    my_users = app_user.objects.filter(project_assignees__assigned_to_project=active_project.pk)
    if request.user.is_authenticated and request.user.app_user.role == 'PM':
        return render(request, 'ranking_application/users.html', {'my_users': my_users})
    else:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('login')


def assign_users(request):
    # if this is a POST request we need to process the form data
    user_choices = [[x.id, str(x.username)+' - '+str(x.get_role_display())] for x in app_user.objects.exclude(pk=request.user.app_user.pk).exclude(
        pk__in=app_user.objects.filter(project_assignees__assigned_to_project=request.user.app_user.active_project))]

    if request.method == 'POST':
        try:
            active_project = project.objects.get(pk=request.user.app_user.active_project_id)
        except ObjectDoesNotExist:
            active_project = ''
        # create a form instance and populate it with data from the request:
        users_to_assign = request.POST.getlist('users_to_assign')
        for elem in users_to_assign:
            new_entry = project_assignees()
            new_entry.assigned_to_project = active_project
            new_entry.save()
            new_entry.assigned_user.add(app_user.objects.get(pk=elem))
            new_entry.save()
            print(new_entry.assigned_user)
        return redirect('users')
    # if a GET (or any other method) we'll create a blank form
    else:
        form = AssignUsers(user_choices=user_choices)
    if request.user.is_authenticated and request.user.app_user.role == 'PM':
        return render(request, 'ranking_application/users_assign.html', {'form': form})
    else:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('login')


def unassign_user(request, user_id):
    if request.user.is_authenticated and request.user.app_user.role == 'PM':
        project_assignees.objects.get(assigned_to_project=request.user.app_user.active_project_id, assigned_user=user_id).delete()
        return redirect('users')
    else:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('login')


def rankings(request):
    if request.user.is_authenticated:
        if request.user.app_user.role == 'PM':
            finished_rankings = {}
            criteria = {}
            rankings_complete = True
            try:
                active_project = project.objects.get(pk=request.user.app_user.active_project_id)
            except ObjectDoesNotExist:
                active_project = ''
            assigned_users = app_user.objects.filter(project_assignees__assigned_to_project=active_project.pk)
            project_requirements = requirement.objects.filter(assigned_to_project=request.user.app_user.active_project)
            for user in assigned_users:
                #finished_rankings[user] = []
                specific_ranking = ranking.objects.filter(ranked_by=user,
                                                          project=request.user.app_user.active_project).order_by('rank')
                #finished_rankings.append(specific_ranking)
                finished_rankings[user] = specific_ranking
                if specific_ranking:
                    criteria[user] = specific_ranking[0].criterion
            for elem in finished_rankings.values():
                if len(elem) != len(project_requirements):
                    rankings_complete = False
            dataframes = []
            for elem in finished_rankings:
                dict_to_dataframe = {'requ_name': [], 'requ_id': [], 'rank': [], 'membership': [],
                                     'nonmembership': [], 'hesitation': []}
                for elem2 in finished_rankings[elem]:
                    dict_to_dataframe['requ_name'].append(elem2.ranked_requirement)
                    dict_to_dataframe['requ_id'].append(elem2.ranked_requirement.id_in_project)
                    dict_to_dataframe['rank'].append(elem2.rank)
                    dict_to_dataframe['membership'].append(0)
                    dict_to_dataframe['nonmembership'].append(0)
                    dict_to_dataframe['hesitation'].append(0)

                df = pandas.DataFrame(data=dict_to_dataframe, columns=dict_to_dataframe.keys())
                dataframes.append(df)
            for dataframe in dataframes:
                dataframe['membership'] = dataframe['rank'].apply(calculate_membership,
                                                                  args=(dataframe['rank'],
                                                                        len(project_requirements)))
                dataframe['nonmembership'] = dataframe['rank'].apply(calculate_non_membership,
                                                                      args=(dataframe['rank'],
                                                                            len(project_requirements)))
                dataframe['hesitation'] = 1 - dataframe['membership'] - dataframe['nonmembership']

            finished_rankings2 = {}
            for x in range(len(assigned_users)):
                finished_rankings2[assigned_users[x]] = dataframes[x].to_dict(orient='records')
            #finished_rankings = ranking.objects.filter(project=request.user.app_user.active_project)
            return render(request, 'ranking_application/ranking.html', {'assigned_users': assigned_users,
                                                                        'finished_rankings': finished_rankings,
                                                                        'finished_rankings2': finished_rankings2,
                                                                        'dataframes': dataframes,
                                                                        'project_requirements': project_requirements,
                                                                        'rankings_complete': rankings_complete,
                                                                        'criteria': criteria})
        else:
            project_requirements = requirement.objects.filter(assigned_to_project=request.user.app_user.active_project)
            return render(request, 'ranking_application/ranking.html', {'project_requirements': project_requirements})
    else:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('login')


def final_ranking(request):
    if request.user.is_authenticated and request.user.app_user.role == 'PM':
        finished_rankings = {}
        dataframes = []
        hesitation_values = []
        weights = []
        try:
            active_project = project.objects.get(pk=request.user.app_user.active_project_id)
        except ObjectDoesNotExist:
            active_project = ''
        assigned_users = app_user.objects.filter(project_assignees__assigned_to_project=active_project.pk)
        project_requirements = requirement.objects.filter(assigned_to_project=request.user.app_user.active_project)
        for user in assigned_users:
            specific_ranking = ranking.objects.filter(ranked_by=user,
                                                      project=request.user.app_user.active_project).order_by('rank')
            finished_rankings[user] = specific_ranking
        try:
            for ranking_by_user in finished_rankings:
                dict_to_dataframe = {'requ_name': [], 'requ_id': [], 'rank': [], 'membership': [],
                                     'non-membership': [], 'hesitation': []}
                for single_ranked_requirement in finished_rankings[ranking_by_user]:
                    dict_to_dataframe['requ_name'].append(single_ranked_requirement.ranked_requirement)
                    dict_to_dataframe['requ_id'].append(single_ranked_requirement.ranked_requirement.id_in_project)
                    dict_to_dataframe['rank'].append(single_ranked_requirement.rank)
                    dict_to_dataframe['membership'].append(0)
                    dict_to_dataframe['non-membership'].append(0)
                    dict_to_dataframe['hesitation'].append(0)
                df = pandas.DataFrame(data=dict_to_dataframe, index=[x for x in range(len(dict_to_dataframe['requ_name']))],
                                      columns=dict_to_dataframe.keys())
                dataframes.append(df)
            for dataframe in dataframes:
                dataframe['membership'] = dataframe['rank'].apply(calculate_membership,
                                                                  args=(dataframe['rank'],
                                                                        len(project_requirements)))
                dataframe['non-membership'] = dataframe['rank'].apply(calculate_non_membership,
                                                                      args=(dataframe['rank'],
                                                                            len(project_requirements)))
                dataframe['hesitation'] = 1 - dataframe['membership'] - dataframe['non-membership']
                # Calculate average hesitation values per ranking
                hesitation_values.append(Decimal(dataframe['hesitation'].sum()) / len(project_requirements))
            # Gives the weight for every ranking, in the same order as the list of dataframes
            for val in hesitation_values:
                print(Decimal(1) - Decimal(val))
                print((Decimal(len(dataframes)) - Decimal(sum(hesitation_values))))
                weights.append((1 - val) / (len(dataframes) - sum(hesitation_values)))
            print('Average hesitation values: ', hesitation_values)
            print('Calculated weights: ', weights)
            for dataframe in dataframes:
                print(dataframe)
                dataframe.sort_values('requ_id', axis=0, inplace=True)
            results_final_ranking = {}
            for x in range(len(project_requirements)):
                first_step = 0
                second_step = 0
                for y in range(len(dataframes)):
                    if first_step == 0:
                        first_step = weights[y] * dataframes[y].at[x, 'membership']
                    else:
                        first_step = first_step + weights[y] * dataframes[y].at[x, 'membership']
                    if second_step == 0:
                        second_step = weights[y] * ((dataframes[y].at[x, 'membership'] ** 2) + (dataframes[y].at[x, 'non-membership'] ** 2))
                    else:
                        second_step = second_step + weights[y] * \
                                                    ((dataframes[y].at[x, 'membership'] ** 2) + (dataframes[y].at[x, 'non-membership'] ** 2))
                third_step = math.sqrt(second_step)
                if first_step == 0.0 and third_step == 0.0:
                    result = 0.0
                else:
                    result = Decimal(first_step) / Decimal(third_step)
                results_final_ranking[project_requirements[x]] = result
            results_final_ranking = dict(helpers.sort_dict(results_final_ranking))
            print(results_final_ranking)
        except(ZeroDivisionError):
            results_final_ranking = False
        categories = []
        for key in results_final_ranking.keys():
            categories.append(key.title)
        # Transforming the category list into json for safer processing in highcharts.js
        categories = json.dumps(categories)
        help_dict = {}
        counter = 0
        for user in assigned_users:
            help_dict[user] = [weights[counter], hesitation_values[counter], sum(dataframes[counter]['hesitation'])]
            counter += 1
        scores = []
        for x in list(results_final_ranking.values()):
            scores.append(float(round(x, 9)))
        return render(request, 'ranking_application/final_ranking.html', {'results_final_ranking': results_final_ranking,
                                                                          'categories': categories,
                                                                          'scores': scores,
                                                                          'help_dict': help_dict
                                                                          })
        project_requirements = requirement.objects.filter(assigned_to_project=request.user.app_user.active_project)
        return render(request, 'ranking_application/ranking.html', {'project_requirements': project_requirements})
    else:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('login')


def rank_requirements(request):
    if request.user.is_authenticated:
        project_requirements = requirement.objects.filter(assigned_to_project=request.user.app_user.active_project)
        ranked_requirements = ranking.objects.filter(ranked_by=request.user.app_user,
                                                     project=request.user.app_user.active_project).order_by('rank')
        criteria = assigned_criteria.objects.filter(assigned_to_project=request.user.app_user.active_project)
        select_list = ['N']
        select_list.extend(list(range(1, len(project_requirements)+1)))
        if ranked_requirements:
            used_criterion = ranked_requirements[0].criterion
        else:
            used_criterion = None
        print(used_criterion)
        if request.method == 'POST':
            ranks = {}
            checklist = []
            for requ in project_requirements:
                ranks[requ.pk] = request.POST.get(str(requ.pk))
                print(ranks)
            criterion = request.POST.get('criteria')
            for elem in ranks.values():
                if elem == 'N':
                    checklist.append(elem)
                else:
                    checklist.append(int(elem))
            # for elem in ranked_requirements:
            #     if elem.rank == 'N':
            #         pass
            #     else:
            #         checklist.append(int(elem.rank))
            checklist = list(set(checklist))
            if 'N' in checklist:
                checklist.remove('N')
            # If there are only unknowns, checklist is None
            print(checklist)
            if not checklist:
                valid = True
            else:
                maximum = max(checklist)
                if sum(checklist) == maximum * (maximum + 1) / 2:
                    valid = True
                else:
                    valid = False
            if valid:
                try:
                    active_project = project.objects.get(pk=request.user.app_user.active_project_id)
                except ObjectDoesNotExist:
                    active_project = ''
                # Iterate over the dict with the rankings, key=Primary key of ranked requirement, value=specified rank
                for elem in ranks:
                    requ = requirement.objects.get(pk=elem)
                    existing_ranking = ranking.objects.filter(ranked_requirement=elem, ranked_by=request.user.app_user)
                    # Check, if a ranking already exists
                    if not existing_ranking:
                        new_ranking = ranking()
                        new_ranking.ranked_requirement = requ
                        new_ranking.ranked_by = request.user.app_user
                        new_ranking.rank = ranks[elem]
                        new_ranking.project = active_project
                        new_ranking.criterion = criterion
                        new_ranking.save()
                        print(existing_ranking)
                    else:
                        existing_ranking = existing_ranking.first()
                        existing_ranking.rank = ranks[elem]
                        existing_ranking.last_updated = timezone.now()
                        existing_ranking.criterion = criterion
                        existing_ranking.save()
                        print(existing_ranking)
                messages.success(request, 'Ranking succesfully saved!')
                return redirect('rank_requirements')
            else:
                messages.error(request, 'Please specify consecutive ranks!')
                return redirect('rank_requirements')
        return render(request, 'ranking_application/rank_requirements.html',
                      {'project_requirements': project_requirements,
                       'select_list': select_list,
                       'ranked_requirements': ranked_requirements,
                       'criteria': criteria,
                       'criterion': used_criterion})
    else:
        return redirect('login')


def create_new_project(request):
    # if this is a POST request we need to process the form data
    choices = [('Importance', 'Importance'), ('Cost', 'Cost'), ('Damage', 'Damage'), ('Duration', 'Duration'),
               ('Risk', 'Risk'), ('Volatility', 'Volatility')]
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = NewProject(request.POST, criteria_choices=choices)
        # check whether it's valid:
        if form.is_valid():
            new_project = project()
            new_project.title = form.cleaned_data['project_title']
            new_project.description = form.cleaned_data['project_description']
            new_project.created_by = request.user.app_user
            new_project.save()

            new_project_owner = project_owned_by.objects.create(project=new_project)
            new_project_owner.project_owner.add(request.user.app_user)
            new_project_owner.save()

            for elem in form.cleaned_data['criteria']:
                new_assigned_criterion = assigned_criteria()
                new_assigned_criterion.assigned_to_project = new_project
                new_assigned_criterion.criterion = elem
                new_assigned_criterion.save()
            messages.success(request, 'Successfully created new project!')
            return redirect('projects')
    # if a GET (or any other method) we'll create a blank form
    else:
        form = NewProject(criteria_choices=choices)
    if request.user.is_authenticated and request.user.app_user.role == 'PM':
        return render(request, 'ranking_application/projects_create.html', {'form': form})
    else:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('login')


def create_new_requirement(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = NewRequirement(request.POST)
        # check whether it's valid:
        if form.is_valid():
            print(form.cleaned_data)
            try:
                active_project = project.objects.get(pk=request.user.app_user.active_project_id)
            except ObjectDoesNotExist:
                active_project = ''
            last_id = requirement.objects.filter(assigned_to_project=active_project).aggregate(Max('id_in_project'))
            print(last_id)
            new_requirement = requirement()

            new_requirement.title = form.cleaned_data['requirement_title']
            new_requirement.description = form.cleaned_data['requirement_description']
            new_requirement.assigned_to_project = active_project
            new_requirement.created_by = request.user.app_user
            if last_id['id_in_project__max'] is None:
                new_requirement.id_in_project = 1
            else:
                new_requirement.id_in_project = last_id['id_in_project__max'] + 1
            new_requirement.save()

            messages.success(request, 'Successfully created new requirement!')
            return redirect('requirements')
    # if a GET (or any other method) we'll create a blank form
    else:
        form = NewRequirement()
    if request.user.is_authenticated and request.user.app_user.role == 'PM':
        return render(request, 'ranking_application/requirements_create.html', {'form': form})
    else:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('login')


def change_active_project(request, project_id):
    app_user.objects.filter(pk=request.user.app_user.pk).update(active_project=project_id)
    # Change active project
    request.session['active_project'] = project.objects.get(pk=project_id).title
    if request.user.is_authenticated:
        return redirect('projects')
    else:
        return redirect('login')


def delete_project(request, project_id):
    print(project_id)
    print(type(project_id))
    project.objects.get(pk=project_id).delete()
    if request.user.is_authenticated and request.user.app_user.role == 'PM':
        return redirect('projects')
    else:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('login')


def edit_project(request, project_id):
    project_editted = project.objects.get(pk=project_id)
    old_title = project_editted.title
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = EditProject(request.POST)
        # check whether it's valid:
        if form.is_valid():
            print(form.cleaned_data)
            project_editted.title = form.cleaned_data['project_title']
            project_editted.description = form.cleaned_data['project_description']
            # project_editted.objects.update(title=form.cleaned_data['project_title'], description=form.cleaned_data['project_description'])
            project_editted.save()
            messages.success(request, 'Successfully altered project %s!' % (old_title,))
            return redirect('projects')
    # if a GET (or any other method) we'll create a blank form
    else:
        form = EditProject(
            initial={'project_title': project_editted.title, 'project_description': project_editted.description})
    if request.user.is_authenticated and request.user.app_user.role == 'PM':
        return render(request, 'ranking_application/projects_edit.html', {'form': form,
                                                                          'project_id': project_id,
                                                                          'project_data': project_editted})
    else:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('login')

        # def login(request):
        #     return render(request, 'ranking_application/login.html', {})
        #
        # def dashboard(request):
        #     pass


def calculate_membership(x, column, number_requirements):
    if x == 'N':
        return 0
    else:
        counter = 0
        for elem in column:
            if elem == 'N':
                continue
            if elem > x:
                counter += 1
        return Decimal(counter) / Decimal((number_requirements - 1))


def calculate_non_membership(x, column, number_requirements):
    if x == 'N':
        return 0
    else:
        counter = 0
        for elem in column:
            if elem == 'N':
                continue
            if elem < x:
                counter += 1
        return Decimal(counter) / Decimal((number_requirements - 1))


def calculate_hesitation(x, non_membership):
    if x == 'N':
        return 1
    else:
        return 1 - (x + non_membership)
