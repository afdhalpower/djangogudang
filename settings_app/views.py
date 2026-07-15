from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic.edit import UpdateView
from django.views.generic import ListView
from .models import CompanySetting
from .forms import CompanySettingForm
from core.models import ActivityLog
from core.utils import log_activity


class CompanySettingUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """Edit company & warehouse settings (single-row, pk always 1)."""
    model = CompanySetting
    form_class = CompanySettingForm
    template_name = "settings_app/form.html"
    success_url = "/settings/"
    success_message = "Settings saved successfully."

    def get_object(self, queryset=None):
        return CompanySetting.get_settings()

    def form_valid(self, form):
        response = super().form_valid(form)
        log_activity(
            self.request.user,
            "Updated company settings",
            f"Company name: {self.object.company_name}, alert enabled: {self.object.enable_low_stock_alert}"
        )
        return response


class ActivityLogListView(LoginRequiredMixin, ListView):
    """Paginated user activity logs view for audit trail."""
    model = ActivityLog
    template_name = "settings_app/activity_logs.html"
    context_object_name = "logs"
    paginate_by = 50
