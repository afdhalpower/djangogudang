"""
Unit model — measurement units for Products (pcs, box, kg, liter, pack...).

MENTOR NOTE: This is a classic "lookup table" in Django — simple, shared,
referenced by ForeignKey from Product. The structure is nearly identical to
Category, which reinforces the DRY pattern of CBV + ModelForm.
"""
from django.db import models
from django.urls import reverse


class Unit(models.Model):
    STATUS_ACTIVE = "active"
    STATUS_INACTIVE = "inactive"
    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Active"),
        (STATUS_INACTIVE, "Inactive"),
    ]

    name = models.CharField(max_length=100, unique=True, help_text="Full name e.g. 'Kilogram'")
    abbreviation = models.CharField(max_length=20, unique=True, help_text="Short form e.g. 'kg', 'pcs'")
    description = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Units"

    def __str__(self):
        return f"{self.abbreviation} ({self.name})"

    def get_absolute_url(self):
        return reverse("units:detail", kwargs={"pk": self.pk})
