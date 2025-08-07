# enrollment/filters.py

import django_filters
from django import forms
from django.db.models import Q
from .models import Applicant, Quota, Specialty, Qualification

class ApplicantFilter(django_filters.FilterSet):
    """
    Фильтр для абитуриентов с возможностью поиска по всем ключевым полям.
    """
    # 1. Универсальное поле для поиска по ФИО и ИИН
    search = django_filters.CharFilter(
        method='search_filter',
        label='ФИО или ИИН'
    )

    # 2. Фильтр для ManyToMany поля 'quotas' с поддержкой множественного выбора
    quotas = django_filters.ModelMultipleChoiceFilter(
        field_name='quotas',
        queryset=Quota.objects.all(),
        label='Квоты',
        widget=forms.SelectMultiple # Этот виджет будет улучшен с помощью Tom Select
    )

    # 3. Фильтр по полям с выбором, чтобы явно указать модель
    specialty = django_filters.ModelChoiceFilter(
        queryset=Specialty.objects.all(),
        label="Специальность"
    )

    qualification = django_filters.ModelChoiceFilter(
        queryset=Qualification.objects.all(),
        label="Квалификация"
    )

    def __init__(self, *args, **kwargs):
        super(ApplicantFilter, self).__init__(*args, **kwargs)
        # Автоматически добавляем классы Bootstrap ко всем полям формы
        for field_name, field in self.form.fields.items():
            # Для поля 'search' и других текстовых полей
            if isinstance(field, forms.CharField):
                 field.widget.attrs.update({'class': 'form-control', 'placeholder': 'Поиск...'})
            # Для полей с выбором
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': 'form-select'})
            # Для чекбоксов
            elif isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-check-input'})


    class Meta:
        model = Applicant
        # 4. Явно перечисляем все поля, по которым можно фильтровать
        fields = [
            'search',
            'specialty',
            'qualification',
            'study_form',
            'base_education',
            'study_language',
            'payment_type',
            'payment_status',
            'gender',
            'with_honors',
            'has_incomplete_docs',
            'needs_dormitory',
            'is_ready_for_enrollment',
            'quotas',
        ]

    def search_filter(self, queryset, name, value):
        """
        Метод для поиска по нескольким полям: ФИО и ИИН.
        """
        if not value:
            return queryset
        return queryset.filter(
            Q(full_name__icontains=value) | Q(iin__icontains=value)
        )