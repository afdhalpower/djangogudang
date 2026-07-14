from django import forms
from .models import Product


class ProductForm(forms.ModelForm):
    """
    ModelForm for Product. Handles FK relationship fields as dropdowns
    (Django auto-renders ModelChoiceField for ForeignKey fields).

    MENTOR NOTE: Django's ModelForm reads the model's field types and picks
    the right widget automatically. ForeignKey → <select>. ImageField →
    file input. No manual field mapping needed — unlike Laravel where you
    manually specify $casts and validation rules.
    """
    class Meta:
        model = Product
        fields = [
            "sku", "barcode", "name", "description",
            "category", "unit", "supplier",
            "purchase_price", "selling_price",
            "current_stock", "minimum_stock",
            "image", "status",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }
        help_texts = {
            "current_stock": "Initial stock quantity. After creation, stock is managed via Stock In/Out transactions.",
        }
