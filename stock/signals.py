"""
Signals — update product stock incrementally on every transaction.

FIX: Previously we recalculated stock from ALL transactions, which erased
the seed value (current_stock set directly on model). Now we use an
INCREMENTAL approach — adding/subtracting from current_stock directly.

This matches how a real warehouse works: you set initial stock when
creating the product, then every IN/OUT adjusts it.

ARCHITECTURE NOTE:
- Incremental updates are simpler but CAN drift if a transaction is
  deleted/modified. For a production system you'd add a reconciliation
  script. For a learning project this is the right balance.
- F() expressions do the update in a single SQL statement (race-condition
  resistant, no need for select_for_update for most cases).
"""
from django.db.models import F
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from .models import StockTransaction, StockTransactionItem
from products.models import Product


@receiver(post_save, sender=StockTransactionItem)
def stock_item_saved(sender, instance, created, **kwargs):
    """
    On every item save:
      - OUT: validate stock is sufficient BEFORE subtracting.
      - Update current_stock atomically with F().
    """
    if not created:
        return  # Only act on NEW items; edits handled separately later

    movement_type = instance.transaction.movement_type
    product_id = instance.product_id
    qty = instance.quantity

    if movement_type == StockTransaction.MOVEMENT_IN:
        # Increase stock atomically
        Product.objects.filter(pk=product_id).update(
            current_stock=F("current_stock") + qty
        )

    elif movement_type == StockTransaction.MOVEMENT_OUT:
        # Check — SELECT then UPDATE (prevents negative without table-lock)
        product = Product.objects.get(pk=product_id)
        if product.current_stock < qty:
            raise ValidationError(
                f"Insufficient stock for {product.name} (SKU: {product.sku}). "
                f"Available: {product.current_stock}, requested: {qty}."
            )
        Product.objects.filter(pk=product_id).update(
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
    elif movement_type == StockTransaction.MOVEMENT_OUT:
        Product.objects.filter(pk=product_id).update(
            current_stock=F("current_stock") + qty
        )
