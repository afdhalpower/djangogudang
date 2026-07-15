from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = ("username", "email", "first_name", "last_name", "role", "is_staff", "is_active")
    list_filter = ("role", "is_staff", "is_active", "groups")
    search_fields = ("username", "email", "first_name", "last_name")
    ordering = ("username",)
    # Fields shown on the "change user" page, grouped into fieldsets.
    fieldsets = UserAdmin.fieldsets + (
        ("Warehouse Info", {"fields": ("role", "phone")}),
    )
    # Fields shown on the "add user" page
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Warehouse Info", {"fields": ("role", "phone")}),
    )
