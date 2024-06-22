from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),

    path('machines/', views.machines_page, name='machines'),
    path('machines/add_machine/', views.add_machine, name='add_machine'),
    path('machines/mapping/', views.machine_mapping, name='mapping'),
    path('machines/mapping_list/', views.machine_mapping_list, name='mapping_list'),
    path('machines/machines_list/', views.machines_list, name='machines_list'),
    path('machines/edit_machine/<int:id>/', views.edit_machine, name='edit_machine'),
    path('machines/delete_machine/<int:id>/', views.delete_machine, name='delete_machine'),
    
    path('parts/', views.parts_page, name='parts'),
    path('parts/add_part/', views.add_part, name='add_part'),
    path('parts/parts_list/', views.parts_list, name='parts_list'),
    path('parts/delete_part/<int:id>/', views.delete_part, name='delete_part'),
    path('parts/edit_part/<int:id>/', views.edit_part, name='edit_part'),

    path('tickets/', views.tickets_page, name="tickets_page"),
    path('tickets/tickets_list/', views.tickets_list, name='tickets_list'),
    path('tickets/resolve_tickets/', views.resolve_tickets, name='resolve_tickets'),
    path('tickets/resolve_ticket/<int:id>/', views.resolve_ticket, name='resolve_ticket'),

    path('add_location/', views.add_location, name='add_location'),
    path('add_issue/', views.add_issue, name='add_issue'),
]
