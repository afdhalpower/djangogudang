from django.contrib import admin
from .models import Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "status", "created_at", "updated_at")
    list_filter = ("status", "created_at")
    search_fields = ("name", "description")
    ordering = ("name",)
    list_per_page = 25
