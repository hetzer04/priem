# students/admin.py
# -----------------
from django.contrib import admin
from .models import Student

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'iin', 'specialty', 'qualification', 'study_form', 'payment_type')
    list_filter = ('specialty', 'qualification', 'study_form', 'payment_type')
    search_fields = ('full_name', 'iin')