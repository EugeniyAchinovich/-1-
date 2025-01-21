import re

from django import forms
from .models import Client


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['first_name', 'last_name', 'address', 'passport_data', 'age', 'phone']

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        phone_pattern = re.compile(r'^\+375 \(\d{2}\) \d{3}-\d{2}-\d{2}$')
        if not phone_pattern.match(phone):
            raise forms.ValidationError("Номер телефона должен быть в формате +375 (29) XXX-XX-XX")
        return phone

    def clean_age(self):
        age = self.cleaned_data.get('age')
        if age < 18:
            raise forms.ValidationError("Клиенты должны быть не моложе 18 лет")
        return age

    def clean(self):
        cleaned_data = super().clean()
        age = cleaned_data.get('age')


class ClientSearchForm(forms.Form):
    query = forms.CharField(required=True, label='Поиск по имени или фамилии')
    sort_by = forms.ChoiceField(
        choices=[
            ('first_name', 'Имя'),
            ('last_name', 'Фамилия'),
            ('age', 'Возраст'),
        ],
        label='Сортировать по',
        required=False,
    )
    sort_order = forms.ChoiceField(
        choices=[
            ('asc', 'По возрастанию'),
            ('desc', 'По убыванию'),
        ],
        label='Порядок сортировки',
        required=False,
    )
