from django import forms
from .models import StockTransaction, StockTransactionItem
from products.models import Product


class StockTransactionItemForm(forms.ModelForm):
    """
    Form for a single line item. Used inline within the main transaction form.
    """
    class Meta:
        model = StockTransactionItem
        fields = ["product", "quantity", "unit_price"]


class StockInForm(forms.ModelForm):
    """
    Specialised form for Stock In — hides movement_type (preset to IN),
    auto-generates reference if blank, and provides a clean UX for
    warehouse staff recording incoming goods.

    MENTOR NOTE: We use a dedicated form (not the generic ModelForm) to
    show different fields for IN vs OUT vs ADJUSTMENT. This follows the
    "one form per use case" Django best practice — even when backed by the
    same model.
    """
    class Meta:
        model = StockTransaction
        fields = ["reference_number", "notes"]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["reference_number"].help_text = "Supplier invoice / PO number (auto-generated if blank)"


class StockOutForm(forms.ModelForm):
    class Meta:
        model = StockTransaction
        fields = ["reference_number", "notes"]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 2}),
        }
