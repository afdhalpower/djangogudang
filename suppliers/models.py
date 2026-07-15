"""
Supplier model — who we buy products from.
"""
from django.db import models
from django.urls import reverse


class Supplier(models.Model):
    STATUS_ACTIVE = "active"
    STATUS_INACTIVE = "inactive"
    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Active"),
        (STATUS_INACTIVE, "Inactive"),
    ]

    company_name = models.CharField(max_length=200, unique=True)
    contact_person = models.CharField(max_length=200, blank=True, help_text="Primary contact name")
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["company_name"]
        verbose_name_plural = "Suppliers"

    def __str__(self):
        return self.company_name

    def get_absolute_url(self):
        return reverse("suppliers:detail", kwargs={"pk": self.pk})
