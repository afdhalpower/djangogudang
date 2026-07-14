"""
Notification — low stock alert triggered by dashboard middleware/view.

MENTOR NOTE: Notifications are read-only computed data (no DB model needed).
We generate them on-the-fly from product stock queries. This matches
Django's "thin model, fat query" philosophy — no need to store what you
can compute.

For a real system you'd add:
- A Notification model with is_read, created_at
- Django channels / WebSocket for push
- Email/SMS/Telegram integration
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F
from django.shortcuts import render
from django.views.generic import TemplateView
from products.models import Product
from suppliers.models import Supplier


class NotificationListView(LoginRequiredMixin, TemplateView):
    """All low-stock notifications for the current user."""
    template_name = "notifications/list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Low stock products
        low_stock = Product.objects.filter(
            current_stock__lte=F("minimum_stock")
        ).select_related("category", "unit", "supplier").order_by("current_stock")

        # Only items where stock is critically low (<= 50% of minimum)
        critical = Product.objects.filter(
            current_stock__lte=F("minimum_stock") * 0.5
        ).count()

        # Group by shortage severity
        shortages = []
        for p in low_stock:
            shortage = max(0, p.minimum_stock - p.current_stock)
            severity = "critical" if shortage >= p.minimum_stock * 0.5 else "warning"
            shortages.append({
                "product": p,
                "shortage": shortage,
                "severity": severity,
            })

        context.update(
            shortages=shortages,
            total_low_stock=low_stock.count(),
            critical_count=critical,
        )
        return context
