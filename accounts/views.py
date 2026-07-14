from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import UpdateView
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from .models import User
from .forms import UserProfileForm


# --- AUTHENTICATION -------------------------------------------------------
# Django ships fully-tested auth views (LoginView, LogoutView, PasswordChangeView).
# Reusing them = "keep views thin" + don't reinvent security. We only point them
# at our templates and set redirects — exactly like Laravel's built-in Auth
# controllers, but we don't even have to write them.


class LoginView(auth_views.LoginView):
    template_name = "accounts/login.html"
    redirect_authenticated_user = True  # if already logged in, bounce to dashboard


class LogoutView(auth_views.LogoutView):
    # Django 5 requires POST for logout (CSRF-protected) — this is correct
    # security behavior, preventing a third party from logging a user out via
    # a simple GET link. The template submits a small POST form for this.
    next_page = reverse_lazy("accounts:login")


class PasswordChangeView(auth_views.PasswordChangeView):
    template_name = "accounts/password_change.html"
    success_url = reverse_lazy("accounts:profile")

    def form_valid(self, form):
        messages.success(self.request, _("Password berhasil diubah."))
        return super().form_valid(form)


# --- PROFILE (self-service) ------------------------------------------------
class ProfileView(LoginRequiredMixin, UpdateView):
    """Let the current user edit their own profile.

    LoginRequiredMixin = require auth (like Laravel's `auth` middleware /
    `$this->middleware('auth')`). `get_object` pins the edit to request.user
    so a user can NEVER edit someone else — authorization enforced server-side.
    """
    model = User
    form_class = UserProfileForm
    template_name = "accounts/profile.html"
    success_url = reverse_lazy("accounts:profile")

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, _("Profil berhasil diperbarui."))
        return super().form_valid(form)
