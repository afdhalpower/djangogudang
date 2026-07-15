"""Dashboard — aggregate cards, charts, and recent activity.

Uses the existing design system: card, btn-primary, emerald accent.
Now includes date-range filtering, expiring batch alerts, and fast-moving items analysis."""
from collections import defaultdict
from datetime import timedelta

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F, Q, Count, Sum, ExpressionWrapper, DecimalField
from django.utils import timezone
from django.views.generic import TemplateView
from products.models import Product
from stock.models import StockTransaction, StockTransactionItem, ProductBatch
from django.utils.translation import gettext_lazy as _


class DashboardHomeView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/home.html"

    # Allowed "days" presets
    DAYS_PRESETS = {
        "7": 7,
        "30": 30,
        "90": 90,
        "365": 365,
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        today = timezone.localdate()

        # --- Date-range filter ---
        days_param = self.request.GET.get("days", "30")
        days = self.DAYS_PRESETS.get(days_param, 30)
        date_from = today - timedelta(days=days)
        context["active_days"] = str(days)

        # --- Aggregate stats ---
        total_products = Product.objects.count()
        low_stock = Product.objects.filter(current_stock__lte=F("minimum_stock")).count()
        inactive_products = Product.objects.filter(status="inactive").count()

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

        # --- Chart 1: Stock movement trend (within selected range, max 14 labels) ---
        trend_days = min(days, 14)
        last_n = [today - timedelta(days=i) for i in range(trend_days - 1, -1, -1)]
        tx_by_day = defaultdict(lambda: {"in": 0, "out": 0, "adjustment": 0})
        txs = (
            StockTransaction.objects.filter(date__gte=last_n[0])
            .values("date", "movement_type")
            .annotate(count=Count("id"))
        )
        for t in txs:
            d = t["date"]
            if d in last_n:
                tx_by_day[d][t["movement_type"]] = t["count"]
        trend_labels = [d.strftime("%d %b") for d in last_n]
        trend_in = [tx_by_day[d]["in"] for d in last_n]
        trend_out = [tx_by_day[d]["out"] for d in last_n]
        trend_adj = [tx_by_day[d]["adjustment"] for d in last_n]

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

        # Supplier Analytics
        supplier_data = Product.objects.filter(status="active").values("supplier__company_name").annotate(
            total_items=Count("id"),
            total_value=Sum(ExpressionWrapper(F("current_stock") * F("purchase_price"), output_field=DecimalField()))
        ).order_by("-total_value")

        supplier_labels = []
        supplier_values = []
        supplier_colors = ["#10b981", "#3b82f6", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899", "#6b7280"]
        
        top_suppliers = list(supplier_data[:5])
        other_value = sum(item["total_value"] or 0 for item in supplier_data[5:])
        
        for item in top_suppliers:
            name = item["supplier__company_name"] or _("No Supplier")
            val = float(item["total_value"] or 0)
            supplier_labels.append(name)
            supplier_values.append(val)
            
        if other_value > 0:
            supplier_labels.append(str(_("Others")))
            supplier_values.append(float(other_value))

        supplier_share = []
        for i in range(len(supplier_labels)):
            supplier_share.append({
                "label": supplier_labels[i],
                "value": supplier_values[i],
                "color": supplier_colors[i]
            })

        # --- Expiring Batches (within 30 days) ---
        expiry_threshold = today + timedelta(days=30)
        expiring_batches = (
            ProductBatch.objects
            .filter(
                expiry_date__isnull=False,
                expiry_date__lte=expiry_threshold,
                current_stock__gt=0,
            )
            .select_related("product")
            .order_by("expiry_date")[:10]
        )

        # --- Top 5 Fast-Moving Items (within selected date range) ---
        top_moving_items = (
            StockTransactionItem.objects
            .filter(
                transaction__movement_type="out",
                transaction__date__gte=date_from,
            )
            .values("product__id", "product__sku", "product__name")
            .annotate(total_out=Sum("quantity"))
            .order_by("-total_out")[:5]
        )

        context.update(
            total_products=total_products,
            low_stock=low_stock,
            inactive_products=inactive_products,
            stock_in_today=stock_in_today,
            stock_out_today=stock_out_today,
            low_stock_products=low_stock_products,
            recent_transactions=recent_transactions,
            expiring_batches=expiring_batches,
            top_moving_items=top_moving_items,
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
                supplier_labels=supplier_labels,
                supplier_values=supplier_values,
                supplier_colors=supplier_colors[:len(supplier_labels)],
                supplier_share=supplier_share,
            ),
        )
        return context
