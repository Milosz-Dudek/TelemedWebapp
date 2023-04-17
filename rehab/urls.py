from django.urls import path
from . import views

app_name = 'telemedWebapp'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('register_rehabilitator/', views.register_rehabilitator, name='register_rehabilitator'),
    path('register_patient/', views.register_patient, name='register_patient'),
    path('rehabilitators/', views.view_all_rehabilitators, name='view_all_rehabilitators'),
    path('patients/', views.view_particular_patients, name='view_particular_patients'),
    path('login/', views.login_user, name='login_user'),
    path('logout/', views.logout_user, name='logout_user'),
    path('my_account/', views.my_account_view, name='my_account'),
    path('my_account/edit/', views.edit, name='edit'),
    path('add_exercise/', views.add_exercise, name='add_exercise'),
    path('view_exercises/', views.view_exercises, name='view_exercises'),
    path('exercise_plot/', views.exercise_plot, name='exercise_plot')
]
