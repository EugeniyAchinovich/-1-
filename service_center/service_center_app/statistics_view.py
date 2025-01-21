import numpy as np
from statistics import mode, StatisticsError
from django.shortcuts import render
from django.db.models import Sum, Count
from .models import Client, Service, Order, ServiceType


def statistics_view(request):
    clients = Client.objects.all().order_by('first_name', 'last_name')
    total_sales = Order.objects.aggregate(total_cost=Sum('service__price'))['total_cost'] or 0
    sale_amounts = [(order.service.price * order.quantity) for order in Order.objects.prefetch_related('service')]

    mean_sales = np.mean(sale_amounts) if sale_amounts else 0
    median_sales = np.median(sale_amounts) if sale_amounts else 0

    try:
        mode_sales = mode(sale_amounts)
    except StatisticsError:
        mode_sales = 0  # Возврат 0, если нет моды или слишком много уникальных значений

    ages = [client.age for client in clients]
    mean_age = np.mean(ages) if ages else 0
    median_age = np.median(ages) if ages else 0

    popular_service_type = ServiceType.objects.annotate(total_services=Count('services')).order_by(
        '-total_services').first()

    profitable_service = Service.objects.annotate(total_profit=Sum('order__quantity') * Sum('price')).order_by(
        '-total_profit').first()

    context = {
        'clients': clients,
        'total_sales': total_sales,
        'mean_sales': mean_sales,
        'median_sales': median_sales,
        'mode_sales': mode_sales,
        'mean_age': mean_age,
        'median_age': median_age,
        'popular_service_type': popular_service_type,
        'profitable_service': profitable_service,
    }

    return render(request, 'statistics.html', context)
