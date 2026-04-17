from django import forms
from .models import Loan, LoanRepayment

class LoanForm(forms.ModelForm):
    class Meta:
        model = Loan
        fields = [
        'loan_type',
        'person_name',
        'person_contact',
        'principal_amount',
        'interest_rate',
        'interest_type',
        'start_date',
        'due_date',
        'notes'
        ]
        widgets = {
        'start_date': forms.DateInput(attrs={'type': 'date'}),
        'due_date': forms.DateInput(attrs={'type': 'date'}),
        }

class LoanRepaymentForm(forms.ModelForm):
    class Meta:
        model = LoanRepayment
        fields = ['amount', 'paid_date', 'notes']
        widgets = {
        'paid_date': forms.DateInput(attrs={'type': 'date'})
        }
