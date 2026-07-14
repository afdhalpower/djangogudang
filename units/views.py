from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from .models import Unit
from .forms import UnitForm


class UnitListView(LoginRequiredMixin, ListView):
    model = Unit
    template_name = "units/list.html"
    context_object_name = "units"
    paginate_by = 20


class UnitDetailView(LoginRequiredMixin, DetailView):
    model = Unit
    template_name = "units/detail.html"
    context_object_name = "unit"


class UnitCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Unit
    form_class = UnitForm
    template_name = "units/form.html"
    success_message = "Unit created successfully."


class UnitUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Unit
    form_class = UnitForm
    template_name = "units/form.html"
    success_message = "Unit updated successfully."


class UnitDeleteView(LoginRequiredMixin, DeleteView):
    model = Unit
    template_name = "units/confirm_delete.html"
    success_url = reverse_lazy("units:list")
    success_message = "Unit deleted."

    def form_valid(self, form):
        messages.success(self.request, self.success_message)
        return super().form_valid(form)
