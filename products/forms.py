from django import forms
from .models import Product


class ProductForm(forms.ModelForm):
    """
    ModelForm for Product.
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["current_stock"].disabled = True
            self.fields["current_stock"].help_text = "Stock is managed exclusively via transactions."
