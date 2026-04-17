from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .models import Reminder
from .forms import ReminderForm


@login_required
def reminder_list(request):
    reminders = Reminder.objects.filter(user=request.user)
    return render(request, 'reminders/list.html', {'reminders': reminders})


@login_required
def reminder_create(request):
    form = ReminderForm(request.POST or None)

    if form.is_valid():
        obj = form.save(commit=False)
        obj.user = request.user
        obj.save()
        return redirect('reminders:list')

    return render(request, 'reminders/form.html', {'form': form})