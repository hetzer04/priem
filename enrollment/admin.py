from django.contrib import admin
from .models import Applicant, Specialty, Qualification, Order, Student

@admin.register(Applicant)
class ApplicantAdmin(admin.ModelAdmin):
    # ИСПРАВЛЕННЫЕ СТРОКИ:
    list_display = ('full_name', 'specialty', 'qualification', 'gpa', 'study_form', 'payment_type', 'payment_status', 'needs_dormitory')
    list_filter = ('specialty', 'qualification', 'study_form', 'payment_type', 'payment_status', 'needs_dormitory', 'base_education')
    search_fields = ('full_name', 'iin')

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'specialty', 'study_form', 'payment_type')
    list_filter = ('specialty', 'study_form', 'base_education')
    search_fields = ('full_name', 'iin')