# handbooks/forms.py
# ------------------
from django import forms
from .models import Specialty, Qualification
from .models import Quota

class SpecialtyForm(forms.ModelForm):
    class Meta:
        model = Specialty
        fields = ['code', 'name']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }

class QualificationForm(forms.ModelForm):
    class Meta:
        model = Qualification
        fields = ['specialty', 'code', 'name', 'is_worker_qualification']
        widgets = {
            'specialty': forms.Select(attrs={'class': 'form-select'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'is_worker_qualification': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class QuotaForm(forms.ModelForm):
    class Meta:
        model = Quota
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }