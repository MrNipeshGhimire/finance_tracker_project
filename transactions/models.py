from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    CATEGORY_TYPE = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=10, choices=CATEGORY_TYPE)

    icon = models.CharField(max_length=50, blank=True, null=True)  # 🔥 NEW

    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'name', 'type']

    def __str__(self):
        return f"{self.name} ({self.type})"
    
    

class Transaction(models.Model):
    TRANSACTION_TYPE = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)

    type = models.CharField(max_length=10, choices=TRANSACTION_TYPE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    date = models.DateField()
    description = models.TextField(blank=True)

    is_shared = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # 🔥 NEW

    def __str__(self):
        return f"{self.user.username} - {self.type} - {self.amount}"