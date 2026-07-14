"""
Category model — used by Products (ForeignKey) to group inventory.

MENTOR NOTE (Laravel -> Django):
- A Django Model is like an Eloquent Model + Schema definition in one.
  You don't write separate migrations for the schema — you declare fields
  here, then `python manage.py makemigrations` generates the migration file.
- `auto_now_add=True` is like `$table->timestamps()` for `created_at` only.
- `Meta: ordering` sets the default ORDER BY, like `Model::defaultOrderBy()`.
- `class Meta` replaces Eloquent's `$table`, `$fillable`, etc.
- `__str__` is equivalent to Laravel's `__toString()` / implicit model casting.
"""
from django.db import models
from django.urls import reverse  # reverse('categories:update', pk=1) -> /categories/1/edit/


class Category(models.Model):
    STATUS_ACTIVE = "active"
    STATUS_INACTIVE = "inactive"
    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Active"),
        (STATUS_INACTIVE, "Inactive"),
    ]

    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        """
        Like Laravel's `route('categories.show', $this)`.
        Django uses `reverse()` for URL generation from view names.
        """
        return reverse("categories:detail", kwargs={"pk": self.pk})
