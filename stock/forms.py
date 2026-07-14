from django import forms
from .models import StockTransaction, StockTransactionItem
from products.models import Product


class StockTransactionItemForm(forms.ModelForm):
    class Meta:
        model = StockTransactionItem
        fields = ["product", "quantity", "unit_price"]


class StockInForm(forms.ModelForm):
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


class StockAdjustmentForm(forms.ModelForm):
    """Form for manual stock adjustment with reason and direction.

    MENTOR NOTE: Unlike StockInForm/StockOutForm which share the same fields,
    Adjustment shows additional fields (reason, direction) specific to the
    use case — demonstrating Django's "one form per use case" pattern even
    when the underlying model is the same.
    """
    class Meta:
        model = StockTransaction
        fields = ["reference_number", "notes", "adjustment_reason", "adjustment_direction"]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["adjustment_reason"].required = True
        self.fields["adjustment_reason"].help_text = "Why is the stock being adjusted?"
        self.fields["adjustment_direction"].widget = forms.RadioSelect(
            choices=StockTransaction.ADJUSTMENT_DIRECTION_CHOICES
        )
        self.fields["reference_number"].required = False
        self.fields["reference_number"].help_text = "Internal reference (optional)"
