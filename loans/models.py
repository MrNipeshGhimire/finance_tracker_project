from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal, ROUND_HALF_UP
import math


class Loan(models.Model):
    LOAN_TYPE = [
        ('lend', 'I Lent'),
        ('borrow', 'I Borrowed')
    ]

    STATUS = [
        ('active', 'Active'),
        ('partial', 'Partially Paid'),
        ('settled', 'Settled')
    ]

    INTEREST_TYPE = [
        ('simple', 'Simple'),
        ('compound', 'Compound')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    loan_type = models.CharField(max_length=10, choices=LOAN_TYPE)
    person_name = models.CharField(max_length=150)
    person_contact = models.CharField(max_length=20, blank=True)

    principal_amount = models.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )
    interest_type = models.CharField(
        max_length=10,
        choices=INTEREST_TYPE,
        default='simple'
    )

    start_date = models.DateField()
    due_date = models.DateField(null=True, blank=True)

    status = models.CharField(
        max_length=10,
        choices=STATUS,
        default='active'
    )

    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # 🔥 DAILY INTEREST
    @property
    def daily_interest(self):
        if self.interest_rate == 0:
            return Decimal('0')

        p = self.principal_amount
        r = self.interest_rate / Decimal(100)

        daily = (p * r) / Decimal(365)
        return daily.quantize(
            Decimal('0.01'),
            rounding=ROUND_HALF_UP
        )

    # 🔥 TOTAL INTEREST (LIVE)
    @property
    def total_interest(self):
        days = (timezone.now().date() - self.start_date).days

        if days <= 0 or self.interest_rate == 0:
            return Decimal('0')

        p = self.principal_amount
        r = self.interest_rate / Decimal(100)
        years = Decimal(days) / Decimal(365)

        if self.interest_type == 'simple':
            interest = p * r * years
        else:
            # safer compound calculation
            interest = p * (Decimal((1 + r) ** years) - 1)

        return interest.quantize(
            Decimal('0.01'),
            rounding=ROUND_HALF_UP
        )

    # 💰 TOTAL PAYABLE
    @property
    def payable_amount(self):
        return (
            self.principal_amount + self.total_interest
        ).quantize(
            Decimal('0.01'),
            rounding=ROUND_HALF_UP
        )

    # 💵 TOTAL REPAID
    @property
    def total_repaid(self):
        return self.repayments.aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0')

    # 🔻 REMAINING AMOUNT
    @property
    def remaining_amount(self):
        remaining = self.payable_amount - self.total_repaid
        return remaining.quantize(
            Decimal('0.01'),
            rounding=ROUND_HALF_UP
        )
    
    @property
    def is_overdue(self):
        """Check if loan is overdue"""
        if not self.due_date:
            return False

        today = timezone.now().date()

        return today > self.due_date and self.remaining_amount > 0
    
    @property
    def progress_percentage(self):
        if self.payable_amount == 0:
            return 0

        percent = (self.total_repaid / self.payable_amount) * 100
        return min(round(percent, 2), 100)
    

    # 🧠 AUTO STATUS
    @property
    def computed_status(self):
        if self.remaining_amount <= 0:
            return 'settled'
        elif self.total_repaid > 0:
            return 'partial'
        return 'active'

    def __str__(self):
        return f"{self.loan_type} - {self.person_name} - {self.principal_amount}"


class LoanRepayment(models.Model):
    loan = models.ForeignKey(
        Loan,
        on_delete=models.CASCADE,
        related_name='repayments'
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    paid_date = models.DateField(default=timezone.now)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Repayment {self.amount} for {self.loan}"