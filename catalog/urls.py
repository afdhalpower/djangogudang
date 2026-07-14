from django.urls import path
from . import views

app_name = "catalog"

urlpatterns = [
    # Categories
    path("categories/", views.CategoryListView.as_view(), name="category_list"),
    path("categories/create/", views.CategoryCreateView.as_view(), name="category_create"),
    path("categories/<int:pk>/edit/", views.CategoryUpdateView.as_view(), name="category_update"),
    path("categories/<int:pk>/delete/", views.CategoryDeleteView.as_view(), name="category_delete"),
    # Units
    path("units/", views.UnitListView.as_view(), name="unit_list"),
    path("units/create/", views.UnitCreateView.as_view(), name="unit_create"),
    path("units/<int:pk>/edit/", views.UnitUpdateView.as_view(), name="unit_update"),
    path("units/<int:pk>/delete/", views.UnitDeleteView.as_view(), name="unit_delete"),
]
