from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from .models import Supplier
from .forms import SupplierForm


class SupplierListView(LoginRequiredMixin, ListView):
    model = Supplier
    template_name = "suppliers/list.html"
    context_object_name = "suppliers"
    paginate_by = 20


class SupplierDetailView(LoginRequiredMixin, DetailView):
    model = Supplier
    template_name = "suppliers/detail.html"
    context_object_name = "supplier"


class SupplierCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Supplier
    form_class = SupplierForm
    template_name = "suppliers/form.html"
    success_message = "Supplier created successfully."

    def form_valid(self, form):
        response = super().form_valid(form)
        from core.utils import log_activity
        log_activity(self.request.user, "Created Supplier", f"Company: {self.object.company_name}")
        return response


class SupplierUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Supplier
    form_class = SupplierForm
    template_name = "suppliers/form.html"
    success_message = "Supplier updated successfully."

    def form_valid(self, form):
        response = super().form_valid(form)
        from core.utils import log_activity
        log_activity(self.request.user, "Updated Supplier", f"Company: {self.object.company_name}, Status: {self.object.status}")
        return response


class SupplierDeleteView(LoginRequiredMixin, DeleteView):
    model = Supplier
    template_name = "suppliers/confirm_delete.html"
    success_url = reverse_lazy("suppliers:list")
    success_message = "Supplier deleted."

    def form_valid(self, form):
        messages.success(self.request, self.success_message)
        from core.utils import log_activity
        log_activity(self.request.user, "Deleted Supplier", f"Company: {self.get_object().company_name}")
        return super().form_valid(form)
