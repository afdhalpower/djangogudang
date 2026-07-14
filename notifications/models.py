from django.db import models
from django.conf import settings


class Notification(models.Model):
    """System notification — low stock warnings, alerts.

    MENTOR NOTE: This is a simple notification model, akin to Laravel's
    database notifications channel. No real-time push — users see alerts
    on page load via the topbar badge and dashboard widget.
    """
    TYPE_CHOICES = [
        ("low_stock", "Low Stock"),
        ("system", "System"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True, blank=True,
        help_text="Target user. Null = broadcast to all staff.",
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(
        max_length=20, choices=TYPE_CHOICES, default="system",
    )
    is_read = models.BooleanField(default=False)
    link = models.CharField(
        max_length=500, blank=True,
        help_text="Optional URL to navigate to when clicked.",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "is_read"]),
            models.Index(fields=["is_read"]),
        ]

    def __str__(self):
        return f"[{self.get_notification_type_display()}] {self.title}"
