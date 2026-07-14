from django.contrib import admin
from .models import Category, Unit


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Category admin — search, filter, display."""

    list_display = ("name", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("name", "description")
    ordering = ("name",)
    # Read-only in edit form (auto-set, no need to touch)
    readonly_fields = ("created_at", "updated_at")
    # Show a nice list when editing inline
    list_per_page = 25


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ("name", "abbreviation")
    search_fields = ("name", "abbreviation")
    ordering = ("name",)
