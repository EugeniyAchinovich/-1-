from django.contrib import admin
from .models import (Client, Service, ServiceType, Order, Employee,
                     Specialization, SparePart, PartType, RepairDevice, RepairDeviceType, Appointment)


# Inline для редактирования сотрудников для специализаций
class EmployeeInline(admin.TabularInline):
    model = Employee
    extra = 1  # Количество пустых форм для добавления новых сотрудников


# Админ класса для специализаций
class SpecializationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')  # Поля для отображения в списке
    search_fields = ('name',)  # Поля для поиска
    inlines = [EmployeeInline]  # Встроенный список для сотрудников


# Админ класса для типов сервиса
class ServiceTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')  # Поля для отображения в списке
    search_fields = ('name',)  # Поля для поиска


# Админ класса для клиентов
class ClientAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'phone', 'address', 'age')
    fields = ('first_name', 'last_name', 'address', 'passport_data', 'age', 'phone')

    def save_model(self, request, obj, form, change):
        obj.clean()  # Валидация
        super().save_model(request, obj, form, change)


# Inline для редактирования заказов для сотрудников
class OrderInline(admin.TabularInline):
    model = Order
    extra = 1


class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'specialization')
    search_fields = ('first_name', 'last_name')
    list_filter = ('specialization',)

    def save_model(self, request, obj, form, change):
        obj.clean()  # Вызываем метод очистки перед сохранением
        super().save_model(request, obj, form, change)


# Админ класса для сервисов
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'service_type')
    search_fields = ('name',)  # Поля для поиска


# Админ класса для заказов
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'order_number', 'date_created')
    search_fields = ('order_number',)


# Inline для редактирования запасных частей
class SparePartInline(admin.TabularInline):
    model = SparePart
    extra = 1


# Админ класса для объектов запчастей
class PartTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    inlines = [SparePartInline]


# Админ класса для ремонта устройств
class RepairDeviceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


# Админ класса для типов устройств
class RepairDeviceTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


admin.site.register(Client, ClientAdmin)
admin.site.register(Appointment)
admin.site.register(Service, ServiceAdmin)  # Регистрация сервиса через ServiceAdmin
admin.site.register(ServiceType, ServiceTypeAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Specialization, SpecializationAdmin)
admin.site.register(SparePart)  # Регистрация запасных частей
admin.site.register(PartType, PartTypeAdmin)
admin.site.register(RepairDevice, RepairDeviceAdmin)
admin.site.register(RepairDeviceType, RepairDeviceTypeAdmin)
