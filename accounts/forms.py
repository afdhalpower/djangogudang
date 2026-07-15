from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class UserProfileForm(forms.ModelForm):
    """Edit the logged-in user's own profile."""
    class Meta:
        model = User
        # Deliberately EXCLUDE `role`, `is_staff`, `is_superuser` — a user must
        # not be able to promote themselves to admin (authorization/security).
        fields = ["first_name", "last_name", "email", "phone"]


class UserCreationFormCustom(UserCreationForm):
    """Used by admin/staff to create a user WITH a role.

    We extend Django's UserCreationForm (which gives username + password1/2
    with strength validation) and add our `role` and `phone` fields.
    """
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ["username", "first_name", "last_name", "email", "role", "phone"]
