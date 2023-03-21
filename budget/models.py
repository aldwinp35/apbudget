from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    
    # id = models.AutoField(primary_key=True)
    # first_name = models.CharField(blank=True, max_length=150)
    # last_name = models.CharField(blank=True, max_length=150)
    # email = models.EmailField(blank=True, max_length=254)
    # username = models.CharField(max_length=150, unique=True)
    # password = models.CharField(max_length=128)

    def __str__(self):
        return f"{self.pk} - {self.email}"


class IncomeCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="income_categories")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.pk} - {self.name} ({self.user.email})"


class Income(models.Model):
    category = models.ForeignKey(IncomeCategory, models.CASCADE, related_name="incomes")
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    date = models.DateField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="incomes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.pk} - {self.category.name}: {self.amount}"


class BudgetCategory(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="budget_categories")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.pk} - {self.name}"


class ItemCategory(models.Model):
    budget_category = models.ForeignKey(BudgetCategory, on_delete=models.CASCADE, related_name="item_categories")
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="item_categories")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.pk} - {self.name}"


class BudgetItem(models.Model):
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    item_category = models.ForeignKey(ItemCategory, on_delete=models.CASCADE, related_name="budget_items")
    budget_category = models.ForeignKey(BudgetCategory, on_delete=models.CASCADE, related_name="budget_items")
    date = models.DateField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="budget_items")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.pk} - {self.item_category.name} | planned: {self.amount} | {self.date}"


class Member(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="members")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.pk} - {self.name}"


class Expense(models.Model):
    budget_item = models.ForeignKey(BudgetItem, on_delete=models.CASCADE, related_name="expenses")
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="expenses")
    date = models.DateField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="expenses")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.pk} - {self.budget_item.item_category.name} | spent: {self.amount} | {self.date}"
