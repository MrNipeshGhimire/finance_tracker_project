from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from transactions.models import Transaction, Category

class Budget(models.Model):
    PERIOD_CHOICES = [('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly')]

    user       = models.ForeignKey(User, on_delete=models.CASCADE)
    category   = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    period     = models.CharField(max_length=10, choices=PERIOD_CHOICES)
    limit      = models.DecimalField(max_digits=12, decimal_places=2)
    is_active  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'category', 'period']

    @property
    def current_spent(self):
        today = timezone.now().date()

        if self.period == 'daily':
            start = today
        elif self.period == 'weekly':
            start = today - timezone.timedelta(days=today.weekday())
        else:
            start = today.replace(day=1)

        qs = Transaction.objects.filter(
            user=self.user,
            type='expense',
            date__gte=start
        )

        if self.category:
            qs = qs.filter(category=self.category)

        return qs.aggregate(total=models.Sum('amount'))['total'] or Decimal('0')

    @property
    def remaining(self):
        return self.limit - self.current_spent

    @property
    def is_exceeded(self):
        return self.current_spent > self.limit

    def __str__(self):
        return f"{self.period} budget: {self.limit}"