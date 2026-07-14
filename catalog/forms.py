from django import forms
from .models import Category, Unit


class CategoryForm(forms.ModelForm):
    """Form for creating/editing a Category.

    MENTOR NOTE: ModelForm auto-generates fields from the model and runs
    validation (unique name, max_length, etc.). Equivalent to Laravel's
    `Form Request` + model `$fillable`, but Django does both in one class.
    """

    class Meta:
        model = Category
        fields = ["name", "description", "status"]
        widgets = {
            # Django's way of setting HTML attributes on generated inputs.
            # Like Laravel's `{{ Form::text('name', ...) }}`.
            "description": forms.Textarea(attrs={"rows": 3}),
        }


class UnitForm(forms.ModelForm):
    class Meta:
        model = Unit
        fields = ["name", "abbreviation"]
