from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),

    path('machines/', views.machines_page, name='machines'),
    path('machines/add_machine/', views.add_machine, name='add_machine'),
    path('machines/machines_list/', views.machines_list, name='machines_list'),
    path('machines/edit_machine/<int:id>/', views.edit_machine, name='edit_machine'),
    path('machines/delete_machine/<int:id>/', views.delete_machine, name='delete_machine'),
    
    path('parts/', views.parts_page, name='parts'),
    path('parts/add_part/', views.add_part, name='add_part'),
    path('parts/parts_list/', views.parts_list, name='parts_list'),
    path('parts/delete_part/<int:id>/', views.delete_part, name='delete_part'),
    path('parts/edit_part/<int:id>/', views.edit_part, name='edit_part'),
    
    path('maintenance/', views.maintenance_page, name='maintenance'),
    path('maintenance/add_maintenance/', views.add_maintenance, name='add_maintenance'),
    path('maintenance/maintenance_list/', views.maintenance_list, name='maintenance_list'),
    path('maintenance/delete_maintenance/<int:id>/', views.delete_maintenance, name='delete_maintenance'),
    path('maintenance/edit_maintenance/<int:id>/', views.edit_maintenance, name='edit_maintenance'),
]
