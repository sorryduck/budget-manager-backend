from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class AppUser(AbstractUser):
    budget = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)


class ExpensesCategory(models.Model):
    title = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Expenses category"
        verbose_name_plural = "Expenses categories"

    def __str__(self):
        return self.title


class Store(models.Model):
    title = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Store"
        verbose_name_plural = "Stores"

    def __str__(self):
        return self.title


class Expenses(models.Model):
    date = models.DateField(default=timezone.now, editable=True)
    title = models.CharField(max_length=255)
    budget = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=16, decimal_places=2)
    category = models.ForeignKey(
        ExpensesCategory, on_delete=models.SET_NULL, blank=True, null=True
    )
    store = models.ForeignKey(Store, on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        verbose_name = "Expense"
        verbose_name_plural = "Expenses"

    def __str__(self):
        return f"{self.title} - [{self.budget}]"
