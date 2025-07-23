import django_filters
from django import forms
from .models import Applicant

class ApplicantFilter(django_filters.FilterSet):
    full_name = django_filters.CharFilter(lookup_expr='icontains', label='ФИО содержит')
    
    # ДОБАВЛЯЕМ ЭТОТ МЕТОД
    def __init__(self, *args, **kwargs):
        super(ApplicantFilter, self).__init__(*args, **kwargs)
        # Проходим по всем полям формы и добавляем им классы Bootstrap
        for field_name, field in self.form.fields.items():
            if isinstance(field.widget, (forms.TextInput, forms.DateInput, forms.NumberInput)):
                field.widget.attrs.update({'class': 'form-control'})
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': 'form-select'})

    class Meta:
        model = Applicant
        fields = '__all__'
        exclude = ['created_at', 'parents_info', 'photo']


        