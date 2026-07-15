"""
Stock views — Stock In, Stock Out, and Stock Adjustment with line items.
Includes batch/expiry tracking and FEFO (First Expired First Out) logic.
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
from decimal import Decimal, InvalidOperation
from .models import StockTransaction, StockTransactionItem, ProductBatch
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
        prices = self.request.POST.getlist("unit_price")

        # Handle list size mismatch or empty submission
        if not products_ids or not quantities:
            messages.error(self.request, "Please add at least one product item.")
            return redirect(self.request.path)

        # Match prices list length with product_ids
        if not prices:
            prices = ["0"] * len(products_ids)
        elif len(prices) < len(products_ids):
            prices = list(prices) + ["0"] * (len(products_ids) - len(prices))

        # Batch/expiry fields (only relevant for Stock In)
        batch_numbers = self.request.POST.getlist("batch_number")
        expiry_dates = self.request.POST.getlist("expiry_date")

        rows = []
        for i, (pid, qty, price) in enumerate(zip(products_ids, quantities, prices)):
            if not pid:
                continue
            
            # Ensure product ID is valid integer
            if not pid.isdigit():
                messages.error(self.request, f"Invalid Product ID at line {i+1}.")
                return redirect(self.request.path)
            
            # Ensure quantity is positive integer
            if not qty:
                continue
            try:
                qty_val = int(qty)
                if qty_val <= 0:
                    messages.error(self.request, f"Quantity must be greater than 0 at line {i+1}.")
                    return redirect(self.request.path)
            except ValueError:
                messages.error(self.request, f"Quantity must be an integer at line {i+1}.")
                return redirect(self.request.path)

            # Ensure unit price is valid non-negative decimal
            try:
                price_val = Decimal(price or "0")
                if price_val < 0:
                    messages.error(self.request, f"Unit price cannot be negative at line {i+1}.")
                    return redirect(self.request.path)
            except InvalidOperation:
                messages.error(self.request, f"Invalid unit price format at line {i+1}.")
                return redirect(self.request.path)

            try:
                product = Product.objects.get(pk=int(pid))
                if product.status != "active":
                    messages.error(self.request, f"Product {product.name} is inactive and cannot be used in transactions.")
                    return redirect(self.request.path)
            except Product.DoesNotExist:
                messages.error(self.request, f"Product ID {pid} does not exist.")
                return redirect(self.request.path)

            # Collect batch info if provided
            batch_num = batch_numbers[i].strip() if i < len(batch_numbers) else ""
            expiry_str = expiry_dates[i].strip() if i < len(expiry_dates) else ""

            rows.append((int(pid), qty_val, price_val, batch_num, expiry_str))

        if not rows:
            messages.error(self.request, "Please add at least one product item.")
            return redirect(self.request.path)

        try:
            with db_transaction.atomic():
                transaction = form.save(commit=False)
                transaction.movement_type = self.movement_type
                transaction.created_by = self.request.user
                transaction.save()

                for pid, qty, price, batch_num, expiry_str in rows:
                    batch_obj = None

                    if self.movement_type == StockTransaction.MOVEMENT_IN and batch_num:
                        # Parse expiry date if provided
                        expiry_date = None
                        if expiry_str:
                            from datetime import datetime
                            try:
                                expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d").date()
                            except ValueError:
                                pass  # Silently skip invalid dates

                        # Get or create the batch
                        batch_obj, _created = ProductBatch.objects.get_or_create(
                            product_id=pid,
                            batch_number=batch_num,
                            defaults={"expiry_date": expiry_date},
                        )
                        # If batch already exists but expiry was updated
                        if not _created and expiry_date and not batch_obj.expiry_date:
                            batch_obj.expiry_date = expiry_date
                            batch_obj.save(update_fields=["expiry_date"])

                    elif self.movement_type == StockTransaction.MOVEMENT_OUT:
                        # FEFO: auto-pick the batch with earliest expiry that has stock
                        batch_obj = self._fefo_pick_batch(pid, qty)

                    StockTransactionItem.objects.create(
                        transaction=transaction,
                        product_id=pid,
                        quantity=qty,
                        unit_price=price,
                        batch=batch_obj,
                    )

                from core.utils import log_activity
                log_activity(
                    self.request.user,
                    f"Recorded {transaction.get_movement_type_display()}",
                    f"Ref: {transaction.reference_number}, items: {len(rows)}"
                )

        except ValidationError as e:
            messages.error(self.request, ", ".join(e.messages))
            return redirect(self.request.path)

        messages.success(self.request, self.success_message)
        return redirect(transaction.get_absolute_url())

    def _fefo_pick_batch(self, product_id, qty):
        """
        FEFO (First Expired First Out): Find the batch with the earliest
        expiry date that still has remaining stock for this product.
        Returns a ProductBatch or None if no batches exist.
        """
        # Order: expiry_date ASC (NULL last), then created_at ASC
        from django.db.models import F
        batch = (
            ProductBatch.objects
            .filter(product_id=product_id, current_stock__gt=0)
            .order_by(
                # Batches with expiry_date come first (NULLS LAST)
                F("expiry_date").asc(nulls_last=True),
                "created_at",
            )
            .first()
        )
        return batch

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
            "items", "items__product", "items__product__unit", "items__batch"
        )
