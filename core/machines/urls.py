from django.urls import path
from . import views

urlpatterns = [
    path('', views.machines_page, name='machines'),
    path('add_machine/', views.add_machine, name='add_machine'),
    path('mapping/', views.machine_mapping, name='mapping'),
    path('mapping_list/', views.machine_mapping_list, name='mapping_list'),
    path('machines_list/', views.machines_list, name='machines_list'),
    path('edit_machine/<int:id>/', views.edit_machine, name='edit_machine'),
    path('delete_machine/<int:id>/', views.delete_machine, name='delete_machine'),
    path('purchase_machine/', views.purchase_machine, name='purchase_machine'),
    path('purchase_machine_history/', views.purchase_machine_history, name='purchase_machine_history')
]
