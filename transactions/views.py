from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import TransactionForm
from .models import Transaction
from django.shortcuts import get_object_or_404



@login_required
def transaction_create(request):
    today = timezone.now().date()
    form = TransactionForm(request.POST or None, user=request.user)

    if request.method == "POST":
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()

            messages.success(request, "Transaction added successfully ✅")
            return redirect('transactions:list')
        else:
            messages.error(request, "Please fix the errors ❌")

    return render(request, 'transactions/form.html', {'form': form})





@login_required
def transaction_update(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)

    form = TransactionForm(request.POST or None, instance=transaction, user=request.user)

    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "Transaction updated ✏️")
            return redirect('transactions:list')
        else:
            messages.error(request, "Update failed ❌")

    return render(request, 'transactions/form.html', {'form': form})


@login_required
def transaction_delete(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)

    if request.method == "POST":
        transaction.delete()
        messages.success(request, "Transaction deleted 🗑️")
        return redirect('transactions:list')

    return redirect('transactions:list')


from django.db.models import Sum, Q
from django.utils import timezone
from datetime import timedelta


@login_required
def transaction_list(request):
    search_query = request.GET.get('search', '')
    filter_type = request.GET.get('filter', 'monthly')

    transactions = Transaction.objects.filter(user=request.user)

    # 🔍 Search
    if search_query:
        transactions = transactions.filter(
            Q(description__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )

    # 📅 Date Filter
    today = timezone.now().date()

    if filter_type == 'daily':
        transactions = transactions.filter(date=today)

    elif filter_type == 'weekly':
        start_week = today - timedelta(days=7)
        transactions = transactions.filter(date__gte=start_week)

    elif filter_type == 'monthly':
        transactions = transactions.filter(
            date__year=today.year,
            date__month=today.month
        )

    # 💰 Calculations
    total_income = transactions.filter(type='income').aggregate(
        Sum('amount')
    )['amount__sum'] or 0

    total_expense = transactions.filter(type='expense').aggregate(
        Sum('amount')
    )['amount__sum'] or 0

    balance = total_income - total_expense

    # 📄 Order
    transactions = transactions.order_by('-date', '-created_at')

    context = {
        'transactions': transactions,
        'search_query': search_query,
        'filter_type': filter_type,
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': balance,
    }

    return render(request, 'transactions/list.html', context)


@login_required
def transaction_detail(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)

    form = TransactionForm(instance=transaction, user=request.user)

    return render(request, 'transactions/detail.html', {
        'transaction': transaction,
        'form': form
    })
    
    

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Category


@require_POST
def category_create_ajax(request):
    name = request.POST.get('name')
    type_ = request.POST.get('type')

    if not name or not type_:
        return JsonResponse({'error': 'Missing data'}, status=400)

    category = Category.objects.create(
        user=request.user,
        name=name,
        type=type_,
        icon='📁',  # default icon
        is_default=False
    )

    return JsonResponse({
        'id': category.id,
        'name': category.name,
        'type': category.type,
        'icon': category.icon
    })
    


from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone
import json


@login_required
def dashboard(request):
    user = request.user
    today = timezone.now().date()

    # 📅 Monthly transactions
    transactions = Transaction.objects.filter(
        user=user,
        date__year=today.year
    )

    # 💰 totals
    total_income = transactions.filter(type='income').aggregate(
        Sum('amount')
    )['amount__sum'] or 0

    total_expense = transactions.filter(type='expense').aggregate(
        Sum('amount')
    )['amount__sum'] or 0

    balance = total_income - total_expense

    # 📊 monthly chart
    monthly_data = transactions.annotate(
        month=TruncMonth('date')
    ).values('month', 'type').annotate(
        total=Sum('amount')
    ).order_by('month')

    months = []
    income_data = []
    expense_data = []

    month_map = {}

    for item in monthly_data:
        m = item['month'].strftime("%b")

        if m not in month_map:
            month_map[m] = {'income': 0, 'expense': 0}

        month_map[m][item['type']] = float(item['total'])

    for m, val in month_map.items():
        months.append(m)
        income_data.append(val['income'])
        expense_data.append(val['expense'])

    # 🍩 category expense
    category_data = transactions.filter(type='expense').values(
        'category__name'
    ).annotate(total=Sum('amount'))

    categories = [c['category__name'] for c in category_data]
    category_totals = [float(c['total']) for c in category_data]
    
    recent_transactions = Transaction.objects.filter(
    user=request.user
        ).order_by('-date')[:5]

    context = {
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': balance,
        'months': json.dumps(months),
        'income_data': json.dumps(income_data),
        'expense_data': json.dumps(expense_data),
        'categories': json.dumps(categories),
        'category_totals': json.dumps(category_totals),
        'recent_transactions': recent_transactions,
    }

    return render(request, 'dashboard/dashboard.html', context)