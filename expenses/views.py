from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

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