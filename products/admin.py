from django.contrib import admin
from django.utils.html import format_html
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "sku", "name", "category", "unit", "supplier",
        "current_stock", "minimum_stock", "selling_price", "status", "image_tag",
    )
    list_filter = ("status", "category", "unit", "supplier")
    search_fields = ("sku", "barcode", "name")
    ordering = ("-created_at",)
    list_per_page = 25
    readonly_fields = ("current_stock", "created_at", "updated_at", "image_tag")

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="60" />', obj.image.url)
        return "—"
    image_tag.short_description = "Image"

    fieldsets = [
        ("Identity", {"fields": ("sku", "barcode", "name", "description")}),
        ("Relationships", {"fields": ("category", "unit", "supplier")}),
        ("Pricing", {"fields": ("purchase_price", "selling_price")}),
        ("Stock", {"fields": ("current_stock", "minimum_stock")}),
        ("Media", {"fields": ("image",)}),
        ("Status & Timestamps", {"fields": ("status", "created_at", "updated_at")}),
    ]
