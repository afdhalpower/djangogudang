"""Catalog models: Category, Unit (and later Product).

MENTOR NOTE (Laravel -> Django):
- Django's `Model` = Eloquent Model
- `CharField(max_length=...)` = `$table->string('column', length)` in Laravel migration
- `BooleanField(default=True)` = `$table->boolean('column')->default(true)`
- `DateTimeField(auto_now_add=True)` = `$table->timestamps()` (created_at only)
- `auto_now=True` = `updated_at` behavior in Laravel
- `class Meta` = `$table->...` properties (table name, ordering, etc.)
"""
from django.db import models


class Category(models.Model):
    """Product categories (e.g., Electronics, Furniture, Raw Materials).

    STATUS_CHOICES mimics an enum column — Django doesn't have a native enum
    field type, but you can use CharField with `choices`. This is equivalent
    to Laravel's `$table->enum('status', ['active','inactive'])->default('active')`.
    """
    STATUS_ACTIVE = "active"
    STATUS_INACTIVE = "inactive"
    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Active"),
        (STATUS_INACTIVE, "Inactive"),
    ]

    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Category name, e.g. 'Electronics'.",
    )
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=STATUS_ACTIVE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Unit(models.Model):
    """Unit of measurement (pcs, box, kg, liter, pack).

    This is a simple lookup table like Laravel's "settings" or "lookup" table.
    """
    name = models.CharField(max_length=50, unique=True)
    abbreviation = models.CharField(
        max_length=10,
        blank=True,
        help_text="Short form, e.g. 'pcs', 'kg'.",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.abbreviation or self.name
