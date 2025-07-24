from django.contrib import admin

from handbooks.models import Qualification, Specialty

# Register your models here.
@admin.register(Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Qualification)
class QualificationAdmin(admin.ModelAdmin):
    list_display = ('name', 'specialty')
    list_filter = ('specialty',)
    search_fields = ('name',)