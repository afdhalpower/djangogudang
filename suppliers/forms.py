from django import forms
from .models import Supplier


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ["company_name", "contact_person", "phone", "email", "address", "status"]
        widgets = {
            "address": forms.Textarea(attrs={"rows": 3}),
        }
