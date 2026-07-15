"""
Notification — low stock alert list.
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F
from django.shortcuts import render
from django.views.generic import TemplateView
from products.models import Product
from suppliers.models import Supplier
from settings_app.models import CompanySetting


class NotificationListView(LoginRequiredMixin, TemplateView):
    """All low-stock notifications for the current user."""
    template_name = "notifications/list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        settings = CompanySetting.get_settings()
        alerts_enabled = settings.enable_low_stock_alert

        if not alerts_enabled:
            context.update(
                shortages=[],
                total_low_stock=0,
                critical_count=0,
                alerts_enabled=False,
            )
            return context

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
            alerts_enabled=True,
        )
        return context
