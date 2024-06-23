from django.urls import path
from . import views

urlpatterns = [
    path('', views.tickets_page, name="tickets_page"),
    path('tickets_list/', views.tickets_list, name='tickets_list'),
    path('resolve_tickets/', views.resolve_tickets, name='resolve_tickets'),
    path('resolve_ticket/<int:id>/', views.resolve_ticket, name='resolve_ticket'),
]
