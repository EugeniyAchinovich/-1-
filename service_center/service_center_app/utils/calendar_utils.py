import calendar
from datetime import datetime


def get_current_month_calendar():
    """
    Генерирует текстовый календарь для текущего месяца.

    :return: Текстовый календарь на текущий месяц
    """
    now = datetime.now()
    month = now.month
    year = now.year

    return calendar.TextCalendar().formatmonth(year, month)
