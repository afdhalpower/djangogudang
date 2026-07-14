from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import TemplateView
from products.models import Product
from suppliers.models import Supplier
from stock.models import StockTransaction
from categories.models import Category
from units.models import Unit


class GlobalSearchView(LoginRequiredMixin, TemplateView):
    """Search across products, suppliers, and transactions from one page."""
    template_name = "search/results.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        q = self.request.GET.get("q", "").strip()

        context["query"] = q

        if not q:
            context["product_count"] = 0
            context["supplier_count"] = 0
            context["transaction_count"] = 0
            return context

        # Products
        products = Product.objects.filter(
            Q(name__icontains=q)
            | Q(sku__icontains=q)
            | Q(barcode__icontains=q)
            | Q(description__icontains=q)
        ).select_related("category", "unit", "supplier")[:10]
        context["products"] = products
        context["product_count"] = products.count()

        # Suppliers
        suppliers = Supplier.objects.filter(
            Q(company_name__icontains=q)
            | Q(contact_person__icontains=q)
            | Q(phone__icontains=q)
            | Q(email__icontains=q)
        )[:10]
        context["suppliers"] = suppliers
        context["supplier_count"] = suppliers.count()

        # Stock transactions
        transactions = StockTransaction.objects.filter(
            Q(reference_number__icontains=q)
            | Q(notes__icontains=q)
        ).select_related("created_by").prefetch_related(
            "items", "items__product"
        )[:10]
        context["transactions"] = transactions
        context["transaction_count"] = transactions.count()

        return context


from django.contrib.auth.decorators import login_required


@login_required
def global_search_json(request):
    """JSON endpoint for topbar autocomplete — returns lightweight results."""
    q = request.GET.get("q", "").strip()
    if not q or len(q) < 2:
        return JsonResponse({"results": [], "total": 0})

    results = []

    # Products
    products = Product.objects.filter(
        Q(name__icontains=q) | Q(sku__icontains=q)
    ).select_related("category", "unit")[:5]
    for p in products:
        results.append({
            "type": "product",
            "label": f"{p.sku} — {p.name}",
            "subtitle": f"{p.current_stock} {p.unit.abbreviation} · {p.category.name if p.category else '—'}",
            "url": f"/products/{p.pk}/",
        })

    # Categories
    cats = Category.objects.filter(name__icontains=q)[:5]
    for c in cats:
        results.append({
            "type": "category",
            "label": c.name,
            "subtitle": f"{'Active' if c.status == 'active' else 'Inactive'}",
            "url": f"/categories/{c.pk}/",
        })

    # Suppliers
    suppliers = Supplier.objects.filter(
        Q(company_name__icontains=q) | Q(contact_person__icontains=q)
    )[:5]
    for s in suppliers:
        results.append({
            "type": "supplier",
            "label": s.company_name,
            "subtitle": s.contact_person or "—",
            "url": f"/suppliers/{s.pk}/",
        })

    return JsonResponse({"results": results, "total": len(results)})
