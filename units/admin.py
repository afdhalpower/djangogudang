from django.contrib import admin
from .models import Unit


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ("name", "abbreviation", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("name", "abbreviation")
    ordering = ("name",)
