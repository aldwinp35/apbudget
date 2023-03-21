import re
from datetime import date
from rest_framework import serializers

from budget.models import *

# USER
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "username", "email"]


# ACCOUNT
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "username",
            "password",
        ]


class RequestResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    url = serializers.URLField()

    class Meta:
        fields = ["email", "url"]


class ResetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True, min_length=3)
    confirm_password = serializers.CharField(write_only=True, min_length=3)

    def validate(self, attrs):
        # Make sure the new password and confirmation are the same.
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError("The new password and confirmation do not match. Please try again.")
        return super().validate(attrs)

    def validate_new_password(self, value):
        # Make sure the new password and current password are different.
        request = self.context.get("request")
        user = request.user
        if user.check_password(value):
            raise serializers.ValidationError(
                "The new password cannot be the same as your current password. Please try again."
            )
        return value


class ChangePasswordSerializer(ResetPasswordSerializer):
    old_password = serializers.CharField(write_only=True, min_length=3)

    def validate_old_password(self, value):
        # Make sure the current password is correct
        request = self.context.get("request")
        user = request.user
        if not user.check_password(value):
            raise serializers.ValidationError("Your old password is incorrect. Please try again.")
        return value


# INCOME
class IncomeCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = IncomeCategory
        fields = ["id", "name", "description"]

    def validate_name(self, value):
        value = clear_string(value)
        qs = IncomeCategory.objects.filter(name__iexact=value)
        if qs.exists():
            raise serializers.ValidationError(f"{value} is already a income category.")
        return value


class IncomeSerializer(serializers.ModelSerializer):
    """
    Serialize Income to JSON object.
    """

    name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Income
        fields = [
            "id",
            "amount",
            "category",
            "name",
            "date",
            "created_at",
            "updated_at",
        ]


# BUDGET
class BudgetItemSerializer(serializers.ModelSerializer):
    """
    Serialize BudgetItem to JSON objects.
    """

    name = serializers.CharField(read_only=True, source="item_category.name")
    category = serializers.IntegerField(source="item_category.pk")
    spent = serializers.SerializerMethodField(read_only=True)
    difference = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = BudgetItem
        fields = [
            "id",
            "amount",
            "spent",
            "difference",
            "date",
            # "item_category",
            "category",
            "name",
            "created_at",
            "updated_at",
        ]

    def get_spent(self, instance):
        expenses = instance.expenses.values_list("amount", flat=True)
        return sum(expenses)

    def get_difference(self, instance):
        return instance.amount - self.get_spent(instance)

    def validate_item_category(self, item_category):
        request = self.context.get("request")
        # Make sure that an user don't have more than one item per budget on a month
        obj_date = date.fromisoformat(request.data["date"])
        item_exists = BudgetItem.objects.filter(
            item_category=item_category, date__month=obj_date.month, date__year=obj_date.year
        ).exists()
        if item_exists:
            raise serializers.ValidationError("You already added this item on this date.")

    def update(self, instance, validated_data):
        # User can't change an item_category
        if validated_data["item_category"] != instance.item_category:
            raise serializers.ValidationError({"item_category": ["Cannot change item category."]})
        return super().update(instance, validated_data)


class BudgetCategorySerializer(serializers.ModelSerializer):
    """
    - Serialize BudgetCategory to JSON objects.
    - Add BudgetItem (items) as childs of BudgetCategory (budget).
    """

    items = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = BudgetCategory
        fields = ["id", "name", "items"]

    # Return all BudgetItem (items) belonging to BudgetCategory
    def get_items(self, instance):
        items = instance.budget_items
        request = self.context.get("request")
        if request:
            month = request.GET.get("month")
            year = request.GET.get("year")
            date = request.GET.get("date")

            # Filter by month and year
            if month and year:
                items = items.filter(date__month=month, date__year=year)

            # Filter by date
            if date:
                items = items.filter(date=date)

        return BudgetItemSerializer(items, many=True).data

    # Prevent user to create BudgetCategory instances with the same name.
    def validate_name(self, value):
        value = clear_string(value)
        qs = BudgetCategory.objects.filter(name__iexact=value)
        if qs.exists():
            raise serializers.ValidationError(f"{value} is already a budget.")
        return value


# ITEM CATEGORY
class ItemCategorySerializer(serializers.ModelSerializer):
    """
    Serialize ItemCategory to JSON objects.
    """

    class Meta:
        model = ItemCategory
        # exclude = ['user']
        fields = [
            "id",
            "name",
            "budget_category",
            "created_at",
            "updated_at",
        ]

    def validate_name(self, value):
        value = clear_string(value)
        qs = ItemCategory.objects.filter(name__iexact=value)
        if qs.exists():
            raise serializers.ValidationError(f"{value} is already an item category.")
        return value


# EXPENSES
class ExpenseSerializer(serializers.ModelSerializer):
    budget_item_name = serializers.CharField(source="budget_item.item_category.name", read_only=True)
    member_name = serializers.CharField(source="member.name", read_only=True)
    date = serializers.DateField(read_only=True)

    class Meta:
        model = Expense
        fields = [
            "id",
            "amount",
            "budget_item",
            "budget_item_name",
            "member",
            "member_name",
            "date",
            "created_at",
            "updated_at",
        ]


def clear_string(val):
    """
    Capitalize, remove special characters and trailing spaces from a string.
    """
    val = val.strip().capitalize()
    val = re.sub("[^\w\s]+", "", val)
    return val
