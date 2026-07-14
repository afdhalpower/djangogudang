from django.contrib import admin
from .models import Supplier


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("company_name", "contact_person", "phone", "email", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("company_name", "contact_person", "phone", "email")
    ordering = ("company_name",)
