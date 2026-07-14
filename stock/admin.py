from django.contrib import admin
from .models import StockTransaction, StockTransactionItem


class StockTransactionItemInline(admin.TabularInline):
    """
    Inline admin — like Laravel's `Nova HasMany` / Filament `Repeater`.
    Shows/edit line items directly on the parent StockTransaction form.
    """
    model = StockTransactionItem
    extra = 1
    autocomplete_fields = ("product",)


@admin.register(StockTransaction)
class StockTransactionAdmin(admin.ModelAdmin):
    list_display = ("__str__", "movement_type", "date", "reference_number", "created_by", "created_at")
    list_filter = ("movement_type", "date")
    search_fields = ("reference_number", "notes")
    ordering = ("-created_at",)
    inlines = [StockTransactionItemInline]
    readonly_fields = ("created_at", "updated_at")


@admin.register(StockTransactionItem)
class StockTransactionItemAdmin(admin.ModelAdmin):
    list_display = ("transaction", "product", "quantity", "unit_price")
    search_fields = ("product__name", "product__sku")
