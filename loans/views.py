from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import Loan, LoanRepayment
from .forms import LoanForm, LoanRepaymentForm


from django.shortcuts import render
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import Loan


from django.shortcuts import render
from django.db.models import Q
from django.utils import timezone

@login_required
def loan_list(request):
    loans = Loan.objects.filter(user=request.user).order_by('-created_at')

    search = request.GET.get('search')
    status = request.GET.get('status')
    date_filter = request.GET.get('date')
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    # ✅ Clean "None"
    if search == "None":
        search = None

    if status == "None":
        status = None

    if date_filter == "None":
        date_filter = None

    # 🔍 SEARCH
    if search:
        loans = loans.filter(
            Q(person_name__icontains=search) |
            Q(person_contact__icontains=search) |
            Q(notes__icontains=search)
        )

    # 📅 DATE FILTER
    today = timezone.now().date()

    if date_filter == 'today':
        loans = loans.filter(start_date=today)

    elif date_filter == 'week':
        start = today - timezone.timedelta(days=today.weekday())
        loans = loans.filter(start_date__gte=start)

    elif date_filter == 'month':
        loans = loans.filter(
            start_date__month=today.month,
            start_date__year=today.year
        )

    elif date_filter == 'year':
        loans = loans.filter(start_date__year=today.year)

    # 📆 CUSTOM RANGE
    if from_date:
        loans = loans.filter(start_date__gte=from_date)

    if to_date:
        loans = loans.filter(start_date__lte=to_date)

    # 🔴 OVERDUE (first)
    overdue_loans = [loan for loan in loans if loan.is_overdue]

    # 🟢 ACTIVE (excluding overdue)
    active_loans = [
        loan for loan in loans
        if loan.status in ['active', 'partial'] and not loan.is_overdue
    ]

    # ⚪ SETTLED
    settled_loans = loans.filter(status='settled')

    # 🎯 STATUS FILTER LOGIC
    if status == 'overdue':
        active_loans = []
        settled_loans = []

    elif status == 'active':
        overdue_loans = []
        settled_loans = []

    elif status == 'settled':
        overdue_loans = []
        active_loans = []

    elif status == 'all':
        pass

    # ✅ DEFAULT (no filter → hide settled)
    elif not status:
        settled_loans = []

    context = {
        'overdue_loans': overdue_loans,
        'active_loans': active_loans,
        'settled_loans': settled_loans,
        'search_query': search,
        'status_filter': status,
        'date_filter': date_filter,
        'status_options': ['all', 'active', 'settled', 'overdue'],
    }

    return render(request, 'loans/list.html', context)


@login_required
def loan_create(request):
    form = LoanForm(request.POST or None)

    if form.is_valid():
        obj = form.save(commit=False)
        obj.user = request.user
        obj.save()
        return redirect('loans:list')

    return render(request, 'loans/form.html', {'form': form})


@login_required
def loan_detail(request, pk):
    loan = get_object_or_404(Loan, pk=pk, user=request.user)
    repayments = loan.repayments.all()

    return render(request, 'loans/detail.html', {
        'loan': loan,
        'repayments': repayments
    })


@login_required
def loan_update(request, pk):
    loan = get_object_or_404(Loan, pk=pk, user=request.user)

    if request.method == 'POST':
        loan.loan_type = request.POST.get('loan_type')
        loan.person_name = request.POST.get('person_name')
        loan.principal_amount = request.POST.get('principal_amount')
        loan.start_date = request.POST.get('start_date')
        loan.due_date = request.POST.get('due_date')

        # ✅ Handle interest
        interest_rate = request.POST.get('interest_rate') or 0
        loan.interest_rate = interest_rate
        loan.interest_type = request.POST.get('interest_type') or 'simple'

        loan.save()

        return redirect('loans:detail', pk=loan.id)

    return render(request, 'loans/form.html', {
        'loan': loan
    })



from django.contrib import messages


@login_required
def loan_delete(request, pk):
    loan = get_object_or_404(Loan, pk=pk, user=request.user)

    if request.method == 'POST':
        try:
            loan.delete()
            messages.success(request, "Loan deleted successfully")
            return redirect('loans:list')

        except Exception as e:
            messages.error(
                request,
                "Cannot delete loan. It may have related repayments."
            )
            return redirect('loans:detail', pk=pk)

    return redirect('loans:detail', pk=pk)

from django.contrib import messages
from decimal import Decimal, InvalidOperation


@login_required
def add_repayment(request, pk):
    loan = get_object_or_404(Loan, pk=pk, user=request.user)

    if request.method == 'POST':
        amount = request.POST.get('amount')
        paid_date = request.POST.get('paid_date')

        if not amount or not paid_date:
            messages.error(request, "All fields are required.")
            return redirect('loans:detail', pk=pk)

        try:
            amount = Decimal(amount)
        except:
            messages.error(request, "Invalid amount.")
            return redirect('loans:detail', pk=pk)

        if amount <= 0:
            messages.error(request, "Amount must be greater than 0.")
            return redirect('loans:detail', pk=pk)

        if amount > loan.remaining_amount:
            messages.error(
                request,
                f"Cannot pay more than remaining (Rs. {loan.remaining_amount})"
            )
            return redirect('loans:detail', pk=pk)

        # Save
        LoanRepayment.objects.create(
            loan=loan,
            amount=amount,
            paid_date=paid_date
        )

        # Refresh values
        loan.refresh_from_db()

        # Status update
        if loan.remaining_amount <= 0:
            loan.status = 'settled'
        elif loan.total_repaid > 0:
            loan.status = 'partial'
        else:
            loan.status = 'active'

        loan.save()

        messages.success(request, "Repayment added successfully.")
        return redirect('loans:detail', pk=pk)

    return redirect('loans:detail', pk=pk)