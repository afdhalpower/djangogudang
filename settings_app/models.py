from django.db import models
from django.core.validators import MinValueValidator


class CompanySetting(models.Model):
    """Single-instance model for company & warehouse configuration.

    MENTOR NOTE (Laravel → Django):
    This is Django's version of a single-row settings table — vs Laravel
    where you'd typically stash config in config/*.php or a settings
    JSON column. Django's ORM makes single-row models easy with
    get_or_create() and get_first() patterns.
    """
    # Company info
    company_name = models.CharField(max_length=255, default="My Warehouse")
    tax_id = models.CharField("Tax ID / NPWP", max_length=50, blank=True, default="")
    address = models.TextField(blank=True, default="")
    phone = models.CharField(max_length=30, blank=True, default="")
    email = models.EmailField(blank=True, default="")
    website = models.URLField(blank=True, default="")

    # Warehouse info
    warehouse_name = models.CharField(max_length=255, default="Main Warehouse")
    warehouse_location = models.CharField(max_length=255, blank=True, default="")
    warehouse_code = models.CharField(max_length=20, blank=True, default="WH-01")

    # Defaults
    default_currency = models.CharField(max_length=10, default="IDR")
    low_stock_threshold = models.PositiveIntegerField(
        "Low Stock Alert Threshold",
        default=10,
        validators=[MinValueValidator(1)],
        help_text="Global minimum stock notification threshold",
    )
    enable_low_stock_alert = models.BooleanField("Enable Low Stock Alerts", default=True)
    enable_low_stock_email = models.BooleanField("Email Alerts", default=False,
                                                  help_text="Send email when stock is low")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Company Setting"
        verbose_name_plural = "Company Settings"

    def __str__(self):
        return self.company_name

    def save(self, *args, **kwargs):
        # Enforce single-instance: always update the first row
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        """Get or create the singleton settings row."""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
