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

        # Filter category, unit, supplier to active-only status, keeping existing relation if editing.
        from categories.models import Category
        from units.models import Unit
        from suppliers.models import Supplier
        from django.db.models import Q

        if self.instance and self.instance.pk:
            self.fields["category"].queryset = Category.objects.filter(
                Q(status="active") | Q(pk=self.instance.category_id)
            )
            self.fields["unit"].queryset = Unit.objects.filter(
                Q(status="active") | Q(pk=self.instance.unit_id)
            )
            if self.instance.supplier_id:
                self.fields["supplier"].queryset = Supplier.objects.filter(
                    Q(status="active") | Q(pk=self.instance.supplier_id)
                )
            else:
                self.fields["supplier"].queryset = Supplier.objects.filter(status="active")
        else:
            self.fields["category"].queryset = Category.objects.filter(status="active")
            self.fields["unit"].queryset = Unit.objects.filter(status="active")
            self.fields["supplier"].queryset = Supplier.objects.filter(status="active")
