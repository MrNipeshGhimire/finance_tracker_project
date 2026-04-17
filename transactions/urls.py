from django.urls import path
from . import views

app_name = 'transactions'

urlpatterns = [
    path('', views.transaction_list, name='list'),
    path('add/', views.transaction_create, name='create'),
    path('<int:pk>/edit/', views.transaction_update, name='update'),
    path('<int:pk>/delete/', views.transaction_delete, name='delete'),
    path('category/create/', views.category_create_ajax, name='category_create_ajax'),
    path('<int:pk>/', views.transaction_detail, name='detail'),
    path('dashboard/', views.dashboard, name='dashboard'),
]