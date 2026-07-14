from django.urls import path
from . import views

app_name = "units"

urlpatterns = [
    path("", views.UnitListView.as_view(), name="list"),
    path("create/", views.UnitCreateView.as_view(), name="create"),
    path("<int:pk>/", views.UnitDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", views.UnitUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", views.UnitDeleteView.as_view(), name="delete"),
]
