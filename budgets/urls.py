from django.urls import path
from . import views

app_name = 'budgets'

urlpatterns = [
    path('', views.budget_list, name='list'),
    path('add/', views.budget_create, name='add'),
    path('<int:pk>/edit/', views.budget_update, name='edit'),
]