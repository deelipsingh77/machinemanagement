from django.urls import path
from . import views
from core.api.views import get_machines_by_location, get_parts_by_location, get_parts_for_machine

urlpatterns = [
    path('', views.homepage, name='home'),
    path('ticket/', views.ticket, name='ticket'),
    
    path('get_parts_for_machine/<int:machine_id>/', get_parts_for_machine, name='get_parts_for_machine'),
    path('get_parts_by_location/<int:location_id>/', get_parts_by_location, name='get_parts_by_location'),
    path('get_machines_by_location/<int:location_id>/', get_machines_by_location, name='get_machines_by_location')
]