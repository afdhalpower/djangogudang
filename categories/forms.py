from django import forms
from .models import Category


class CategoryForm(forms.ModelForm):
    """
    ModelForm auto-generates fields from the Category model, adds validation,
    and handles save(). It's like a Laravel FormRequest + Livewire form in one.
    NOTE: You don't need to manually re-list fields — ModelForm reads them.
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
