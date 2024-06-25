from django.urls import path
from . import views

urlpatterns = [
    path("", views.reports, name="reports"),
    path("machines/", views.machines_report, name="machines_report"),
    path("parts/", views.parts_report, name="parts_report"),
    path("purchases/", views.purchases_report, name="purchases_report"),
]
