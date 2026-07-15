"""Dashboard — aggregate cards, charts, and recent activity.

Uses the existing design system: card, btn-primary, emerald accent."""
from collections import defaultdict
from datetime import timedelta

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F, Q
from django.utils import timezone
from django.views.generic import TemplateView
from products.models import Product
from stock.models import StockTransaction, StockTransactionItem
from django.utils.translation import gettext_lazy as _


class DashboardHomeView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # --- Aggregate stats ---
        total_products = Product.objects.count()
        low_stock = Product.objects.filter(current_stock__lte=F("minimum_stock")).count()
        inactive_products = Product.objects.filter(status="inactive").count()

        today = timezone.localdate()
        stock_in_today = StockTransaction.objects.filter(
            movement_type="in", date=today
        ).count()
        stock_out_today = StockTransaction.objects.filter(
            movement_type="out", date=today
        ).count()

        # Top 5 low-stock products
        low_stock_products = Product.objects.filter(
            current_stock__lte=F("minimum_stock")
        ).select_related("category", "unit")[:5]

        # Recent transactions (last 5)
        recent_transactions = StockTransaction.objects.select_related(
            "created_by"
        ).prefetch_related("items", "items__product")[:5]

        # --- Chart 1: Stock movement trend (last 14 days) ---
        from django.db.models import Count
        last_14 = [today - timedelta(days=i) for i in range(13, -1, -1)]
        tx_by_day = defaultdict(lambda: {"in": 0, "out": 0, "adjustment": 0})
        txs = (
            StockTransaction.objects.filter(date__gte=last_14[0])
            .values("date", "movement_type")
            .annotate(count=Count("id"))
        )
        for t in txs:
            d = t["date"]
            if d in last_14:
                tx_by_day[d][t["movement_type"]] = t["count"]
        trend_labels = [d.strftime("%d %b") for d in last_14]
        trend_in = [tx_by_day[d]["in"] for d in last_14]
        trend_out = [tx_by_day[d]["out"] for d in last_14]
        trend_adj = [tx_by_day[d]["adjustment"] for d in last_14]

        # --- Chart 2: Stock health distribution (pie) ---
        healthy = Product.objects.filter(
            current_stock__gt=F("minimum_stock"), status="active"
        ).count()
        low = Product.objects.filter(
            current_stock__lte=F("minimum_stock"), status="active"
        ).count()
        inactive = Product.objects.filter(status="inactive").count()
        health_labels = ["Healthy", "Low Stock", "Inactive"]
        health_data = [healthy, low, inactive]

        context.update(
            total_products=total_products,
            low_stock=low_stock,
            inactive_products=inactive_products,
            stock_in_today=stock_in_today,
            stock_out_today=stock_out_today,
            low_stock_products=low_stock_products,
            recent_transactions=recent_transactions,
            chart=dict(
                trend_labels=trend_labels,
                trend_in=trend_in,
                trend_out=trend_out,
                trend_adj=trend_adj,
                health=[
                    {"label": _("Healthy"), "value": healthy, "color": "#059669"},
                    {"label": _("Low Stock"), "value": low, "color": "#dc2626"},
                    {"label": _("Inactive"), "value": inactive, "color": "#94a3b8"},
                ],
            ),
        )
        return context
