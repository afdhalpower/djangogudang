"""
Reports — Inventory, Low Stock, Stock Card, and CSV export.

Architecture decision: pure function-based views (not CBV) because:
1. Each report has unique logic (query, chart data, export variants)
2. Function views allow returning different response types (HTML vs CSV)
3. Easier to compose shared logic (e.g. export_csv helper)

MENTOR NOTE: Django supports both function views and class-based views.
Use CBV for CRUD (where the pattern is the same), use function views for
pages where the logic is unique (reports, dashboards, exports).
"""
import csv
from io import StringIO
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from django.db.models import F, Sum, Q, Count
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.views.generic import TemplateView, ListView, DetailView
from products.models import Product
from stock.models import StockTransaction, StockTransactionItem
from suppliers.models import Supplier


# ─── Helpers ───────────────────────────────────────────────────

def _csv_response(filename: str, header: list, rows: list) -> HttpResponse:
    """Return an HttpResponse with CSV content (Content-Type + download headers)."""
    buf = StringIO()
    writer = csv.writer(buf)
    writer.writerow(header)
    writer.writerows(rows)
    response = HttpResponse(buf.getvalue(), content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="{filename}.csv"'
    return response


def _format_rp(val):
    """Format number to IDR string without symbol (for CSV numbers)."""
    if val is None:
        return 0
    return int(val)


# ─── Inventory Report ──────────────────────────────────────────

class InventoryReportView(LoginRequiredMixin, TemplateView):
    """
    Full product inventory table: current stock, minimum, status,
    purchase/selling price, and total inventory value.

    MENTOR NOTE: TemplateView with context data is perfect for reports —
    no form handling needed, just query and render.
    """
    template_name = "reports/inventory.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        products = Product.objects.select_related("category", "unit", "supplier").all()

        # Totals
        total_inventory_value = sum(
            (p.current_stock * p.purchase_price) for p in products
        )
        total_selling_value = sum(
            (p.current_stock * p.selling_price) for p in products
        )
        total_items = products.count()
        low_stock_count = products.filter(current_stock__lte=F("minimum_stock")).count()

        products_list = []
        for p in products:
            products_list.append({
                "product": p,
                "inventory_value": p.current_stock * p.purchase_price,
            })

        context.update(
            products=products_list,
            total_inventory_value=total_inventory_value,
            total_selling_value=total_selling_value,
            total_items=total_items,
            low_stock_count=low_stock_count,
        )
        return context


@login_required
def inventory_csv(request):
    """Export Inventory Report as CSV."""
    products = Product.objects.select_related("category", "unit", "supplier").all()
    rows = []
    for p in products:
        rows.append([
            p.sku, p.name, p.category.name if p.category else "",
            p.unit.abbreviation if p.unit else "",
            p.current_stock, p.minimum_stock,
            p.supplier.company_name if p.supplier else "",
            _format_rp(p.purchase_price),
            _format_rp(p.selling_price),
            _format_rp(p.current_stock * p.purchase_price),
            p.status,
        ])
    return _csv_response(
        "inventory_report",
        ["SKU", "Name", "Category", "Unit", "Stock", "Min", "Supplier",
         "Purchase Price", "Selling Price", "Inventory Value", "Status"],
        rows,
    )


# ─── Low Stock Report ──────────────────────────────────────────

class LowStockReportView(LoginRequiredMixin, TemplateView):
    """All products where current_stock <= minimum_stock."""
    template_name = "reports/low_stock.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        products = Product.objects.filter(
            current_stock__lte=F("minimum_stock")
        ).select_related("category", "unit", "supplier").order_by("current_stock")
        context["products"] = products
        context["count"] = products.count()
        return context


@login_required
def low_stock_csv(request):
    """Export Low Stock Report as CSV."""
    products = Product.objects.filter(
        current_stock__lte=F("minimum_stock")
    ).select_related("category", "unit", "supplier").order_by("current_stock")
    rows = []
    for p in products:
        rows.append([
            p.sku, p.name, p.category.name if p.category else "",
            p.unit.abbreviation if p.unit else "",
            p.current_stock, p.minimum_stock,
            p.supplier.company_name if p.supplier else "",
            _format_rp(p.purchase_price),
            _format_rp(p.selling_price),
            p.status,
        ])
    return _csv_response(
        "low_stock_report",
        ["SKU", "Name", "Category", "Unit", "Stock", "Min", "Supplier",
         "Purchase Price", "Selling Price", "Status"],
        rows,
    )


# ─── Stock Card ────────────────────────────────────────────────

class StockCardView(LoginRequiredMixin, TemplateView):
    """
    Per-product movement history — shows every IN/OUT/ADJUSTMENT
    that affected this product's stock.

    Like a bank statement for inventory.
    """
    template_name = "reports/stock_card.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product_id = self.request.GET.get("product", "")
        date_from = self.request.GET.get("date_from", "")
        date_to = self.request.GET.get("date_to", "")

        products = Product.objects.filter(status="active").select_related("unit")
        context["products"] = products

        if product_id:
            product = get_object_or_404(Product, pk=int(product_id))
            context["selected_product"] = product

            items = StockTransactionItem.objects.filter(
                product=product
            ).select_related("transaction", "product__unit").order_by(
                "-transaction__date", "-transaction__created_at"
            )

            if date_from:
                items = items.filter(transaction__date__gte=date_from)
            if date_to:
                items = items.filter(transaction__date__lte=date_to)

            context["items"] = items
            # Running balance starts from initial seed minus any transaction-based
            # For accuracy, we calculate from DB
            context["date_from"] = date_from
            context["date_to"] = date_to

        return context


@login_required
def stock_card_csv(request):
    """Export Stock Card for a specific product as CSV."""
    product_id = request.GET.get("product", "")
    if not product_id:
        return HttpResponse("Select a product first", status=400)

    product = get_object_or_404(Product, pk=int(product_id))
    items = StockTransactionItem.objects.filter(
        product=product
    ).select_related("transaction").order_by("transaction__date")

    # Running balance
    balance = product.current_stock
    # We'll calculate backward from current stock
    # Simple approach: just show movement type and qty
    rows = []
    for item in items:
        movement = item.transaction.movement_type
        direction = item.transaction.adjustment_direction if movement == "adjustment" else ""
        rows.append([
            item.transaction.date,
            item.transaction.reference_number or "",
            movement.upper(),
            direction,
            item.quantity,
            _format_rp(item.unit_price),
        ])

    return _csv_response(
        f"stock_card_{product.sku}",
        ["Date", "Reference", "Type", "Direction", "Qty", "Unit Price"],
        rows,
    )
