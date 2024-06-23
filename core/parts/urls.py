from django.urls import path
from . import views

urlpatterns = [
    path('', views.parts_page, name='parts'),
    path('add_part/', views.add_part, name='add_part'),
    path('parts_list/', views.parts_list, name='parts_list'),
    path('delete_part/<int:id>/', views.delete_part, name='delete_part'),
    path('edit_part/<int:id>/', views.edit_part, name='edit_part'),
]
