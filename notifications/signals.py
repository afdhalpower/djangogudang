"""
Signal — auto-generate low-stock notifications when products
cross the threshold during stock transactions.

Fire-and-forget: if no matching notification exists for this product,
one is created. This prevents duplicate spam.
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import F
from django.utils import timezone
from .models import Notification
from products.models import Product


def _check_and_notify(product):
    """Create low-stock notification if product is below threshold.

    Dedup: skip if an unread low_stock notification already exists
    for this product (by title contains product name).
    """
    if product.current_stock > product.minimum_stock:
        return  # All good, no notification needed

    # Check for existing unread low-stock notification for this product
    exists = Notification.objects.filter(
        notification_type="low_stock",
        is_read=False,
        title__icontains=product.name,
    ).exists()

    if exists:
        return

    Notification.objects.create(
        user=None,  # broadcast
        title=f"Low Stock: {product.name}",
        message=(
            f"Product {product.name} (SKU: {product.sku}) has only "
            f"{product.current_stock} {product.unit.abbreviation} in stock, "
            f"below minimum of {product.minimum_stock}."
        ),
        notification_type="low_stock",
        link=f"/products/{product.pk}/",
    )


@receiver(post_save, sender=Product)
def product_saved(sender, instance, **kwargs):
    """Check low stock after every product save."""
    _check_and_notify(instance)
