from django.conf.urls import url
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': 'login'}, name='logout'),
    url(r'^home/$', views.home, name='home'),
    url(r'^$', views.home, name='home'),
    url(r'^projects/$', views.projects, name='projects'),
    url(r'^requirements/$', views.requirements, name='requirements'),
    url(r'^requirements/new_requirement/$', views.create_new_requirement, name='requirements_create'),
    url(r'^requirements/delete/(?P<requirement_id>[0-9]*)$', views.delete_requirement, name='delete_requirement'),
    url(r'^requirements/edit/(?P<requirement_id>[0-9]*)$', views.edit_requirement, name='edit_requirement'),
    url(r'^users/$', views.users, name='users'),
    url(r'^users/assign/$', views.assign_users, name='users_assign'),
    url(r'^users/unassign/(?P<user_id>[0-9]*)$', views.unassign_user, name='unassign_user'),
    url(r'^ranking/$', views.rankings, name='ranking'),
    url(r'^ranking/final_ranking$', views.final_ranking, name='final_ranking'),
    url(r'^ranking/rank_requirements$', views.rank_requirements, name='rank_requirements'),
    url(r'^projects/new_project/$', views.create_new_project, name='projects_create'),
    url(r'^projects/change/(?P<project_id>[0-9]*)$', views.change_active_project, name='change_active_project'),
    url(r'^projects/delete/(?P<project_id>[0-9]*)$', views.delete_project, name='delete_project'),
    url(r'^projects/edit/(?P<project_id>[0-9]*)$', views.edit_project, name='edit_project'),
    url(r'^explanation/$', views.explanation, name='explanation'),



    # url(r'^$', views.login, name='login'),
    # url(r'^home$', views.dashboard, name='dashboard'),
]