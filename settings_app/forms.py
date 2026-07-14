from django import forms
from .models import CompanySetting


class CompanySettingForm(forms.ModelForm):
    class Meta:
        model = CompanySetting
        exclude = ["created_at", "updated_at"]
        widgets = {
            "address": forms.Textarea(attrs={"rows": 3}),
            "warehouse_location": forms.Textarea(attrs={"rows": 2}),
            "low_stock_threshold": forms.NumberInput(attrs={"min": 1}),
        }
