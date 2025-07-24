from django.contrib import admin
from .models import Applicant, Specialty, Qualification, Order, Student

@admin.register(Applicant)
class ApplicantAdmin(admin.ModelAdmin):
    # ИСПРАВЛЕННЫЕ СТРОКИ:
    list_display = ('full_name', 'specialty', 'qualification', 'gpa', 'study_form', 'payment_type', 'payment_status', 'needs_dormitory')
    list_filter = ('specialty', 'qualification', 'study_form', 'payment_type', 'payment_status', 'needs_dormitory', 'base_education')
    search_fields = ('full_name', 'iin')



@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Настройка отображения приказов в админ-панели."""
    list_display = ('order_number', 'order_date', 'status', 'group_name', 'created_by', 'signed_by')
    list_filter = ('status', 'created_by', 'order_date')
    search_fields = ('order_number', 'group_name')
    readonly_fields = ('created_by', 'signed_by', 'created_at', 'updated_at')

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'specialty', 'study_form', 'payment_type')
    list_filter = ('specialty', 'study_form', 'base_education')
    search_fields = ('full_name', 'iin')