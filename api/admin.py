from django.contrib import admin

from budget.models import *


admin.site.register(User)
admin.site.register(IncomeCategory)
admin.site.register(Income)
admin.site.register(BudgetCategory)
admin.site.register(ItemCategory)
admin.site.register(BudgetItem)
admin.site.register(Member)
admin.site.register(Expense)
