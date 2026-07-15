from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import UpdateView
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from .models import User
from .forms import UserProfileForm


# --- AUTHENTICATION -------------------------------------------------------


class LoginView(auth_views.LoginView):
    template_name = "accounts/login.html"
    redirect_authenticated_user = True  # if already logged in, bounce to dashboard


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy("accounts:login")


class PasswordChangeView(auth_views.PasswordChangeView):
    template_name = "accounts/password_change.html"
    success_url = reverse_lazy("accounts:profile")

    def form_valid(self, form):
        messages.success(self.request, _("Password berhasil diubah."))
        return super().form_valid(form)


# --- PROFILE (self-service) ------------------------------------------------
class ProfileView(LoginRequiredMixin, UpdateView):
    """Let the current user edit their own profile."""
    model = User
    form_class = UserProfileForm
    template_name = "accounts/profile.html"
    success_url = reverse_lazy("accounts:profile")

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, _("Profil berhasil diperbarui."))
        return super().form_valid(form)
