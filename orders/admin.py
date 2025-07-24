# orders/admin.py
# ---------------
from django.contrib import admin
from .models import Order

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'order_number', 'order_date', 'status', 'group_name', 'created_by', 'signed_by')
    list_filter = ('status', 'order_date')
    search_fields = ('order_number', 'group_name')
    readonly_fields = ('created_by', 'signed_by', 'created_at', 'updated_at')