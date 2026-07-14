from django import forms
from .models import Unit


class UnitForm(forms.ModelForm):
    class Meta:
        model = Unit
        fields = ["name", "abbreviation", "description", "status"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }
