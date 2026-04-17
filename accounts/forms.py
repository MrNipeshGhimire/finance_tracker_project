from django import forms
from django.contrib.auth.models import User
from .models import UserProfile


class UserRegisterForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput,
        error_messages={'required': 'Password is required'}
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput,
        error_messages={'required': 'Please confirm your password'}
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already registered")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm = cleaned_data.get('confirm_password')

        if password and confirm and password != confirm:
            raise forms.ValidationError("Passwords do not match")

        return cleaned_data


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['currency', 'timezone', 'email_alerts']