import datetime
from rest_framework import status
from rest_framework.response import Response

class AddRequestToContext():
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context


class ValidateDateQueryStringParameters():
    def list(self, request, *args, **kwargs):
        month = request.GET.get("month") # Two digit number: (mm)
        year = request.GET.get("year") # Four digit number: (yyyy)
        date = request.GET.get("date") # ISO date format: (yyyy-mm-dd)

        try:
            # Check for a valid date
            if date:
                date = datetime.date.fromisoformat(date)

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

        return super().list(request, *args, **kwargs)