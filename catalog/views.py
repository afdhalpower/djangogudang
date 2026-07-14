"""
Catalog views — HTMX-driven CRUD for Category and Unit.

MENTOR NOTE (Laravel -> Django):
- We use mixins (LoginRequiredMixin) to enforce auth — equivalent to
  Laravel's `__construct` + `$this->middleware('auth')` or route middleware.
- We use generic CBVs (ListView, CreateView, UpdateView, DeleteView) which
  correspond to Laravel's Resource Controller methods (index, create, store,
  edit, update, destroy) all in one class.
- HTMX pattern: the list page has a "table partial" that gets swapped via
  `hx-target` + `hx-get` — like Alpine + Livewire, but lighter.
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView
from django.contrib import messages

from .forms import CategoryForm, UnitForm
from .models import Category, Unit


# ─── CATEGORY CRUD ─────────────────────────────────────────────────────────


class CategoryListView(LoginRequiredMixin, ListView):
    """List all categories with search/filter."""
    model = Category
    template_name = "catalog/category_list.html"
    context_object_name = "categories"
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset()
        search = self.request.GET.get("q", "").strip()
        status_filter = self.request.GET.get("status", "")
        if search:
            qs = qs.filter(name__icontains=search)
        if status_filter:
            qs = qs.filter(status=status_filter)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = "Categories"
        ctx["filter_status"] = self.request.GET.get("status", "")
        ctx["filter_q"] = self.request.GET.get("q", "")
        return ctx


class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = "catalog/category_form.html"
    success_url = reverse_lazy("catalog:category_list")

    def form_valid(self, form):
        messages.success(self.request, f"Category '{form.instance.name}' created.")
        return super().form_valid(form)


class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = "catalog/category_form.html"
    success_url = reverse_lazy("catalog:category_list")

    def form_valid(self, form):
        messages.success(self.request, f"Category '{form.instance.name}' updated.")
        return super().form_valid(form)


class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = Category
    template_name = "catalog/category_confirm_delete.html"
    success_url = reverse_lazy("catalog:category_list")

    def form_valid(self, form):
        messages.success(self.request, f"Category '{self.object.name}' deleted.")
        return super().form_valid(form)


# ─── UNIT CRUD ──────────────────────────────────────────────────────────────


class UnitListView(LoginRequiredMixin, ListView):
    model = Unit
    template_name = "catalog/unit_list.html"
    context_object_name = "units"
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset()
        search = self.request.GET.get("q", "").strip()
        if search:
            qs = qs.filter(name__icontains=search)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = "Units"
        ctx["filter_q"] = self.request.GET.get("q", "")
        return ctx


class UnitCreateView(LoginRequiredMixin, CreateView):
    model = Unit
    form_class = UnitForm
    template_name = "catalog/unit_form.html"
    success_url = reverse_lazy("catalog:unit_list")

    def form_valid(self, form):
        messages.success(self.request, f"Unit '{form.instance.name}' created.")
        return super().form_valid(form)


class UnitUpdateView(LoginRequiredMixin, UpdateView):
    model = Unit
    form_class = UnitForm
    template_name = "catalog/unit_form.html"
    success_url = reverse_lazy("catalog:unit_list")

    def form_valid(self, form):
        messages.success(self.request, f"Unit '{form.instance.name}' updated.")
        return super().form_valid(form)


class UnitDeleteView(LoginRequiredMixin, DeleteView):
    model = Unit
    template_name = "catalog/unit_confirm_delete.html"
    success_url = reverse_lazy("catalog:unit_list")

    def form_valid(self, form):
        messages.success(self.request, f"Unit '{self.object.name}' deleted.")
        return super().form_valid(form)
