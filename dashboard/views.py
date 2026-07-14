"""Dashboard — aggregate cards, charts, and recent activity.

Uses the existing design system: card, btn-primary, emerald accent."""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F, Q
from django.utils import timezone
from django.views.generic import TemplateView
from products.models import Product
from stock.models import StockTransaction, StockTransactionItem


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

        context.update(
            total_products=total_products,
            low_stock=low_stock,
            inactive_products=inactive_products,
            stock_in_today=stock_in_today,
            stock_out_today=stock_out_today,
            low_stock_products=low_stock_products,
            recent_transactions=recent_transactions,
        )
        return context
