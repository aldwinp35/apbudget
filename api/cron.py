from django_apscheduler.models import DjangoJobExecution
from django_apscheduler import util
from datetime import date, timedelta


from budget.models import *


def copy_budget_item():
    """
    Copy `budget-items` on the 1st day of every month.\n
    This apply to all users, so that every month they can see their budget's item,\n
    without having to enter the budget's item manually each month.
    """

    users = User.objects.all()
    yesterday = date.today() + timedelta(days=-1)

    for user in users:
        budget_items = BudgetItem.objects.filter(user=user, date__year=yesterday.year, date__month=yesterday.month)
        # budget_items = BudgetItem.objects.filter(user=user, date__year=2023, date__month=2) # TEST
        if budget_items.count() > 0:
            for item in budget_items.values():
                # Remove unnecessary data
                item.pop("id")
                item.pop("created_at")
                item.pop("updated_at")

                # Update date
                item["date"] = date.today()
                BudgetItem.objects.create(**item)


# The `close_old_connections` decorator ensures that database connections, that have become
# unusable or are obsolete, are closed before and after your job has run. You should use it
# to wrap any jobs that you schedule that access the Django database in any way.
@util.close_old_connections
def delete_old_job_executions(max_age=604_800):
    """
    This job deletes APScheduler job execution entries older than `max_age` from the database.
    It helps to prevent the database from filling up with old historical records that are no
    longer useful.

    :param max_age: The maximum length of time to retain historical job execution records.
                    Defaults to 7 days.
    """
    DjangoJobExecution.objects.delete_old_job_executions(max_age)
