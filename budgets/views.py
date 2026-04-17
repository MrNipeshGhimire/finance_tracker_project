from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import Budget
from .forms import BudgetForm


@login_required
def budget_list(request):
    budgets = Budget.objects.filter(user=request.user)
    return render(request, 'budgets/list.html', {'budgets': budgets})


@login_required
def budget_create(request):
    form = BudgetForm(request.POST or None)

    if form.is_valid():
        obj = form.save(commit=False)
        obj.user = request.user
        obj.save()
        return redirect('budgets:list')

    return render(request, 'budgets/form.html', {'form': form})


@login_required
def budget_update(request, pk):
    budget = get_object_or_404(Budget, pk=pk, user=request.user)
    form = BudgetForm(request.POST or None, instance=budget)

    if form.is_valid():
        form.save()
        return redirect('budgets:list')

    return render(request, 'budgets/form.html', {'form': form})