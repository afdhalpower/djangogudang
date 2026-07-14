from django.urls import path
from . import views

app_name = "reports"

urlpatterns = [
    # Inventory Report
    path("inventory/", views.InventoryReportView.as_view(), name="inventory"),
    path("inventory/csv/", views.inventory_csv, name="inventory_csv"),

    # Low Stock Report
    path("low-stock/", views.LowStockReportView.as_view(), name="low_stock"),
    path("low-stock/csv/", views.low_stock_csv, name="low_stock_csv"),

    # Stock Card
    path("stock-card/", views.StockCardView.as_view(), name="stock_card"),
    path("stock-card/csv/", views.stock_card_csv, name="stock_card_csv"),
]
