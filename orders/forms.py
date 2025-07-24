# orders/forms.py
# ---------------
from django import forms
from .models import Order

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['title', 'preamble', 'group_name']
        
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'preamble': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
            'group_name': forms.TextInput(attrs={'class': 'form-control'}),
        }
        
        labels = {
            'title': '2. Заголовок приказа',
            'preamble': '3. Преамбула (основание для приказа)',
            'group_name': '4. Название группы (если применимо)',
        }