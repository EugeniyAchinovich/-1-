import pytz
from django.utils import timezone
from datetime import datetime


def get_current_dates(user_timezone_str):
    """
    Получает текущие даты для UTC и заданной тайм-зоны пользователя.

    :param user_timezone_str: Строка с тайм-зоной пользователя
    :return: Словарь с текущими датами
    """
    # Получение текущего времени в UTC
    utc_now = timezone.now()

    # Получение тайм-зоны пользователя
    user_timezone = pytz.timezone(user_timezone_str)
    user_now = utc_now.astimezone(user_timezone)

    # Форматирование дат в нужный формат
    date_format = "%d/%m/%Y"
    current_utc_date = utc_now.strftime(date_format)
    current_user_date = user_now.strftime(date_format)

    return {
        'current_utc_date': current_utc_date,
        'current_user_date': current_user_date,
    }
