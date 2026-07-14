from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic.edit import UpdateView
from .models import CompanySetting
from .forms import CompanySettingForm


class CompanySettingUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """Edit company & warehouse settings (single-row, pk always 1)."""
    model = CompanySetting
    form_class = CompanySettingForm
    template_name = "settings_app/form.html"
    success_url = "/settings/"
    success_message = "Settings saved successfully."

    def get_object(self, queryset=None):
        return CompanySetting.get_settings()
