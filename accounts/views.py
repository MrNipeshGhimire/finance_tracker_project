from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required

from .forms import UserRegisterForm, UserProfileForm


def register_view(request):
    form = UserRegisterForm(request.POST or None)

    if form.is_valid():
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.save()

        login(request, user)
        return redirect('dashboard')

    return render(request, 'accounts/register.html', {'form': form})


from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password")

    return render(request, 'accounts/login.html')


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def profile_view(request):
    profile = request.user.userprofile
    form = UserProfileForm(request.POST or None, instance=profile)

    if form.is_valid():
        form.save()
        return redirect('profile')

    return render(request, 'accounts/profile.html', {'form': form})