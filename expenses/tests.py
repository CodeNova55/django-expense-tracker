from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Expense
from .views import parse_month

User = get_user_model()


class ExpenseModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("njeri", password="pass12345")

    def test_str_contains_title(self):
        expense = Expense.objects.create(
            owner=self.user, title="Lunch", amount=Decimal("350")
        )
        self.assertIn("Lunch", str(expense))

    def test_default_category_is_other(self):
        expense = Expense.objects.create(
            owner=self.user, title="Misc", amount=Decimal("10")
        )
        self.assertEqual(expense.category, Expense.Category.OTHER)


class ExpenseViewTests(TestCase):
    def setUp(self):
        self.alice = User.objects.create_user("alice", password="pass12345")
        self.bob = User.objects.create_user("bob", password="pass12345")
        self.alice_expense = Expense.objects.create(
            owner=self.alice, title="Alice lunch", amount=100, date=date(2026, 10, 5)
        )
        self.bob_expense = Expense.objects.create(
            owner=self.bob, title="Bob lunch", amount=200, date=date(2026, 10, 5)
        )

    def login_alice(self):
        self.client.login(username="alice", password="pass12345")

    def test_list_requires_login(self):
        response = self.client.get(reverse("expense_list"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_user_sees_only_own_expenses(self):
        self.login_alice()
        response = self.client.get(reverse("expense_list"))
        self.assertContains(response, "Alice lunch")
        self.assertNotContains(response, "Bob lunch")

    def test_create_expense_sets_owner(self):
        self.login_alice()
        self.client.post(
            reverse("expense_create"),
            {
                "title": "Bus fare",
                "amount": "120",
                "category": "transport",
                "date": "2026-10-05",
                "note": "",
            },
        )
        self.assertTrue(
            Expense.objects.filter(title="Bus fare", owner=self.alice).exists()
        )

    def test_cannot_edit_other_users_expense(self):
        self.login_alice()
        response = self.client.get(reverse("expense_update", args=[self.bob_expense.pk]))
        self.assertEqual(response.status_code, 404)

    def test_cannot_delete_other_users_expense(self):
        self.login_alice()
        response = self.client.post(reverse("expense_delete", args=[self.bob_expense.pk]))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Expense.objects.filter(pk=self.bob_expense.pk).exists())


class SummaryTests(TestCase):
    def setUp(self):
        self.alice = User.objects.create_user("alice", password="pass12345")
        self.bob = User.objects.create_user("bob", password="pass12345")
        Expense.objects.create(
            owner=self.alice, title="Groceries", amount=200,
            category="food", date=date(2026, 10, 5),
        )
        Expense.objects.create(
            owner=self.alice, title="Matatu", amount=100,
            category="transport", date=date(2026, 10, 10),
        )
        Expense.objects.create(
            owner=self.alice, title="Last month food", amount=50,
            category="food", date=date(2026, 9, 20),
        )
        Expense.objects.create(
            owner=self.bob, title="Bob food", amount=999,
            category="food", date=date(2026, 10, 5),
        )
        self.client.login(username="alice", password="pass12345")

    def test_summary_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("expense_summary"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_month_total_ignores_other_users_and_months(self):
        response = self.client.get(reverse("expense_summary") + "?month=2026-10")
        self.assertEqual(response.context["total"], Decimal("300"))
        self.assertEqual(response.context["count"], 2)

    def test_category_breakdown_percentages(self):
        response = self.client.get(reverse("expense_summary") + "?month=2026-10")
        breakdown = response.context["breakdown"]
        self.assertEqual(breakdown[0]["label"], "Food")
        self.assertEqual(breakdown[0]["percent"], 67)
        self.assertEqual(breakdown[1]["label"], "Transport")
        self.assertEqual(breakdown[1]["percent"], 33)

    def test_previous_month_shows_only_that_month(self):
        response = self.client.get(reverse("expense_summary") + "?month=2026-09")
        self.assertEqual(response.context["total"], Decimal("50"))
        self.assertEqual(response.context["count"], 1)

    def test_invalid_month_falls_back_to_current_month(self):
        response = self.client.get(reverse("expense_summary") + "?month=abc")
        self.assertEqual(
            response.context["month_start"], timezone.localdate().replace(day=1)
        )

    def test_month_navigation_crosses_year_boundaries(self):
        december = self.client.get(reverse("expense_summary") + "?month=2026-12")
        self.assertEqual(december.context["next_month"], "2027-01")
        january = self.client.get(reverse("expense_summary") + "?month=2026-01")
        self.assertEqual(january.context["previous_month"], "2025-12")


class ParseMonthTests(TestCase):
    def test_parse_month_handles_good_and_bad_values(self):
        current = timezone.localdate().replace(day=1)
        self.assertEqual(parse_month("2026-10"), date(2026, 10, 1))
        self.assertEqual(parse_month("abc"), current)
        self.assertEqual(parse_month("2026-13"), current)
        self.assertEqual(parse_month(None), current)