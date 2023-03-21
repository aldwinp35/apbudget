from django_filters import rest_framework as filters
from rest_framework import filters as drf_filters

from budget.models import *


class IsOwnerFilterBackend(drf_filters.BaseFilterBackend):
    """
    Filter that only allows users to see their own objects.
    """

    def filter_queryset(self, request, queryset, view):
        return queryset.filter(user=request.user)


class IncomeFilter(filters.FilterSet):
    """
    Provide filters and ordering for Income objects.
    """

    # Filter by month and year
    month = filters.NumberFilter(field_name="date", lookup_expr="month", label="Month")
    year = filters.NumberFilter(field_name="date", lookup_expr="year", label="Year")

    # Filter by date range
    start = filters.DateFilter(field_name="date", lookup_expr="gte", label="Start Date")
    end = filters.DateFilter(field_name="date", lookup_expr="lte", label="End Date")

    # Order by fields
    ordering = filters.OrderingFilter(
        fields=(
            ("date", "date"),
            ("category__name", "name"),
            ("amount", "amount"),
        )
    )

    class Meta:
        model = Income
        fields = ["date", "month", "year", "start", "end"]


class BudgetItemFilter(filters.FilterSet):
    """
    Provide filters and ordering for BudgetItem objects.
    """

    # Filter by item category name
    name = filters.CharFilter(field_name="item_category", lookup_expr="name", label="Name")

    # Filter by month and year
    month = filters.NumberFilter(field_name="date", lookup_expr="month", label="Month")
    year = filters.NumberFilter(field_name="date", lookup_expr="year", label="Year")

    # Filter by date range
    start = filters.DateFilter(field_name="date", lookup_expr="gte", label="Start Date")
    end = filters.DateFilter(field_name="date", lookup_expr="lte", label="End Date")

    # Order by fields
    ordering = filters.OrderingFilter(
        fields=(
            ("item__name", "name"),
            ("amount", "amount"),
        )
    )

    class Meta:
        model = BudgetItem
        fields = ["date", "month", "year", "start", "end", "name"]


class BudgetCategoryFilter(filters.FilterSet):
    """
    Provide filters for BudgetCategory objects.
    """

    name = filters.CharFilter(field_name="name", lookup_expr="icontains", label="Name")

    class Meta:
        model = BudgetCategory
        fields = ["name"]


class ExpenseFilter(filters.FilterSet):
    """
    Provide filters and ordering for Expense objects.
    """

    # Filter by month and year
    month = filters.NumberFilter(field_name="date", lookup_expr="month", label="Month")
    year = filters.NumberFilter(field_name="date", lookup_expr="year", label="Year")

    # Order by fields
    ordering = filters.OrderingFilter(
        fields=(
            ("date", "date"),
            ("budget_item__item_category__name", "name"),
        )
    )

    class Meta:
        model = Expense
        fields = ["date", "month", "year"]
