"""
Product model — the core entity of the warehouse system.
"""
from django.db import models
from django.urls import reverse
from decimal import Decimal
from categories.models import Category
from units.models import Unit
from suppliers.models import Supplier


def product_image_path(instance, filename):
    """
    Store uploads in media/products/<sku>/<filename>.
    """
    return f"products/{instance.sku}/{filename}"


class Product(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
    ]

    # Core identity
    sku = models.CharField(
        max_length=50, unique=True, db_index=True,
        verbose_name="SKU",
        help_text="Stock Keeping Unit — unique product code",
    )
    barcode = models.CharField(
        max_length=100, blank=True, db_index=True,
        verbose_name="Barcode",
    )
    name = models.CharField(max_length=300, db_index=True)
    description = models.TextField(blank=True)

    # Relationships
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT,
        related_name="products",
        verbose_name="Category",
    )
    unit = models.ForeignKey(
        Unit, on_delete=models.PROTECT,
        related_name="products",
        verbose_name="Unit",
    )
    supplier = models.ForeignKey(
        Supplier, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="products",
        verbose_name="Supplier",
    )

    # Pricing
    purchase_price = models.DecimalField(
        max_digits=14, decimal_places=2, default=0,
        verbose_name="Purchase Price",
    )
    selling_price = models.DecimalField(
        max_digits=14, decimal_places=2, default=0,
        verbose_name="Selling Price",
    )

    # Stock
    current_stock = models.PositiveIntegerField(default=0, verbose_name="Current Stock")
    minimum_stock = models.PositiveIntegerField(default=0, verbose_name="Minimum Stock")

    # File upload
    image = models.ImageField(
        upload_to=product_image_path, blank=True,
        verbose_name="Product Image",
    )

    # Status & timestamps
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Products"
        indexes = [
            models.Index(fields=["name", "sku", "barcode"]),
        ]

    def __str__(self):
        return f"{self.sku} — {self.name}"

    def get_absolute_url(self):
        return reverse("products:detail", kwargs={"pk": self.pk})

    # --- Business helpers --------------------------------------------------

    @property
    def is_low_stock(self):
        """True when stock drops below or equal to minimum."""
        return self.current_stock <= self.minimum_stock

    @property
    def profit_margin(self):
        """Gross profit per unit."""
        if self.purchase_price > 0:
            return self.selling_price - self.purchase_price
        return Decimal("0.00")

    @property
    def profit_margin_percent(self):
        if self.purchase_price > 0:
            return round((self.selling_price - self.purchase_price)
                         / self.purchase_price * 100, 1)
        return Decimal("0.0")
