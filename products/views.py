"""
Products views — full CRUD plus search/filter.
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db import models
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from .models import Product
from .forms import ProductForm


class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = "products/list.html"
    context_object_name = "products"
    paginate_by = 20

    def get_queryset(self):
        qs = Product.objects.select_related("category", "unit", "supplier").all()

        # --- Search (name, sku, barcode) ---
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(
                models.Q(name__icontains=q)
                | models.Q(sku__icontains=q)
                | models.Q(barcode__icontains=q)
            )

        # --- Filter by status ---
        status = self.request.GET.get("status", "")
        if status in ("active", "inactive"):
            qs = qs.filter(status=status)

        # --- Filter by category ---
        cat = self.request.GET.get("category", "")
        if cat.isdigit():
            qs = qs.filter(category_id=int(cat))

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["q"] = self.request.GET.get("q", "")
        context["filter_status"] = self.request.GET.get("status", "")
        context["filter_category"] = self.request.GET.get("category", "")
        # Pass categories for the filter dropdown
        from categories.models import Category
        context["categories"] = Category.objects.filter(status="active")
        return context


class ProductDetailView(LoginRequiredMixin, DetailView):
    model = Product
    template_name = "products/detail.html"
    context_object_name = "product"

    def get_queryset(self):
        return Product.objects.select_related("category", "unit", "supplier")


class ProductCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = "products/form.html"
    success_message = "Product created successfully."

    def form_valid(self, form):
        response = super().form_valid(form)
        from core.utils import log_activity
        log_activity(self.request.user, "Created Product", f"SKU: {self.object.sku}, Name: {self.object.name}")
        return response


class ProductUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = "products/form.html"
    success_message = "Product updated successfully."

    def form_valid(self, form):
        response = super().form_valid(form)
        from core.utils import log_activity
        log_activity(self.request.user, "Updated Product", f"SKU: {self.object.sku}, Name: {self.object.name}, Status: {self.object.status}")
        return response


class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = "products/confirm_delete.html"
    success_url = reverse_lazy("products:list")
    success_message = "Product deleted."

    def form_valid(self, form):
        messages.success(self.request, self.success_message)
        from core.utils import log_activity
        log_activity(self.request.user, "Deleted Product", f"SKU: {self.get_object().sku}, Name: {self.get_object().name}")
        return super().form_valid(form)


class ProductBarcodePrintView(LoginRequiredMixin, DetailView):
    """View to display and print barcode sheet for a product."""
    model = Product
    template_name = "products/barcode_print.html"
    context_object_name = "product"
