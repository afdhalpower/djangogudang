from django.apps import AppConfig


class StockConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "stock"
    verbose_name = "Stock Transactions"

    def ready(self):
        import stock.signals  # noqa — registers signal receivers
