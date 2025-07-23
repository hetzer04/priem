from django import forms
from django.core.exceptions import ValidationError
from .models import Applicant, Qualification, Order



class ApplicantForm(forms.ModelForm):
    class Meta:
        model = Applicant
        fields = '__all__'
        
        # Определяем виджеты для красивого отображения и добавляем Bootstrap классы
        widgets = {
            'application_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'birth_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
            
            # Логические поля (галочки)
            'with_honors': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'has_incomplete_docs': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'needs_dormitory': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_ready_for_enrollment': forms.CheckboxInput(attrs={'class': 'form-check-input'}),

            # Поля с выбором
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'specialty': forms.Select(attrs={'class': 'form-select'}),
            'qualification': forms.Select(attrs={'class': 'form-select'}),
            'study_form': forms.Select(attrs={'class': 'form-select'}),
            'base_education': forms.Select(attrs={'class': 'form-select'}),
            'payment_type': forms.Select(attrs={'class': 'form-select'}),
            'payment_status': forms.Select(attrs={'class': 'form-select'}),

            # Многострочные поля
            'parents_info': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),

            # Все остальные текстовые поля
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'iin': forms.TextInput(attrs={'class': 'form-control'}),
            'nationality': forms.TextInput(attrs={'class': 'form-control'}),
            'citizenship': forms.TextInput(attrs={'class': 'form-control'}),
            'study_language': forms.TextInput(attrs={'class': 'form-control'}),
            'school': forms.TextInput(attrs={'class': 'form-control'}),
            'graduation_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'gpa': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'home_address': forms.TextInput(attrs={'class': 'form-control'}),
            'social_status': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['qualification'].queryset = Qualification.objects.all()
        
        if self.instance and self.instance.pk:
            self.fields['qualification'].queryset = Qualification.objects.filter(specialty=self.instance.specialty).order_by('name')

        if 'specialty' in self.data:
            try:
                specialty_id = int(self.data.get('specialty'))
                self.fields['qualification'].queryset = Qualification.objects.filter(specialty_id=specialty_id).order_by('name')
            except (ValueError, TypeError):
                if not self.instance.pk:
                     self.fields['qualification'].queryset = Qualification.objects.none()

    # ДОБАВЛЯЕМ МЕТОД ДЛЯ ВАЛИДАЦИИ
    def clean(self):
        cleaned_data = super().clean()
        specialty = cleaned_data.get("specialty")
        qualification = cleaned_data.get("qualification")

        if specialty and qualification:
            # Проверяем, что выбранная квалификация действительно принадлежит выбранной специальности
            if qualification.specialty != specialty:
                raise ValidationError(
                    "Выбранная квалификация не соответствует выбранной специальности. Пожалуйста, выберите корректную квалификацию."
                )
        return cleaned_data

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        # Включаем все новые поля
        fields = ['title', 'preamble', 'group_name']
        
        # Добавляем виджеты и стили Bootstrap
        widgets = {
            'order_type': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'preamble': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
            'group_name': forms.TextInput(attrs={'class': 'form-control'}),
        }
        
        # Указываем понятные названия для полей
        labels = {
            'order_type': '1. Тип приказа',
            'title': '2. Заголовок приказа',
            'preamble': '3. Преамбула (основание для приказа)',
            'group_name': '4. Название группы (если применимо)',
        }