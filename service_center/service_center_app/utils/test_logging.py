import logging
from django.http import HttpResponse

# Получаем логгер
logger = logging.getLogger('myapp')


def my_view(request):
    logger.info('Accessed my_view function.')

    return HttpResponse('Hello, world!')
