from django import forms

from .models import project, app_user

# class newProject(forms.ModelForm):
#
#     class Meta:
#         model = project
#         fields = ('title', 'description')


class NewProject(forms.Form):
    project_title = forms.CharField(label='Project title', max_length=100)
    project_description = forms.CharField(widget=forms.Textarea, max_length=200)
    criteria = forms.MultipleChoiceField(label='Relevant criteria')
    def __init__(self, *args, **kwargs):
        criteria_choices = kwargs.pop('criteria_choices')
        super(NewProject, self).__init__(*args, **kwargs)
        self.fields['criteria'].choices = criteria_choices


class EditProject(forms.Form):
    project_title = forms.CharField(label='Project title', max_length=100)
    project_description = forms.CharField(widget=forms.Textarea, max_length=200)


class NewRequirement(forms.Form):
    requirement_title = forms.CharField(label='Requirement title', max_length=100)
    requirement_description = forms.CharField(widget=forms.Textarea, max_length=200)


class EditRequirement(forms.Form):
    requirement_title = forms.CharField(label='Requirement title', max_length=100)
    requirement_description = forms.CharField(widget=forms.Textarea, max_length=200)


class AssignUsers(forms.Form):
    users_to_assign = forms.MultipleChoiceField(label='Users to assign')
    def __init__(self, *args, **kwargs):
        user_choices = kwargs.pop('user_choices')
        super(AssignUsers, self).__init__(*args, **kwargs)
        self.fields['users_to_assign'].choices = user_choices

