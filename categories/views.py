"""
Category views — full CRUD using Django's generic Class-Based Views.

MENTOR NOTE (Laravel -> Django):
- Single CBV replaces a resource controller method (index, show, create, etc.)
- LoginRequiredMixin = auth middleware (like Laravel's `auth` middleware)
- SuccessMessageMixin = flash message on success (like `session()->flash()`)
- get_absolute_url() on model = default success_url for create/update views
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Category
from .forms import CategoryForm


class CategoryListView(LoginRequiredMixin, ListView):
    """
    ListView = "give me all objects, render template" — like
    `Category::all()` + `return view('categories.index', compact('categories'))`.
    The context variable defaults to `category_list` (lowercase model + _list).
    """
    model = Category
    template_name = "categories/list.html"
    context_object_name = "categories"  # override default 'category_list'
    paginate_by = 20


class CategoryDetailView(LoginRequiredMixin, DetailView):
    model = Category
    template_name = "categories/detail.html"
    context_object_name = "category"


class CategoryCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """
    CreateView:
      1. GET  -> renders form (empty)
      2. POST -> validates & saves, then redirects to get_absolute_url()
    Equivalent to a Laravel controller with two methods (create() + store()).
    """
    model = Category
    form_class = CategoryForm
    template_name = "categories/form.html"
    success_message = "Category created successfully."


class CategoryUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """
    UpdateView: same anatomy as CreateView but pre-fills from the existing object.
    Like Laravel's edit() + update() combined.
    """
    model = Category
    form_class = CategoryForm
    template_name = "categories/form.html"
    success_message = "Category updated successfully."


class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    """
    DeleteView:
      GET  -> render confirmation page
      POST -> delete object, redirect to success_url
    Equivalent to Laravel's destroy() that returns a confirmation form first.
    """
    model = Category
    template_name = "categories/confirm_delete.html"
    success_url = reverse_lazy("categories:list")
    success_message = "Category deleted."

    def form_valid(self, form):
        # SuccessMessageMixin works with DeleteView in Django 5 if we
        # add the message manually (DeleteView doesn't auto-call success_message).
        from django.contrib import messages
        messages.success(self.request, self.success_message)
        return super().form_valid(form)
