from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase

from .forms import ClientSearchForm
from .models import Client, Service, Employee, Specialization, ServiceType
from django.urls import reverse  # Импортируйте reverse для динамического построения URL


class ClientModelTests(TestCase):
    def test_client_age_validation(self):
        client = Client(first_name='Маша', last_name='Петрова', age=15)
        with self.assertRaises(ValidationError):
            client.full_clean()


class ServiceModelTests(TestCase):
    def setUp(self):
        self.service_type = ServiceType.objects.create(name='Мастера')
        self.service = Service.objects.create(
            name='Ремонт АКПП',
            price=400.00,
            service_type=self.service_type
        )

    def test_service_str(self):
        self.assertEqual(str(self.service), 'Ремонт АКПП')


class EmployeeModelTests(TestCase):
    def setUp(self):
        self.specialization = Specialization.objects.create(name='Слесарь')
        self.employee = Employee.objects.create(
            first_name='Сергей',
            last_name='Алексеев',
            age=30,  # Возраст больше 18
            specialization=self.specialization
        )

    def test_employee_age_validation(self):
        with self.assertRaises(ValidationError):
            Employee.objects.create(
                first_name='Лена',
                last_name='Семенова',
                age=16,  # Возраст меньше 18
                specialization=self.specialization
            )


class ClientSearchFormTests(TestCase):
    def test_valid_form(self):
        form_data = {'query': 'Иван', 'sort_by': 'first_name', 'sort_order': 'asc'}
        form = ClientSearchForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        # Параметры с пустым обязательным полем
        form_data = {
            'query': '',   # Обязательное поле пустое
            'sort_by': None,
            'sort_order': None
        }
        form = ClientSearchForm(data=form_data)
        self.assertFalse(form.is_valid())  # Ожидаем, что форма окажется недействительной


class ClientListViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_superuser(
            username='testuser',
            email='test@example.com',
            password='password123',
        )
        cls.client_instance = Client.objects.create(
            first_name="Александр",
            last_name="Петров",
            address="Улица Мира, 1",
            passport_data="AB123456",
            age=30,
            phone="+375 (29) 123-45-67"
        )

    def setUp(self):
        self.client.login(username='testuser', password='password123')  # Логин перед выполнением тестов

    def test_search_functionality(self):
        response = self.client.get('/clients/')  # укажите правильный URL
        self.assertContains(response, 'Александр')

    def test_view_url(self):
        response = self.client.get(reverse('client_list_view'))
        self.assertEqual(response.status_code, 200)

    def test_view_renders_correct_template(self):
        response = self.client.get(reverse('client_list_view'))
        self.assertTemplateUsed(response, 'client_list_view.html')

    def test_sorting(self):
        response = self.client.get(reverse('client_list_view'), {'sort_by': 'age', 'sort_order': 'asc'})
        self.assertEqual(response.status_code, 200)

