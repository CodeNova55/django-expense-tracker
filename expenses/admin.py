from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class Expense(models.Model):
    class Category(models.TextChoices):
        FOOD = "food", "Food"
        TRANSPORT = "transport", "Transport"
        RENT = "rent", "Rent & Utilities"
        AIRTIME = "airtime", "Airtime & Data"
        SHOPPING = "shopping", "Shopping"
        OTHER = "other", "Other"

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="expenses",
    )
    title = models.CharField(max_length=200)
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)]
    )  # in KES
    category = models.CharField(
        max_length=20, choices=Category.choices, default=Category.OTHER
    )
    date = models.DateField(default=timezone.localdate)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-created_at"]

    def __str__(self):
        return f"{self.title} (KES {self.amount})"