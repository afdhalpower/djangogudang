from django.contrib import admin
from .models import CompanySetting


@admin.register(CompanySetting)
class CompanySettingAdmin(admin.ModelAdmin):
    list_display = ("company_name", "warehouse_name", "currency", "updated_at")
    fieldsets = (
        ("Company Profile", {
            "fields": ("company_name", "address", "phone", "email", "tax_id", "logo"),
        }),
        ("Warehouse", {
            "fields": ("warehouse_name", "warehouse_address"),
        }),
        ("System", {
            "fields": ("currency", "low_stock_threshold"),
        }),
    )
