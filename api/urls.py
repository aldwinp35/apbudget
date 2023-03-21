from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from . import views


urlpatterns = [
    # Root
    path("", views.Root, name="root"),
    # Tokens
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    # User
    path("user/", views.UserList.as_view(), name="user"),
    path("user/<int:pk>/", views.UserDetail.as_view(), name="user_detail"),
    # Account
    path("account/", views.UserAccount.as_view(), name="account"),
    path("account/register/", views.Register.as_view(), name="register"),
    path("account/password-change/", views.ChangePassword.as_view(), name="change_password"),
    path("account/password-reset/", views.ResetPassword.as_view(), name="reset_password"),
    path("account/password-request-reset/", views.RequestResetPassword.as_view(), name="request_reset_password"),
    # Income Category
    path("income-category/", views.IncomeCategoryListCreate.as_view(), name="income_category"),
    path("income-category/<int:pk>/", views.IncomeCategoryDetail.as_view(), name="income_detail"),
    # Income
    path("income/", views.IncomeListCreate.as_view(), name="income"),
    path("income/<int:pk>/update/", views.IncomeUpdate.as_view(), name="income_update"),
    path("income/<int:pk>/delete/", views.IncomeDestroy.as_view(), name="income_delete"),
    # Budget
    path("budget/", views.BudgetListCreate.as_view(), name="budget"),
    path("budget/<int:pk>/update/", views.BudgetUpdate.as_view(), name="budget_update"),
    path("budget/<int:pk>/delete/", views.BudgetDestroy.as_view(), name="budget_delete"),
    # Budget's Item
    path("budget/<int:pk>/items/", views.BudgetItemListCreate.as_view(), name="budgets_item"),
    path("budget/<int:pk>/items/<int:id>/", views.BudgetItemDetail.as_view(), name="budgets_item_detail"),
    # Budget Items
    path("budget-item/", views.BudgetItemListCreate.as_view(), name="budget_items"),
    path("budget-item/<int:id>/", views.BudgetItemDetail.as_view(), name="budget_items_detail"),
    # Item Category
    path("item-category/", views.ItemCategoryListCreate.as_view(), name="item_category"),
    path("item-category/<int:pk>/", views.ItemCategoryDetail.as_view(), name="item_detail"),
    # Expense
    path("expense/", views.ExpensesList.as_view(), name="expense"),
    path("expense/<int:pk>/", views.ExpensesDetail.as_view(), name="expense_detail"),
    path("balance/", views.Balance.as_view(), name="balance"),
]
