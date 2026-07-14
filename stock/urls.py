from django.urls import path
from . import views

app_name = "stock"

urlpatterns = [
    path("", views.StockTransactionListView.as_view(), name="list"),
    path("in/new/", views.StockInCreateView.as_view(), name="in_create"),
    path("out/new/", views.StockOutCreateView.as_view(), name="out_create"),
    path("<int:pk>/", views.StockTransactionDetailView.as_view(), name="detail"),
]
