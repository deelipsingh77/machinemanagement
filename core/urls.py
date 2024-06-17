from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),

    path('machines/', views.machines_page, name='machines'),
    path('machines/add_machine/', views.add_machine, name='add_machine'),
    path('machines_list/', views.machines_list, name='machines_list'),
    # path('edit_machine/<int:id>/', views.edit_machine, name='edit_machine'),
    # path('delete_machine/<int:id>/', views.delete_machine, name='delete_machine'),
    
    path('parts/', views.parts_page, name='parts'),
    path('add_part/', views.add_part, name='add_part'),
    path('parts_list/', views.parts_list, name='parts_list'),
    # path('delete_part/<int:id>/', views.delete_part, name='delete_part'),
    # path('edit_part/<int:id>/', views.edit_part, name='edit_part'),
]
