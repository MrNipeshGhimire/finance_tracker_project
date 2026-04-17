from django.contrib import admin
from django.urls import path, include
from transactions.views import transaction_list,dashboard

urlpatterns = [
    path('admin/', admin.site.urls),

    # Home / Dashboard
    path('', dashboard, name='dashboard'),

    # Apps
    path('accounts/', include('accounts.urls')),
    path('transactions/', include('transactions.urls')),
    path('loans/', include('loans.urls')),
    path('budgets/', include('budgets.urls')),
    path('reminders/', include('reminders.urls')),
]