"""
Signals to incrementally update product stock on every transaction.
Also updates ProductBatch stock when batch tracking is used.
"""
from django.db.models import F
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from .models import StockTransaction, StockTransactionItem, ProductBatch
from products.models import Product


@receiver(post_save, sender=StockTransactionItem)
def stock_item_saved(sender, instance, created, **kwargs):
    """
    On every item save:
      - For stock reduction (OUT/ADJUSTMENT remove): lock the product row,
        validate that current stock is sufficient, and subtract atomically.
      - For stock addition (IN/ADJUSTMENT add): add to stock atomically.
      - Also update the linked ProductBatch if one is set.
    """
    if not created:
        return

    movement_type = instance.transaction.movement_type
    product_id = instance.product_id
    qty = instance.quantity

    if movement_type == StockTransaction.MOVEMENT_IN:
        Product.objects.filter(pk=product_id).update(
            current_stock=F("current_stock") + qty
        )
        # Update batch stock if linked
        if instance.batch_id:
            ProductBatch.objects.filter(pk=instance.batch_id).update(
                current_stock=F("current_stock") + qty
            )

    elif movement_type == StockTransaction.MOVEMENT_OUT:
        product = Product.objects.select_for_update().get(pk=product_id)
        if product.current_stock < qty:
            raise ValidationError(
                f"Insufficient stock for {product.name} (SKU: {product.sku}). "
                f"Available: {product.current_stock}, requested: {qty}."
            )
        Product.objects.filter(pk=product_id).update(
            current_stock=F("current_stock") - qty
        )
        # Update batch stock if linked
        if instance.batch_id:
            ProductBatch.objects.filter(pk=instance.batch_id).update(
                current_stock=F("current_stock") - qty
            )

    elif movement_type == StockTransaction.MOVEMENT_ADJUSTMENT:
        direction = instance.transaction.adjustment_direction
        if direction == "add":
            Product.objects.filter(pk=product_id).update(
                current_stock=F("current_stock") + qty
            )
            if instance.batch_id:
                ProductBatch.objects.filter(pk=instance.batch_id).update(
                    current_stock=F("current_stock") + qty
                )
        else:
            product = Product.objects.select_for_update().get(pk=product_id)
            if product.current_stock < qty:
                raise ValidationError(
                    f"Insufficient stock for {product.name} (SKU: {product.sku}). "
                    f"Available: {product.current_stock}, requested removal: {qty}."
                )
            Product.objects.filter(pk=product_id).update(
                current_stock=F("current_stock") - qty
            )
            if instance.batch_id:
                ProductBatch.objects.filter(pk=instance.batch_id).update(
                    current_stock=F("current_stock") - qty
                )


@receiver(post_delete, sender=StockTransactionItem)
def stock_item_deleted(sender, instance, **kwargs):
    """Reverse the stock change when an item is deleted."""
    movement_type = instance.transaction.movement_type
    product_id = instance.product_id
    qty = instance.quantity

    if movement_type == StockTransaction.MOVEMENT_IN:
        Product.objects.filter(pk=product_id).update(
            current_stock=F("current_stock") - qty
        )
        if instance.batch_id:
            ProductBatch.objects.filter(pk=instance.batch_id).update(
                current_stock=F("current_stock") - qty
            )
    elif movement_type == StockTransaction.MOVEMENT_OUT:
        Product.objects.filter(pk=product_id).update(
            current_stock=F("current_stock") + qty
        )
        if instance.batch_id:
            ProductBatch.objects.filter(pk=instance.batch_id).update(
                current_stock=F("current_stock") + qty
            )
    elif movement_type == StockTransaction.MOVEMENT_ADJUSTMENT:
        direction = instance.transaction.adjustment_direction
        if direction == "add":
            Product.objects.filter(pk=product_id).update(
                current_stock=F("current_stock") - qty
            )
            if instance.batch_id:
                ProductBatch.objects.filter(pk=instance.batch_id).update(
                    current_stock=F("current_stock") - qty
                )
        else:
            Product.objects.filter(pk=product_id).update(
                current_stock=F("current_stock") + qty
            )
            if instance.batch_id:
                ProductBatch.objects.filter(pk=instance.batch_id).update(
                    current_stock=F("current_stock") + qty
                )
