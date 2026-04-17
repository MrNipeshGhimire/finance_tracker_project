from django import forms
from .models import Reminder

class ReminderForm(forms.ModelForm):
    class Meta:
        model = Reminder
        fields = [
        'loan',
        'budget',
        'reminder_type',
        'message',
        'remind_on',
        'frequency'
        ]
        widgets = {
        'remind_on': forms.DateTimeInput(attrs={'type': 'datetime-local'})
        }

        def clean(self):
            cleaned_data = super().clean()
            loan = cleaned_data.get('loan')
            budget = cleaned_data.get('budget')

            if not loan and not budget:
                raise forms.ValidationError("Select either a loan or a budget")