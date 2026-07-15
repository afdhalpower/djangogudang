from django.urls import path
from . import views

app_name = "reports"

urlpatterns = [
    # Inventory Report
    path("inventory/", views.InventoryReportView.as_view(), name="inventory"),
    path("inventory/csv/", views.inventory_csv, name="inventory_csv"),
    path("inventory/xlsx/", views.inventory_xlsx, name="inventory_xlsx"),

    # Low Stock Report
    path("low-stock/", views.LowStockReportView.as_view(), name="low_stock"),
    path("low-stock/csv/", views.low_stock_csv, name="low_stock_csv"),
    path("low-stock/xlsx/", views.low_stock_xlsx, name="low_stock_xlsx"),

    # Stock Card
    path("stock-card/", views.StockCardView.as_view(), name="stock_card"),
    path("stock-card/csv/", views.stock_card_csv, name="stock_card_csv"),
    path("stock-card/xlsx/", views.stock_card_xlsx, name="stock_card_xlsx"),
]
