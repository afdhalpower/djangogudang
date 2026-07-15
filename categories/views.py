"""
Category views — full CRUD using Django's generic Class-Based Views.
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Category
from .forms import CategoryForm


class CategoryListView(LoginRequiredMixin, ListView):
    """ListView for displaying the list of categories."""
    model = Category
    template_name = "categories/list.html"
    context_object_name = "categories"  # override default 'category_list'
    paginate_by = 20


class CategoryDetailView(LoginRequiredMixin, DetailView):
    model = Category
    template_name = "categories/detail.html"
    context_object_name = "category"


class CategoryCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = "categories/form.html"
    success_message = "Category created successfully."

    def form_valid(self, form):
        response = super().form_valid(form)
        from core.utils import log_activity
        log_activity(self.request.user, "Created Category", f"Name: {self.object.name}")
        return response


class CategoryUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = "categories/form.html"
    success_message = "Category updated successfully."

    def form_valid(self, form):
        response = super().form_valid(form)
        from core.utils import log_activity
        log_activity(self.request.user, "Updated Category", f"Name: {self.object.name}, Status: {self.object.status}")
        return response


class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = Category
    template_name = "categories/confirm_delete.html"
    success_url = reverse_lazy("categories:list")
    success_message = "Category deleted."

    def form_valid(self, form):
        from django.contrib import messages
        messages.success(self.request, self.success_message)
        from core.utils import log_activity
        log_activity(self.request.user, "Deleted Category", f"Name: {self.get_object().name}")
        return super().form_valid(form)
