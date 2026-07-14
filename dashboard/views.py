from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class DashboardHomeView(LoginRequiredMixin, TemplateView):
    """App home. For now a minimal shell; dashboard cards/charts arrive later.

    MENTOR NOTE: TemplateView is the simplest CBV — render a template with a
    context. Like Laravel's `return view('dashboard.home')`. We'll replace the
    context with real aggregates once the data models (products, stock) exist.
    """
    template_name = "dashboard/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Dashboard"
        return context
