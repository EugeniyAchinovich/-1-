from django.urls import path
from . import views
from .views import *
from .statistics_view import *
from .timezone_view import *
from .chart_view import *
from .views import client_list_view


urlpatterns = [
    path("", home, name="home"),

    path("home/", home, name="home"),  # Главная страница
    path("about/", about, name="about"),  # Страница "О нас"

    path('m-dashboard/', stylist_dashboard, name='stylist_dashboard'),

    path('available-services/', available_services, name='available_services'),

    path("clients/", views.client_list, name="client_list"),
    path("clients/create/", views.client_create, name="client_create"),
    path("clients/edit/<int:id>/", views.client_edit, name="client_edit"),
    path("clients/delete/<int:id>/", views.client_delete, name="client_delete"),

    path("service-types/", service_type_list, name="service_type_list"),
    path("service-types/create/", service_type_create, name="service_type_create"),
    path("service-types/edit/<int:id>/", service_type_edit, name="service_type_edit"),
    path("service-types/delete/<int:id>/", service_type_delete, name="service_type_delete"),

    path("services/", service_list, name="service_list"),
    path("services/create/", service_create, name="service_create"),
    path("services/edit/<int:id>/", service_edit, name="service_edit"),
    path("services/delete/<int:id>/", service_delete, name="service_delete"),

    path("orders/", order_list, name="order_list"),
    path("orders/create/", order_create, name="order_create"),
    path("orders/edit/<int:id>/", order_edit, name="order_edit"),
    path("orders/delete/<int:id>/", order_delete, name="order_delete"),

    path("employees/", views.employee_list, name="employee_list"),
    path("employees/add", views.employee_list, name="add_employee"),
    path("employees/create/", views.employee_create, name="employee_create"),
    path("employees/edit/<int:id>/", views.employee_edit, name="employee_edit"),
    path("employees/delete/<int:id>/", views.employee_delete, name="employee_delete"),

    path("specializations/", views.specialization_list, name="specialization_list"),
    path("specializations/create/", views.specialization_create, name="specialization_create"),
    path("specializations/edit/<int:id>/", views.specialization_edit, name="specialization_edit"),
    path("specializations/delete/<int:id>/", views.specialization_delete, name="specialization_delete"),

    path('appointments/', appointment_list_view, name='appointment_list'),
    path('appointments/add/', add_appointment_view, name='add_appointment'),
    path('parttypes/', parttype_list_view, name='parttype_list'),
    path('parttypes/add/', add_parttype_view, name='add_parttype'),
    path('available-services/', available_services_view, name='available_services'),

    path('news/', news_view, name='news_view'),
    path('youtube/', youtube_view, name='youtube_view'),

    path('statistics/', statistics_view, name='statistics_view'),
    path('timezone/', timezone_view, name='timezone_view'),
    path('chart/', chart_view, name='chart_view'),
    path('dashboard/', dashboard_view, name='dashboard_view'),

    path('spare-parts/', spare_parts_view, name='spare_parts'),
    path('add-client/', add_client_view, name='add_client'),
    path('clients-search/', client_list_view, name='client_list_view'),
]
