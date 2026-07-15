"""Context processor: expose low-stock count to all templates.

Replaces the deleted notifications.context_processors.notification_unread_count.
We compute the count of products at or below minimum stock — this is what
the badge in the sidebar/topbar represents.
"""
from django.db.models import Q, F
from products.models import Product


def notification_unread_count(request):
    if not hasattr(request, "user") or not request.user.is_authenticated:
        return {"notification_unread_count": 0}
    
    from settings_app.models import CompanySetting
    settings = CompanySetting.get_settings()
    if not settings.enable_low_stock_alert:
        return {"notification_unread_count": 0}

    count = Product.objects.filter(
        current_stock__lte=F("minimum_stock")
    ).count()
    return {"notification_unread_count": count}
