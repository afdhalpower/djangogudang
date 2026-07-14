"""
Context processors — inject global data into every template.

MENTOR NOTE: Context processors are like Laravel's `View::composer` /
`AppServiceProvider::boot()` with `view()->share()`. They run on every
request and add variables to the template context automatically.
"""
from django.db.models import F
from products.models import Product


def notification_unread_count(request):
    """Inject low-stock product count as notification badge."""
    if not request.user.is_authenticated:
        return {"notification_unread_count": 0}
    count = Product.objects.filter(
        current_stock__lte=F("minimum_stock")
    ).count()
    return {"notification_unread_count": count}
