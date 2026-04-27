from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('project/create/', views.create_project, name='create_project'),
    path('projects/', views.project_list, name='project_list'),
    path('project/<int:project_id>/', views.project_detail, name='project_detail'),
    path('project/<int:project_id>/bid/', views.submit_bid, name='submit_bid'),
    path('project/<int:project_id>/bids/', views.view_bids, name='view_bids'),
    path('project/<int:project_id>/select-winner/', views.select_winner, name='select_winner'),
    path('project/<int:project_id>/submit-work/', views.submit_work, name='submit_work'),
    path('my-bids/', views.my_bids, name='my_bids'),
]