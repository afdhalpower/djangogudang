"""
Stock transaction models — track every stock movement (IN, OUT, ADJUSTMENT).
Includes batch/expiry tracking for FEFO (First Expired First Out) support.
"""
from django.db import models, transaction
from django.urls import reverse
from products.models import Product
from suppliers.models import Supplier


class ProductBatch(models.Model):
    """
    Tracks inventory at the batch level — each batch has a unique combination
    of product + batch_number.  Expiry date is optional but recommended for
    perishable / regulated goods.
    """
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE,
        related_name="batches",
        help_text="The product this batch belongs to",
    )
    batch_number = models.CharField(
        max_length=100,
        help_text="Batch / lot number (e.g. LOT-2025-001)",
    )
    expiry_date = models.DateField(
        null=True, blank=True,
        help_text="Expiry / best-before date (leave blank if not applicable)",
    )
    current_stock = models.PositiveIntegerField(
        default=0,
        help_text="Current remaining stock in this batch",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["expiry_date", "created_at"]
        verbose_name = "Product Batch"
        verbose_name_plural = "Product Batches"
        unique_together = [("product", "batch_number")]
        indexes = [
            models.Index(fields=["product", "expiry_date"]),
        ]

    def __str__(self):
        exp = self.expiry_date.strftime("%d/%m/%Y") if self.expiry_date else "No Expiry"
        return f"{self.product.sku} | {self.batch_number} (Exp: {exp}, Stk: {self.current_stock})"

    @property
    def is_expired(self):
        """True when the batch has passed its expiry date."""
        from django.utils import timezone
        if not self.expiry_date:
            return False
        return self.expiry_date < timezone.localdate()

    @property
    def days_until_expiry(self):
        """Number of days until expiry. Negative means already expired."""
        from django.utils import timezone
        if not self.expiry_date:
            return None
        return (self.expiry_date - timezone.localdate()).days


class StockTransaction(models.Model):
    """
    A receipt or dispatch document — one transaction = multiple line items.
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
    One transaction can have many items.
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
    # Optional batch link — used when batch tracking is enabled for the product
    batch = models.ForeignKey(
        ProductBatch, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="transaction_items",
        help_text="Batch this item was taken from / added to",
    )

    class Meta:
        verbose_name = "Stock Transaction Item"
        verbose_name_plural = "Stock Transaction Items"

    def __str__(self):
        batch_info = f" [{self.batch.batch_number}]" if self.batch else ""
        return f"{self.product.sku} x{self.quantity}{batch_info}"
