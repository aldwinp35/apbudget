import datetime
from django.shortcuts import get_object_or_404
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework import generics, status, views
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse

from budget.models import *
from .serializers import *
from .filters import *
from .mixins import *


# ROOT
@api_view(["GET"])
def Root(request):
    return Response(
        {
            "users": reverse("user", request=request),
            "income": reverse("income", request=request),
            "budget": reverse("budget", request=request),
            "budget-item": reverse("budget_items", request=request),
            "expense": reverse("expense", request=request),
            "balance": reverse("balance", request=request),
            "income-category": reverse("income_category", request=request),
            "item-category": reverse("item_category", request=request),
            "register": reverse("register", request=request),
            "account": reverse("account", request=request),
            "change-password": reverse("change_password", request=request),
            "request-reset-password": reverse("request_reset_password", request=request),
            "reset-password": reverse("reset_password", request=request),
        }
    )


# USER
class UserList(views.APIView):
    """
    List all users or create a new one.

    Endpoint: `/api/user/`
    """

    serializer_class = UserSerializer

    def get(self, request):
        queryset = User.objects.all()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetail(views.APIView):
    """
    Retrieve, update or destroy an user.

    Endpoint: `/api/user/<user-id>/`
    """

    serializer_class = UserSerializer

    def get_object(self, pk):
        return get_object_or_404(User, pk=pk)

    def get(self, request, pk):
        queryset = self.get_object(pk)
        serializer = self.serializer_class(queryset)
        return Response(serializer.data)

    def put(self, request, pk):
        queryset = self.get_object(pk)
        serializer = self.serializer_class(queryset, data=request.data)
        if serializer.is_valid():
            # Remove username to avoid unique constraint error.
            serializer.validated_data.pop("username")
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        queryset = self.get_object(pk)
        queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ACCOUNT
# Unauthenticated users
class Register(generics.GenericAPIView):
    """
    Create an user from an unauthenticated endpoint.

    Endpoint: `/api/account/register`
    """

    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class RequestResetPassword(generics.GenericAPIView):
    """
    Generate a password reset link.

    Endpoint: `/api/account/password-request-reset/`
    """

    serializer_class = RequestResetPasswordSerializer
    permission_classes = [AllowAny]

    def get_object(self, email):
        return get_object_or_404(User, email=email)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            email = serializer.data["email"]
            url = serializer.data["url"]
            user = self.get_object(email)
            encoded_pk = urlsafe_base64_encode(force_bytes(user.pk))
            token = PasswordResetTokenGenerator().make_token(user)
            reset_link = f"{url}password-reset/?token={token}&id={encoded_pk}"
            # SEND EMAIL TO USER
            return Response(
                {"email message": f"To reset your psasword, click on this link: {reset_link}"},
                status=status.HTTP_202_ACCEPTED,
            )


class ResetPassword(generics.GenericAPIView):
    """
    Reset user's password. A link is required.

    Endpoint: `/api/account/password-reset/`
    """

    serializer_class = ResetPasswordSerializer
    permission_classes = [AllowAny]

    def get_object(self, pk):
        return get_object_or_404(User, pk=pk)

    def put(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        if serializer.is_valid(raise_exception=True):
            password = serializer.validated_data.get("password")
            token = kwargs.get("token")
            encoded_pk = self.kwargs.get("encoded_pk")
            if token is None or encoded_pk is None:
                raise serializers.ValidationError({"reset": "Invalid request."})

            pk = urlsafe_base64_decode(encoded_pk).decode()
            user = User.objects.get(pk=pk)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise serializers.ValidationError("The reset token is invalid")

            user.set_password(password)
            user.save()
            # SEND EMAIL TO USER
            return Response({"email message": "Your password has been reset."}, status=status.HTTP_200_OK)


# Authenticated users
class UserAccount(generics.GenericAPIView):
    """
    Displays the details of the authenticated user or updates their data.

    Endpoint: `/api/account/`
    """

    serializer_class = UserSerializer

    def get(self, request):
        user = request.user
        serializer = self.serializer_class(user)
        return Response(serializer.data)

    def put(self, request):
        user = request.user
        serializer = self.serializer_class(user, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePassword(generics.GenericAPIView):
    """
    Change password for authenticated users.

    Endpoint: `/api/account/password-change/`
    """

    serializer_class = ChangePasswordSerializer

    def put(self, request):
        user = User.objects.get(pk=request.user.pk)
        serializer = self.serializer_class(user, request.data, context={"request": request})

        if serializer.is_valid(raise_exception=True):
            new_password = serializer.validated_data["new_password"]
            user.set_password(new_password)
            user.save()
            return Response(status=status.HTTP_200_OK)


# INCOME CATEGORY
class IncomeCategoryListCreate(generics.ListCreateAPIView):
    """
    List all income categories or create a new one.

    Endpoint: `/api/income-category/`
    """

    queryset = IncomeCategory.objects.all()
    serializer_class = IncomeCategorySerializer
    ordering = "name"

    def perform_create(self, serializer):
        description = serializer.validated_data.get("description")
        name = serializer.validated_data.get("name")
        serializer.save(user=self.request.user, name=name, description=description)


class IncomeCategoryDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or destroy an income category.

    Endpoint: `/api/income-category/<income-category-id>/`
    """

    queryset = IncomeCategory.objects.all()
    serializer_class = IncomeCategorySerializer


# INCOME
class IncomeListCreate(ValidateDateQueryStringParameters, generics.ListCreateAPIView):
    """
    List all income or create a new income.

    Endpoint: `/api/income/`
    """

    queryset = Income.objects.all()
    serializer_class = IncomeSerializer
    filterset_class = IncomeFilter
    ordering = "date"

    def perform_create(self, serializer):
        amount = serializer.validated_data.get("amount")
        category = serializer.validated_data.get("category")
        date = serializer.validated_data.get("date")
        serializer.save(user=self.request.user, amount=amount, category=category, date=date)


class IncomeUpdate(generics.RetrieveUpdateAPIView):
    """
    Retrieve and update an income.

    Endpoint: `/api/income/<income-id>/update/`
    """

    queryset = Income.objects.all()
    serializer_class = IncomeSerializer
    lookup_field = "pk"


class IncomeDestroy(generics.RetrieveDestroyAPIView):
    """
    Retrieve and destroy an income.

    Endpoint: `/api/income/<income-id>/delete/`
    """

    queryset = Income.objects.all()
    serializer_class = IncomeSerializer
    lookup_field = "pk"


# BUDGET CATEGORY
class BudgetListCreate(ValidateDateQueryStringParameters, generics.ListCreateAPIView):
    """
    - List all budget categories and its items.
    - Create a new budget category.

    Endpoint: `/api/budget/`
    """

    queryset = BudgetCategory.objects.all()
    serializer_class = BudgetCategorySerializer
    filterset_class = BudgetCategoryFilter
    ordering = "name"

    def perform_create(self, serializer):
        name = serializer.validated_data.get("name")
        serializer.save(user=self.request.user, name=name)


class BudgetUpdate(generics.RetrieveUpdateAPIView):
    """
    Retrieve and update a budget category.

    Endpoint: `/api/budget/<budget-id>/update/`
    """

    queryset = BudgetCategory.objects.all()
    serializer_class = BudgetCategorySerializer


class BudgetDestroy(generics.RetrieveDestroyAPIView):
    """
    Retrieve and destroy a budget category.

    Endpoint: `/api/budget/<budget-id>/delete/`
    """

    queryset = BudgetCategory.objects.all()
    serializer_class = BudgetCategorySerializer


# ITEM CATEGORY
class ItemCategoryListCreate(generics.ListCreateAPIView):
    """
    List all item categories or create a new one.

    Endpoint: `/api/item-category/`
    """

    queryset = ItemCategory.objects.all()
    serializer_class = ItemCategorySerializer
    ordering = "name"

    def perform_create(self, serializer):
        budget_category = serializer.validated_data.get("budget_category")
        name = serializer.validated_data.get("name")
        serializer.save(user=self.request.user, name=name, budget_category=budget_category)


class ItemCategoryDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or destroy an item category.

    Endpoint: `/api/item-category/<item-category-id>/`
    """

    queryset = ItemCategory.objects.all()
    serializer_class = ItemCategorySerializer


# BUDGET ITEM
class BudgetItemListCreate(ValidateDateQueryStringParameters, generics.ListCreateAPIView):
    """
    List budget items or create a new one.

    Endpoints:
    - List all budget items. `/api/budget-item/`
    - List all items under a budget category. `/api/budget/<budget-id>/items/`
    """

    queryset = BudgetItem.objects.all()
    serializer_class = BudgetItemSerializer
    filterset_class = BudgetItemFilter
    ordering = "-date"

    # Get items by budget category
    def get_queryset(self):
        queryset = super().get_queryset()
        budget_category_id = self.kwargs.get("pk")
        if budget_category_id:
            return queryset.filter(budget_category=budget_category_id)
        return queryset

    def perform_create(self, serializer):
        amount = serializer.validated_data.get("amount")
        date = serializer.validated_data.get("date")
        item_category = serializer.validated_data.get("item_category")
        serializer.save(
            user=self.request.user,
            amount=amount,
            date=date,
            item_category=item_category,
            budget_category=item_category.budget_category,
        )


class BudgetItemDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or destroy a budget item.

    Endpoints:
    - `/api/budget-item/<item-id>/`
    - `/api/budget/<budget-id>/items/<item-id>/`
    """

    queryset = BudgetItem.objects.all()
    serializer_class = BudgetItemSerializer
    lookup_url_kwarg = "id"

    # Get items by budget category
    def get_queryset(self):
        queryset = super().get_queryset()
        category_id = self.kwargs.get("pk")
        if category_id:
            return queryset.filter(budget_category=category_id)
        return queryset


# EXPENSE
class ExpensesList(ValidateDateQueryStringParameters, generics.ListCreateAPIView):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    filterset_class = ExpenseFilter
    # ordering = "budget_item__item_category__name"
    ordering = "-date"

    def perform_create(self, serializer):
        amount = serializer.validated_data.get("amount")
        member = serializer.validated_data.get("member")
        budget_item = serializer.validated_data.get("budget_item")
        budget_item_date = BudgetItem.objects.get(pk=budget_item.pk).date
        expense_date = date(budget_item_date.year, budget_item_date.month, date.today().day)
        serializer.save(user=self.request.user, amount=amount, date=expense_date, member=member)


class ExpensesDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer


class Balance(views.APIView):
    """
    Calculate the remaining balance based on the monthly income and expenses.

    Endpoint: `/api/balance/`

    Required params:
    - `month` a number between 1 - 12.
    - `year` a four digit number.

    For example: `/api/balance/?month=1&year=2023`
    """

    def get(self, request):

        user = request.user
        month = request.GET.get("month")
        year = request.GET.get("year")

        # Make sure month and year are passed as query params
        if not month and not year:
            return Response(
                {"url_params": "Missing query params: `month` and `year` are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Check if year it's a valid date parameter
            if year:
                year = int(year)
                datetime.date(year, 1, 1)

            # Check for a valid month
            if month:
                month = int(month)
                if month < 1 and month > 12:
                    raise
        except:
            return Response({"url_params": "Invalid query string parameters."}, status=status.HTTP_400_BAD_REQUEST)

        # Get monthly income
        income = sum(
            Income.objects.filter(
                user=user,
                date__month=month,
                date__year=year,
            ).values_list("amount", flat=True)
        )

        # Get monthly expenses
        expenses = sum(
            Expense.objects.filter(
                user=user,
                date__month=month,
                date__year=year,
            ).values_list("amount", flat=True)
        )

        data = {
            "expenses": expenses,
            "income": income,
            "balance": income - expenses,
        }

        return Response(data)