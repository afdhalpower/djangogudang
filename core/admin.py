from django.contrib import admin
from .models import ActivityLog

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ["created_at", "user", "action", "details"]
    list_filter = ["created_at", "user"]
    search_fields = ["action", "details", "user__username"]
    readonly_fields = ["created_at"]
