from django import forms
from .models import Transaction, Category


class TransactionForm(forms.ModelForm):

    class Meta:
        model = Transaction
        fields = ['type', 'amount', 'category', 'date', 'description', 'is_shared']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # ✅ Filter categories by user
        if user:
            self.fields['category'].queryset = Category.objects.filter(user=user)

    def clean(self):
        cleaned_data = super().clean()
        type_ = cleaned_data.get('type')
        category = cleaned_data.get('category')

        # 🔴 Validate category type
        if type_ and category:
            if category.type != type_:
                raise forms.ValidationError(
                    "Category type must match transaction type."
                )

        return cleaned_data