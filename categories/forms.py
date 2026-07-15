from django import forms
from .models import Category


class CategoryForm(forms.ModelForm):
    """
    ModelForm for Category.
    """
    class Meta:
        model = Category
        fields = ["name", "description", "status"]
        # You can pass widget attrs here (like Bootstrap classes) to keep
        # template clean, OR style in the template. We'll style in the template
        # to keep things visible.
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }
