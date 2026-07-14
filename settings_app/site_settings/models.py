from django.db import models
from django.core.validators import MinValueValidator


class CompanySetting(models.Model):
    """Singleton model — company profile and warehouse settings.

    MENTOR NOTE: Singleton pattern in Django: restrict to one row via
    a SingleObjectMixin + pk=1 pattern in the view, enforced with
    get_or_create / hasattr checks. There's no native SingletonField,
    so we just write views that always edit pk=1.

    Fields:
      - company_name, address, phone, email, tax_id
      - logo (image upload)
      - warehouse_name, warehouse_address
      - currency (default: IDR)
      - low_stock_threshold (for global alerts, default: 10)
    """
    company_name = models.CharField(max_length=200, default="My Warehouse")
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    tax_id = models.CharField("Tax ID / NPWP", max_length=30, blank=True)
    logo = models.ImageField(
        upload_to="company/", blank=True,
        help_text="Company logo (will appear on reports)",
    )

    # Warehouse info
    warehouse_name = models.CharField(max_length=200, default="Main Warehouse")
    warehouse_address = models.TextField(blank=True)

    # System defaults
    currency = models.CharField(max_length=10, default="IDR")
    low_stock_threshold = models.PositiveIntegerField(
        default=10,
        validators=[MinValueValidator(1)],
        help_text="Default notification threshold (units) — overrides product minimum_stock",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Company Setting"

    def __str__(self):
        return self.company_name

    @classmethod
    def get_settings(cls):
        """Return the single settings row, creating it if needed."""
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
