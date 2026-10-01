from datetime import date, timedelta

from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    TemplateView,
    UpdateView,
)

from .forms import ExpenseForm
from .models import Expense


class OwnerExpensesMixin(LoginRequiredMixin):
    """Users can only see and change their own expenses."""

    def get_queryset(self):
        return Expense.objects.filter(owner=self.request.user)


class ExpenseListView(OwnerExpensesMixin, ListView):
    model = Expense
    context_object_name = "expenses"


class ExpenseCreateView(LoginRequiredMixin, CreateView):
    model = Expense
    form_class = ExpenseForm
    success_url = reverse_lazy("expense_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class ExpenseUpdateView(OwnerExpensesMixin, UpdateView):
    model = Expense
    form_class = ExpenseForm
    success_url = reverse_lazy("expense_list")


class ExpenseDeleteView(OwnerExpensesMixin, DeleteView):
    model = Expense
    success_url = reverse_lazy("expense_list")


class SignUpView(CreateView):
    form_class = UserCreationForm
    template_name = "registration/signup.html"
    success_url = reverse_lazy("expense_list")

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response


def parse_month(value):
    """Turn '2026-10' into date(2026, 10, 1). Falls back to the current month."""
    try:
        year, month = (int(part) for part in value.split("-"))
        return date(year, month, 1)
    except (AttributeError, ValueError):
        return timezone.localdate().replace(day=1)


class SummaryView(LoginRequiredMixin, TemplateView):
    template_name = "expenses/summary.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        month_start = parse_month(self.request.GET.get("month"))
        expenses = Expense.objects.filter(
            owner=self.request.user,
            date__year=month_start.year,
            date__month=month_start.month,
        )
        total = expenses.aggregate(total=Sum("amount"))["total"] or 0
        labels = dict(Expense.Category.choices)

        breakdown = []
        rows = expenses.values("category").annotate(total=Sum("amount")).order_by("-total")
        for row in rows:
            breakdown.append(
                {
                    "label": labels.get(row["category"], row["category"]),
                    "total": row["total"],
                    "percent": round(row["total"] / total * 100) if total else 0,
                }
            )

        previous_month = (month_start - timedelta(days=1)).replace(day=1)
        next_month = (month_start + timedelta(days=32)).replace(day=1)
        context.update(
            {
                "month_start": month_start,
                "total": total,
                "count": expenses.count(),
                "breakdown": breakdown,
                "previous_month": previous_month.strftime("%Y-%m"),
                "next_month": next_month.strftime("%Y-%m"),
            }
        )
        return context