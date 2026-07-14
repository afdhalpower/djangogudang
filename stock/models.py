"""
Stock transaction models — track every stock movement (IN, OUT, ADJUSTMENT).

ARCHITECTURE DECISION:
We use a single model `StockTransaction` with `MOVEMENT_IN/OUT/ADJUSTMENT`
instead of separate StockIn / StockOut / StockAdjustment tables. Why?
- Single source of truth for ALL stock movement history.
- Querying "all transactions for product X" is one table scan, not UNION three.
- The `movement_type` discriminator + `quantity` sign (+/-) handles everything.
- This is the Django equivalent of a polymorphic "transactions" table.

A separate `StockTransactionItem` model holds individual line items so one
receipt (Stock In) can contain multiple products — realistic warehouse flow.

SIGNAL- vs SERVICE-LAYER debate:
Updating product.current_stock could be done via a Django signal
(post_save on StockTransactionItem) or a service method. We chose the
signal approach because:
  1. Ensures stock is ALWAYS updated when a transaction is saved (no
     calling-convention bugs).
  2. Django signals == Laravel Events/Observers. Same concept, different syntax.
  3. We add validation in the signal to PREVENT negative stock for OUT type.
For learning: this shows both signals AND model business logic.
"""
from django.db import models, transaction
from django.urls import reverse
from products.models import Product
from suppliers.models import Supplier


class StockTransaction(models.Model):
    """
    A receipt or dispatch document — one transaction = multiple line items.
    Like a purchase order (IN) or delivery note (OUT).
    """
    MOVEMENT_IN = "in"
    MOVEMENT_OUT = "out"
    MOVEMENT_ADJUSTMENT = "adjustment"
    MOVEMENT_CHOICES = [
        (MOVEMENT_IN, "Stock In"),
        (MOVEMENT_OUT, "Stock Out"),
        (MOVEMENT_ADJUSTMENT, "Adjustment"),
    ]

    movement_type = models.CharField(
        max_length=20, choices=MOVEMENT_CHOICES,
        help_text="IN = incoming stock, OUT = outgoing, ADJUSTMENT = manual correction",
    )
    date = models.DateField(auto_now_add=True, help_text="Transaction date")
    reference_number = models.CharField(
        max_length=100, blank=True,
        help_text="External reference e.g. supplier invoice / PO number",
    )
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        "accounts.User", on_delete=models.SET_NULL,
        null=True, blank=True,
        help_text="User who recorded this transaction",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Adjustment-specific fields (only used when movement_type='adjustment')
    ADJUSTMENT_REASON_CHOICES = [
        ("lost", "Lost"),
        ("damaged", "Damaged"),
        ("expired", "Expired"),
        ("correction", "Correction"),
    ]
    adjustment_reason = models.CharField(
        max_length=20,
        choices=ADJUSTMENT_REASON_CHOICES,
        blank=True,
        help_text="Reason for stock adjustment (only for adjustment type)",
    )
    # Direction of adjustment: add (+) or remove (-) stock
    ADJUSTMENT_DIRECTION_CHOICES = [
        ("add", "Add Stock (+)" ),
        ("remove", "Remove Stock (-)"),
    ]
    adjustment_direction = models.CharField(
        max_length=10,
        choices=ADJUSTMENT_DIRECTION_CHOICES,
        default="remove",
        help_text="Add or remove stock during adjustment",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Stock Transaction"
        verbose_name_plural = "Stock Transactions"

    def __str__(self):
        return f"[{self.movement_type.upper()}] {self.reference_number or 'No ref'} — {self.created_at.date()}"

    def get_absolute_url(self):
        return reverse("stock:detail", kwargs={"pk": self.pk})


class StockTransactionItem(models.Model):
    """
    Individual line item within a stock transaction.
    One transaction can have many items (like a multi-line purchase order).

    MENTOR NOTE:
    Django's ForeignKey with related_name='items' lets us do
    `transaction.items.all()` to get all line items — like Laravel's
    `$transaction->items()->get()`. The `related_query_name` is optional
    but allows `StockTransactionItem.objects.filter(transaction__pk=1)`.
    """
    transaction = models.ForeignKey(
        StockTransaction, on_delete=models.CASCADE,
        related_name="items",
    )
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT,
        related_name="stock_transactions",
    )
    quantity = models.PositiveIntegerField(help_text="Quantity of items moved")
    unit_price = models.DecimalField(
        max_digits=14, decimal_places=2, default=0,
        help_text="Price per unit for this transaction",
    )

    class Meta:
        verbose_name = "Stock Transaction Item"
        verbose_name_plural = "Stock Transaction Items"

    def __str__(self):
        return f"{self.product.sku} x{self.quantity}"
