from django.shortcuts import render
from .utils.time_utils import get_current_dates
from .utils.calendar_utils import get_current_month_calendar


def timezone_view(request):
    user_timezone_str = 'Europe/Moscow'

    dates = get_current_dates(user_timezone_str)
    current_utc_date = dates['current_utc_date']
    current_user_date = dates['current_user_date']

    calendar_text = get_current_month_calendar()

    context = {
        'current_utc_date': current_utc_date,
        'current_user_date': current_user_date,
        'calendar_text': calendar_text,
    }

    return render(request, 'timezone.html', context)
