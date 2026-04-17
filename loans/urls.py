from django.urls import path
from . import views

app_name = 'loans'

urlpatterns = [
    path('', views.loan_list, name='list'),
    path('create/', views.loan_create, name='create'), 
    path('<int:pk>/', views.loan_detail, name='detail'),
    path('edit/<int:pk>/', views.loan_update, name='edit'),
    path('delete/<int:pk>/', views.loan_delete, name='delete'),
    path('<int:pk>/repayment/', views.add_repayment, name='add_repayment'),
]