# students/forms.py
# -----------------
from django import forms
from .models import Student
from handbooks.models import Qualification # Импортируем для динамической фильтрации

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        exclude = ['movement_history', 'created_at']
        widgets = {
            'application_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'birth_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
            'with_honors': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'has_incomplete_docs': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'needs_dormitory': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            # ... и другие виджеты, как были раньше ...
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk and self.instance.specialty:
            self.fields['qualification'].queryset = Qualification.objects.filter(specialty=self.instance.specialty).order_by('name')
        else:
            self.fields['qualification'].queryset = Qualification.objects.none()