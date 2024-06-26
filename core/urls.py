from django.urls import include, path
from . import views

urlpatterns = [
    path('dashboard/', include('core.dashboard.urls')),
    path('machines/', include('core.machines.urls')), 
    path('parts/', include('core.parts.urls')),
    path('tickets/', include('core.tickets.urls')),
    path('reports/', include('core.reports.urls')),

    path('add_location/', views.add_location, name='add_location'),
    path('remove_location/<int:id>/', views.remove_location, name='remove_location'),
    
    path('add_department/', views.add_department, name='add_department'),
    path('remove_department/<int:id>/', views.remove_department, name='remove_department')
]
