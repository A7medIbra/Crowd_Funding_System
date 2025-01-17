from django.urls import path
from . import views

urlpatterns = [
    path('index/', views.index, name='admin_dashboard'),
    path('users/', views.show_users, name='show_users'),
    path('users/<int:id>/delete/', views.delete_user, name='delete_user'),
    path('projects/', views.show_projects, name='show_projects'),
    path('projects/<slug:slug>/', views.show_project, name='show_project'),
    path('projects/<slug:slug>/update/', views.edit_project, name='edit_project'),
    path('projects/<slug:slug>/featured/', views.featured_project, name='featured_project'),
    path('projects/<slug:slug>/delete/', views.delete_project, name='delete_project'),
    path('projects/<slug:slug>/comments/<int:id>/delete/', views.delete_comment, name='delete_comment'),
    path('projects/<slug:slug>/project_pictures/', views.project_picture, name='project_picture'),
    path('projects/<slug:slug>/delete_picture/<int:pk>/', views.delete_project_picture, name='delete_project_picture'),
    path('categories/', views.show_categories, name='show_categories'),
    path('categories/create/', views.create_category, name='create_category'),
    path('categories/<slug:slug>/', views.show_category, name='show_category'),
    path('categories/<slug:slug>/update/', views.update_category, name='update_category'),
    path('categories/<slug:slug>/delete/', views.delete_category, name='delete_category'),
    path('donations/', views.show_donations, name='show_donations'),
    path('reports/', views.show_reports, name='show_reports'),
    path('projects_reports/<int:id>/', views.show_project_report, name='show_project_report'),
    path('projects_reports/<int:id>/delete/', views.delete_project_report, name='delete_project_report'),
    path('comments_reports/<int:id>/', views.show_comment_report, name='show_comment_report'),
    path('comments_reports/<int:id>/delete/', views.delete_comment_report, name='delete_comment_report'),
]
