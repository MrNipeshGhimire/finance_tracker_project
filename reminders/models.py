from django.db import models
from django.contrib.auth.models import User
from loans.models import Loan
from budgets.models import Budget

class Reminder(models.Model):
    REMINDER_TYPE = [
    ('loan_due', 'Loan Due Date'),
    ('loan_custom', 'Custom Loan Reminder'),
    ('budget', 'Budget Alert'),
    ]

    FREQUENCY = [
        ('once', 'Once'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly')
    ]

    user          = models.ForeignKey(User, on_delete=models.CASCADE)
    loan          = models.ForeignKey(Loan, on_delete=models.CASCADE, null=True, blank=True)
    budget        = models.ForeignKey(Budget, on_delete=models.CASCADE, null=True, blank=True)
    reminder_type = models.CharField(max_length=15, choices=REMINDER_TYPE)
    message       = models.TextField()
    remind_on     = models.DateTimeField()
    frequency     = models.CharField(max_length=10, choices=FREQUENCY, default='once')
    is_sent       = models.BooleanField(default=False)
    created_at    = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reminder: {self.reminder_type} on {self.remind_on}"