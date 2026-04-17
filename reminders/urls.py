from django.urls import path
from . import views

app_name = 'reminders'

urlpatterns = [
    path('', views.reminder_list, name='list'),
    path('add/', views.reminder_create, name='add'),
]