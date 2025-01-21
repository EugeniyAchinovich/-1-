import re

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
import logging

logger = logging.getLogger('myapp')


class Client(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    address = models.CharField(max_length=255)
    passport_data = models.CharField(max_length=100)
    age = models.IntegerField(default=18)
    phone = models.CharField(max_length=20, default="+375 (29) XXX-XX-XX")

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def clean(self):
        if self.age < 18:
            raise ValidationError("Клиенты должны быть не моложе 18 лет.")
        if not re.match(r'^\+375 \(\d{2}\) \d{3}-\d{2}-\d{2}$', self.phone):
            raise ValidationError("Номер телефона должен быть в формате +375 (XX) XXX-XX-XX.")

    def save(self, *args, **kwargs):
        if self.pk:  # Обновление существующего клиента
            logger.info(f'Updated client: {self.name}')
        else:  # Создание нового клиента
            logger.info(f'Created new client: {self.name}')
        super().save(*args, **kwargs)

        self.phone = self.format_phone(self.phone)
        self.clean()
        super(Client, self).save(*args, **kwargs)

    def format_phone(self, phone):
        cleaned_phone = re.sub(r'[^\d+]', '', phone)

        if len(cleaned_phone) == 12:  # +375291234567 -> +375 (29) 123-45-67
            return f"+375 (29) {cleaned_phone[4:7]}-{cleaned_phone[7:9]}-{cleaned_phone[9:11]}"
        return phone.strip()

    def delete(self, *args, **kwargs):
        logger.warning(f'Deleted client: {self.name}')
        super().delete(*args, **kwargs)


class ServiceType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name


class Service(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    service_type = models.ForeignKey(ServiceType, on_delete=models.CASCADE, related_name='services')

    def __str__(self):
        return self.name


class Order(models.Model):
    order_number = models.CharField(max_length=20)
    date_created = models.DateField(auto_now_add=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='orders')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, default=1)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"Order {self.order_number} by {self.client}"


class Appointment(models.Model):
    client = models.ForeignKey('Client', on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    stylist = models.ForeignKey(User, related_name='appointments', on_delete=models.CASCADE)
    date_time = models.DateTimeField()

    def total_cost(self):
        return self.service.cost

    def __str__(self):
        return f'{self.client} - {self.service} at {self.date_time}'


class Employee(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    specialization = models.ForeignKey('Specialization', on_delete=models.CASCADE, related_name='employees')
    age = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.specialization}"

    def clean(self):
        if self.age < 18:
            raise ValidationError("Сотрудники должны быть не моложе 18 лет")

    def save(self, *args, **kwargs):
        self.clean()
        super(Employee, self).save(*args, **kwargs)


class Specialization(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class SparePart(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    part_type = models.ForeignKey('PartType', on_delete=models.CASCADE, related_name='spare_parts')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name


class PartType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class RepairDevice(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class RepairDeviceType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

