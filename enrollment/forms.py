# enrollment/forms.py

from django import forms
from django.core.exceptions import ValidationError
from .models import Applicant, Qualification

class ApplicantForm(forms.ModelForm):
    class Meta:
        model = Applicant
        fields = [
            'full_name', 'iin', 'specialty', 'qualification', 'quotas',
            'study_form', 'base_education', 'school', 'graduation_year',
            'with_honors', 'gpa', 'birth_date', 'study_language',
            'citizenship', 'nationality', 'gender', 'phone_number', 'home_address',
            'parents_info', 'has_incomplete_docs', 'needs_dormitory',
            'application_date', 'photo', 'is_ready_for_enrollment',
            'payment_type', 'payment_status'
        ]
        widgets = {
            'application_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'birth_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
            'with_honors': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'has_incomplete_docs': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'needs_dormitory': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_ready_for_enrollment': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'specialty': forms.Select(attrs={'class': 'form-select'}),
            'qualification': forms.Select(attrs={'class': 'form-select'}),
            'study_form': forms.Select(attrs={'class': 'form-select'}),
            'base_education': forms.Select(attrs={'class': 'form-select'}),
            'payment_type': forms.Select(attrs={'class': 'form-select'}),
            'payment_status': forms.Select(attrs={'class': 'form-select'}),
            'parents_info': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
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
            'quotas': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # --- НАЧАЛО ИСПРАВЛЕНИЯ ---

        # 1. Готовим данные для JavaScript
        qualifications_data = {}
        all_qualifications = Qualification.objects.select_related('specialty').all()
        for qual in all_qualifications:
            if qual.specialty_id not in qualifications_data:
                qualifications_data[qual.specialty_id] = []
            qualifications_data[qual.specialty_id].append({'id': qual.id, 'name': qual.name})
        
        # Сохраняем как JSON-строку, чтобы легко передать в шаблон
        self.qualification_choices_for_js = json.dumps(qualifications_data)

        # 2. Устанавливаем queryset для поля 'qualification' для корректной валидации на сервере
        # и отображения уже выбранного значения при редактировании.
        if self.instance and self.instance.pk and self.instance.specialty:
            self.fields['qualification'].queryset = Qualification.objects.filter(specialty=self.instance.specialty)
        elif 'specialty' in self.data and self.data.get('specialty'):
            try:
                specialty_id = int(self.data.get('specialty'))
                self.fields['qualification'].queryset = Qualification.objects.filter(specialty_id=specialty_id)
            except (ValueError, TypeError):
                self.fields['qualification'].queryset = Qualification.objects.none()
        else:
             self.fields['qualification'].queryset = Qualification.objects.none()

        # --- КОНЕЦ ИСПРАВЛЕНИЯ ---
        
        # Логика для квот остается без изменений
        if self.instance and self.instance.pk and self.instance.social_status:
            self.fields['quotas'].label = f"Квоты (старый статус: {self.instance.social_status})"
            self.fields['quotas'].help_text = "Внимание! Выберите новые квоты из списка. После сохранения старый статус будет очищен."

    def clean(self):
        cleaned_data = super().clean()
        specialty = cleaned_data.get("specialty")
        qualification = cleaned_data.get("qualification")

        if specialty and qualification:
            if qualification.specialty != specialty:
                self.add_error('qualification', "Выбранная квалификация не соответствует выбранной специальности.")
        
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if instance.pk and instance.social_status:
            instance.social_status = ""
        if commit:
            instance.save()
            self.save_m2m()
        return instance