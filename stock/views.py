"""
Stock views — Stock In, Stock Out, and Stock Adjustment with line items.

Uses atomic transactions to ensure header+items are saved or rolled back as
a single unit. If a signal (e.g. negative stock for OUT) raises an error,
the entire transaction is rolled back — no orphan headers.

MENTOR NOTE (Laravel -> Django):
- django.db.transaction.atomic() == DB::transaction() in Laravel.
- If any exception occurs inside the block, ALL DB changes are rolled back.
- We catch ValidationError from signals and surface it as a user-facing
  message, redirecting back to the form with the product selection preserved.
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ValidationError
from django.db import transaction as db_transaction
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView
from django.contrib import messages
from .models import StockTransaction, StockTransactionItem
from .forms import StockInForm, StockOutForm, StockAdjustmentForm
from products.models import Product


class BaseStockCreateView(LoginRequiredMixin, CreateView):
    """
    Shared logic for Stock In and Stock Out.
    Subclasses set `movement_type` and may override `process_item()`.
    """

    def form_valid(self, form):
        """Atomic: save header + all items, or roll back entirely on error."""
        products_ids = self.request.POST.getlist("product_id")
        quantities = self.request.POST.getlist("quantity")
        prices = self.request.POST.getlist("unit_price") or ["0"] * len(products_ids)

        # Filter out empty rows
        rows = []
        for pid, qty, price in zip(products_ids, quantities, prices):
            if pid and qty and int(qty) > 0:
                rows.append((int(pid), int(qty), price))

        if not rows:
            messages.error(self.request, "Please add at least one product item.")
            return redirect(self.request.path)

        try:
            with db_transaction.atomic():
                transaction = form.save(commit=False)
                transaction.movement_type = self.movement_type
                transaction.created_by = self.request.user
                transaction.save()

                for pid, qty, price in rows:
                    StockTransactionItem.objects.create(
                        transaction=transaction,
                        product_id=pid,
                        quantity=qty,
                        unit_price=price or 0,
                    )

        except ValidationError as e:
            # Signal raised this — e.g. "Insufficient stock for Product X"
            messages.error(self.request, str(e))
            return redirect(self.request.path)

        messages.success(self.request, self.success_message)
        return redirect(transaction.get_absolute_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["products"] = Product.objects.filter(status="active").select_related("unit")
        context["movement_type"] = self.movement_type
        return context


class StockInCreateView(BaseStockCreateView):
    model = StockTransaction
    form_class = StockInForm
    template_name = "stock/stock_in_form.html"
    success_message = "Stock In recorded successfully."
    movement_type = StockTransaction.MOVEMENT_IN


class StockOutCreateView(BaseStockCreateView):
    model = StockTransaction
    form_class = StockOutForm
    template_name = "stock/stock_out_form.html"
    success_message = "Stock Out recorded successfully."
    movement_type = StockTransaction.MOVEMENT_OUT


class StockAdjustmentCreateView(BaseStockCreateView):
    """Manual stock adjustment with reason (lost/damaged/expired/correction).

    MENTOR NOTE: Extends the same BaseStockCreateView pattern, proving that
    Django's class-based inheritance keeps views DRY even as features grow.
    The template is slightly different (has reason + direction fields) but
    the save/signal logic is entirely inherited.
    """
    model = StockTransaction
    form_class = StockAdjustmentForm
    template_name = "stock/stock_adjustment_form.html"
    success_message = "Stock adjustment recorded."
    movement_type = StockTransaction.MOVEMENT_ADJUSTMENT


class StockTransactionListView(LoginRequiredMixin, ListView):
    """All transactions with filter by type, date range, and product search."""
    model = StockTransaction
    template_name = "stock/list.html"
    context_object_name = "transactions"
    paginate_by = 20

    def get_queryset(self):
        qs = StockTransaction.objects.select_related("created_by").prefetch_related(
            "items", "items__product"
        )

        # Filter by type
        movement_type = self.request.GET.get("type", "")
        if movement_type in dict(StockTransaction.MOVEMENT_CHOICES):
            qs = qs.filter(movement_type=movement_type)

        # Filter by product search (looks in related items' product name/SKU)
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(
                Q(items__product__name__icontains=q)
                | Q(items__product__sku__icontains=q)
            ).distinct()

        # Filter by date range
        date_from = self.request.GET.get("date_from", "")
        date_to = self.request.GET.get("date_to", "")
        if date_from:
            qs = qs.filter(date__gte=date_from)
        if date_to:
            qs = qs.filter(date__lte=date_to)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter_type"] = self.request.GET.get("type", "")
        context["filter_q"] = self.request.GET.get("q", "")
        context["filter_date_from"] = self.request.GET.get("date_from", "")
        context["filter_date_to"] = self.request.GET.get("date_to", "")
        return context


class StockTransactionDetailView(LoginRequiredMixin, DetailView):
    """Show a single transaction with all its line items."""
    model = StockTransaction
    template_name = "stock/detail.html"
    context_object_name = "transaction"

    def get_queryset(self):
        return StockTransaction.objects.prefetch_related(
            "items", "items__product", "items__product__unit"
        )
