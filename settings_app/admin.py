from django.contrib import admin
from .models import CompanySetting


@admin.register(CompanySetting)
class CompanySettingAdmin(admin.ModelAdmin):
    list_display = ["company_name", "warehouse_name", "default_currency", "updated_at"]
