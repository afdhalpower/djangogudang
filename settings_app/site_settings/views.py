from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import UpdateView
from .models import CompanySetting
from .forms import CompanySettingForm


class CompanySettingView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """Edit the singleton company settings.

    MENTOR NOTE: UpdateView targeting a single object (pk=1). Django
    doesn't have a dedicated SingletonView, so we use get_object to
    fetch or create the settings row. This is the cleanest pattern.
    """
    model = CompanySetting
    form_class = CompanySettingForm
    template_name = "site_settings/form.html"
    success_url = reverse_lazy("settings_app:edit")
    success_message = "Settings saved."

    def get_object(self, queryset=None):
        return CompanySetting.get_settings()
