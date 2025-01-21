import pytz
import requests
from django.core.exceptions import ValidationError

from django.shortcuts import render, redirect, get_object_or_404
from .models import Client, Service, Order, Employee, SparePart, PartType, RepairDevice, RepairDeviceType, \
    ServiceType, Specialization, Appointment
from django.contrib.auth.decorators import login_required, user_passes_test
from .utils.time_utils import get_current_dates
from googleapiclient.discovery import build
from django.conf import settings
from .forms import ClientForm, ClientSearchForm
from django.db.models import Count
from django.db import models


import logging
from django.shortcuts import render
from django.http import HttpResponse
from .models import Service

logger = logging.getLogger('service_center')


@login_required
def add_client_view(request):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/home')
    else:
        form = ClientForm()
    return render(request, 'forms/add_client.html', {'form': form})


def news_view(request):
    query = request.GET.get('query', '')
    articles = get_latest_news(query)

    return render(request, 'api/news.html', {
        'articles': articles,
        'query': query
    })


def get_latest_news(query=None):
    url = f'https://newsapi.org/v2/top-headlines'
    params = {
        'apiKey': settings.NEWS_API_KEY,
        'country': 'us',  #
    }

    if query:
        params['q'] = query

    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json().get('articles', [])
    else:
        return []


def youtube_search(query, max_results=5):
    youtube = build('youtube', 'v3', developerKey=settings.YOUTUBE_API_KEY)

    request = youtube.search().list(
        q=query,
        part='snippet',
        maxResults=max_results
    )

    response = request.execute()
    return response['items']


def youtube_view(request):
    query = request.GET.get('query', '')
    videos = []

    if query:
        videos = youtube_search(query)

    return render(request, 'api/youtube.html', {
        'videos': videos,
        'query': query
    })


def group_required(group_name):
    """Декоратор для проверки принадлежности пользователя к группе."""

    def in_group(u):
        return u.is_authenticated and u.groups.filter(name=group_name).exists()

    return user_passes_test(in_group)


@group_required('ShopOwners')
def owner_dashboard(request):
    return render(request, 'dashboards/owner_dashboard.html')


@group_required('RegisteredUsers')
def registered_user_dashboard(request):
    return render(request, 'dashboards/registered_user_dashboard.html')


def home(request):
    # Возвращаем главную страницу только для авторизованных пользователей
    return render(request, "home.html")


def about(request):
    return render(request, "about.html")


@login_required
def user_dashboard(request):
    return render(request, 'dashboards/user_dashboard.html')


@login_required
def index(request):
    if request.user.is_superuser:
        return render(request, 'dashboards/superuser_dashboard.html')  # Шаблон для суперпользователя
    elif request.user.groups.filter(name='ShopOwners').exists():
        return render(request, 'dashboards/owner_dashboard.html')  # Шаблон для владельцев магазина
    elif request.user.groups.filter(name='RegisteredUsers').exists():
        return render(request, 'dashboards/registered_user_dashboard.html')  # Шаблон для зарегистрированных
    else:
        return render(request, 'dashboards/guest_home.html')  # Шаблон для незарегистрированных пользователей


@login_required
def stylist_dashboard(request):
    appointments = Appointment.objects.filter(stylist=request.user)
    total_cost = sum(appointment.total_cost() for appointment in appointments)
    return render(request, 'dashboards/worker_dashboard.html', {'appointments': appointments,
                                                                 'total_cost': total_cost})


# CRUD операции
@login_required
def client_list(request):
    clients = Client.objects.all()
    return render(request, "lists/client_list.html", {"clients": clients})


@login_required
def client_create(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        address = request.POST.get("address")
        passport_data = request.POST.get("passport_data")
        client = Client(first_name=first_name, last_name=last_name, address=address, passport_data=passport_data)
        client.save()
        return redirect("lists/client_list")  # Переход на страницу со списком клиентов
    return render(request, "forms/client_form.html")


@login_required
def client_edit(request, id):
    client = get_object_or_404(Client, id=id)
    if request.method == "POST":
        client.first_name = request.POST.get("first_name")
        client.last_name = request.POST.get("last_name")
        client.address = request.POST.get("address")
        client.passport_data = request.POST.get("passport_data")
        client.save()
        return redirect("lists/client_list")  # Переход на страницу со списком клиентов
    return render(request, "forms/client_form.html", {"client": client})



@login_required
def client_delete(request, id):
    client = get_object_or_404(Client, id=id)
    client.delete()
    return redirect("lists/client_list")  # Переход на страницу со списком клиентов


@login_required
def service_type_list(request):
    service_types = ServiceType.objects.all()
    return render(request, "lists/service_type_list.html", {"service_types": service_types})


@login_required
def service_type_create(request):
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        service_type = ServiceType(name=name, description=description)
        service_type.save()
        return redirect("lists/service_type_list")
    return render(request, "forms/service_type_form.html")

@login_required
def service_type_edit(request, id):
    service_type = get_object_or_404(ServiceType, id=id)
    if request.method == "POST":
        service_type.name = request.POST.get("name")
        service_type.description = request.POST.get("description")
        service_type.save()
        return redirect("lists/service_type_list")
    return render(request, "forms/service_type_form.html", {"service_type": service_type})


@login_required
def service_type_delete(request, id):
    service_type = get_object_or_404(ServiceType, id=id)
    service_type.delete()
    return redirect("lists/service_type_list")


def service_list(request):
    services = Service.objects.all()
    service_types = ServiceType.objects.all()  # Получаем все типы услуг

    filter_price = request.GET.get('price')
    filter_type = request.GET.get('service_type')

    if filter_price:
        services = services.filter(price__lte=filter_price)

    if filter_type:
        services = services.filter(service_type__name=filter_type)

    try:
        services = Service.objects.all()
        logger.info('Accessed the service list view.')
        return render(request, 'lists/service_list.html', {
            'services': services,
            'service_types': service_types
        })
    except Exception as e:
        logger.error(f'Error accessing service list: {e}')
        return HttpResponse('Error occurred', status=500)


def available_services(request):
    services = Service.objects.all()
    service_types = ServiceType.objects.all()

    if 'price' in request.GET:
        price = request.GET['price']
        services = services.filter(price__lte=price)

    if 'service_type' in request.GET:
        service_type_id = request.GET['service_type']
        services = services.filter(service_type_id=service_type_id)

    return render(request, 'lists/available_services.html', {
        'services': services,
        'service_types': service_types
    })


@login_required
def service_create(request):
    if request.method == "POST":
        name = request.POST.get("name")
        price = request.POST.get("price")
        service_type_id = request.POST.get("service_type_id")
        service_type = get_object_or_404(ServiceType, id=service_type_id)
        service = Service(name=name, price=price, service_type=service_type)
        service.save()
        return redirect("lists/service_list")
    service_types = ServiceType.objects.all()  # Получаем ServiceType для выбора в форме
    return render(request, "forms/service_form.html", {"service_types": service_types})


@login_required
def service_edit(request, id):
    service = get_object_or_404(Service, id=id)
    if request.method == "POST":
        service.name = request.POST.get("name")
        service.price = request.POST.get("price")
        service.service_type = get_object_or_404(ServiceType, id=request.POST.get("service_type_id"))
        service.save()
        return redirect("lists/service_list")
    service_types = ServiceType.objects.all()  # Получаем ServiceType для выбора в форме
    return render(request, "forms/service_form.html", {"service": service, "service_types": service_types})


@login_required
def service_delete(request, id):
    service = get_object_or_404(Service, id=id)
    service.delete()
    return redirect("lists/service_list")


@login_required
def order_list(request):
    orders = Order.objects.all()
    return render(request, "lists/order_list.html", {"orders": orders})


@login_required
def order_create(request):
    if request.method == "POST":
        order_number = request.POST.get("order_number")
        client_id = request.POST.get("client_id")
        client = get_object_or_404(Client, id=client_id)
        order = Order(order_number=order_number, client=client)
        order.save()

        services = request.POST.getlist("services")  # Получение списка выбранных услуг
        order.service.set(services)  # Связываем услуги с заказом
        return redirect("lists/order_list")

    clients = Client.objects.all()
    services = Service.objects.all()
    return render(request, "forms/order_form.html", {"clients": clients, "services": services})


@login_required
def order_edit(request, id):
    order = get_object_or_404(Order, id=id)
    if request.method == "POST":
        order.order_number = request.POST.get("order_number")
        order.client = get_object_or_404(Client, id=request.POST.get("client_id"))
        order.save()

        services = request.POST.getlist("services")
        order.service.set(services)
        return redirect("lists/order_list")

    clients = Client.objects.all()
    services = Service.objects.all()
    return render(request, "forms/order_form.html", {"order": order, "clients": clients, "services": services})


@login_required
def order_delete(request, id):
    order = get_object_or_404(Order, id=id)
    order.delete()
    return redirect("lists/order_list")


@login_required
def employee_list(request):
    employees = Employee.objects.all()
    return render(request, "lists/employee_list.html", {"employees": employees})


@login_required
def employee_create(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        specialization_id = request.POST.get("specialization_id")
        specialization = get_object_or_404(Specialization, id=specialization_id)
        employee = Employee(first_name=first_name, last_name=last_name, specialization=specialization)
        employee.save()
        return redirect("lists/employee_list")

    specializations = Specialization.objects.all()
    return render(request, "forms/add_employee.html", {"specializations": specializations})


@login_required
def employee_edit(request, id):
    employee = get_object_or_404(Employee, id=id)
    if request.method == "POST":
        employee.first_name = request.POST.get("first_name")
        employee.last_name = request.POST.get("last_name")
        employee.specialization = get_object_or_404(Specialization, id=request.POST.get("specialization_id"))
        employee.save()
        return redirect("lists/employee_list")

    specializations = Specialization.objects.all()
    return render(request, "forms/add_employee.html", {"employee": employee, "specializations": specializations})


@login_required
def employee_delete(request, id):
    employee = get_object_or_404(Employee, id=id)
    employee.delete()
    return redirect("lists/employee_list")


@login_required
def specialization_list(request):
    specializations = Specialization.objects.all()
    return render(request, "lists/specialization_list.html", {"specializations": specializations})


@login_required
def specialization_create(request):
    if request.method == "POST":
        name = request.POST.get("name")
        specialization = Specialization(name=name)
        specialization.save()
        return redirect("lists/specialization_list")
    return render(request, "forms/specialization_form.html")


@login_required
def specialization_edit(request, id):
    specialization = get_object_or_404(Specialization, id=id)
    if request.method == "POST":
        specialization.name = request.POST.get("name")
        specialization.save()
        return redirect("lists/specialization_list")
    return render(request, "forms/specialization_form.html", {"specialization": specialization})


@login_required
def specialization_delete(request, id):
    specialization = get_object_or_404(Specialization, id=id)
    specialization.delete()
    return redirect("lists/specialization_list")


@login_required
def spare_parts_view(request):
    user_timezone_str = 'Europe/Minsk'

    spare_parts = SparePart.objects.all()

    dates = get_current_dates(user_timezone_str)
    current_utc_date = dates['current_utc_date']
    current_user_date = dates['current_user_date']

    spare_parts_data = []
    for part in spare_parts:
        utc_created_at = part.created_at.strftime("%d/%m/%Y")
        utc_updated_at = part.updated_at.strftime("%d/%m/%Y")

        user_timezone = pytz.timezone(user_timezone_str)
        created_at_user = part.created_at.astimezone(user_timezone).strftime("%d/%m/%Y")
        updated_at_user = part.updated_at.astimezone(user_timezone).strftime("%d/%m/%Y")

        spare_parts_data.append({
            'name': part.name,
            'price': part.price,
            'utc_created_at': utc_created_at,
            'utc_updated_at': utc_updated_at,
            'user_created_at': created_at_user,
            'user_updated_at': updated_at_user,
        })

    context = {
        'spare_parts': spare_parts_data,
        'current_utc_date': current_utc_date,
        'current_user_date': current_user_date,
    }

    return render(request, 'spare_parts.html', context)


@login_required
def dashboard_view(request):
    # Age Distribution
    age_distribution = Client.objects.values('age').annotate(count=Count('id')).order_by('age')
    age_labels = [str(entry['age']) for entry in age_distribution]
    age_counts = [entry['count'] for entry in age_distribution]

    # Service Type Distribution
    service_distribution = ServiceType.objects.annotate(count=Count('services')).order_by('-count')
    service_labels = [service.name for service in service_distribution]
    service_counts = [service.count for service in service_distribution]

    # Order Count Over Time
    order_counts = Order.objects.values('date_created').annotate(count=Count('id')).order_by('date_created')
    order_dates = [entry['date_created'].strftime('%Y-%m-%d') for entry in order_counts]
    order_counts_values = [entry['count'] for entry in order_counts]

    context = {
        'age_labels': age_labels,
        'age_counts': age_counts,
        'service_labels': service_labels,
        'service_counts': service_counts,
        'order_dates': order_dates,
        'order_counts': order_counts_values,
    }

    return render(request, 'dashboard.html', context)


@login_required
def client_list_view(request):
    # Обработка формы поиска
    form = ClientSearchForm(request.GET)
    clients = Client.objects.all()

    if form.is_valid():
        # Поиск по имени или фамилии
        query = form.cleaned_data.get('query')
        if query:
            clients = clients.filter(
                models.Q(first_name__icontains=query) | models.Q(last_name__icontains=query)
            )

        # Сортировка
        sort_by = form.cleaned_data.get('sort_by')
        sort_order = form.cleaned_data.get('sort_order')
        if sort_by and sort_order:
            if sort_order == 'asc':
                clients = clients.order_by(sort_by)
            else:
                clients = clients.order_by('-' + sort_by)

    context = {
        'form': form,
        'clients': clients,
    }

    return render(request, 'client_list_view.html', context)


# Список назначений
@login_required
def appointment_list_view(request):
    appointments = Appointment.objects.all()
    context = {
        'appointments': appointments
    }
    return render(request, 'lists/appointment_list.html', context)


# Добавление назначения
@login_required
def add_appointment_view(request):
    if request.method == 'POST':
        client_id = request.POST.get('client_id')
        service_id = request.POST.get('service_id')
        stylist_id = request.POST.get('stylist_id')
        date_time = request.POST.get('date_time')

        # Валидация и сохранение
        try:
            appointment = Appointment(
                client_id=client_id,
                service_id=service_id,
                stylist_id=stylist_id,
                date_time=date_time
            )
            appointment.save()
            return redirect('lists/appointment_list')  # Перенаправление на список
        except ValidationError as e:
            return render(request, 'forms/add_appointment.html', {'error': e.message})

    services = Service.objects.all()
    context = {
        'services': services,
        # Здесь можно добавить список клиентов и стилистов.
    }
    return render(request, 'forms/add_appointment.html', context)


# Список типов запчастей
@login_required
def parttype_list_view(request):
    parttypes = PartType.objects.all()
    context = {
        'parttypes': parttypes
    }
    return render(request, 'lists/parttype_list.html', context)


# Добавление типа запчасти
@login_required
def add_parttype_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        parttype = PartType(name=name)
        parttype.save()
        return redirect('lists/parttype_list')  # Перенаправление на список типо запчастей

    return render(request, 'forms/add_parttype.html')


# Список доступных услуг
def available_services_view(request):
    available_services = Service.objects.all()
    context = {
        'services': available_services
    }
    return render(request, 'lists/available_services.html', context)
