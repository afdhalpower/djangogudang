from django import forms
from django.core.validators import MinValueValidator
from .models import CompanySetting


class CompanySettingForm(forms.ModelForm):
    """Form for editing company profile and warehouse settings.

    MENTOR NOTE: A single ModelForm covers both company and warehouse
    info sections — they're related enough to share one view, but in
    production you might split into tabs for UX clarity.
    """
    class Meta:
        model = CompanySetting
        exclude = ["created_at", "updated_at"]
        widgets = {
            "address": forms.Textarea(attrs={"rows": 3}),
            "warehouse_address": forms.Textarea(attrs={"rows": 3}),
            "logo": forms.FileInput(),
        }
