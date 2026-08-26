"""Web page views — renders Django templates for storefront."""

from django.shortcuts import render, get_object_or_404
from apps.store.models import StoreSettings
from apps.products.models import Product, Category


def _get_store(slug=None):
    """Get store by slug or return first store (for single-store dev mode)."""
    if slug:
        return get_object_or_404(StoreSettings, slug=slug)
    return StoreSettings.objects.first()


def home_view(request):
    store = _get_store()
    if not store:
        return render(request, "store/empty_home.html")
    products = Product.objects.filter(store=store, is_active=True)[:12]
    featured = products.filter(is_featured=True)[:4]
    return render(request, "store/home.html", {
        "store": store,
        "products": products,
        "featured_products": featured,
    })


def catalog_view(request):
    store = _get_store()
    if not store:
        return render(request, "store/empty_home.html")
    categories = Category.objects.filter(store=store)
    products = Product.objects.filter(store=store, is_active=True)
    return render(request, "store/catalog.html", {
        "store": store,
        "categories": categories,
        "products": products,
    })


def product_detail_view(request, slug):
    store = _get_store()
    if not store:
        return render(request, "store/empty_home.html")
    product = get_object_or_404(Product, store=store, slug=slug, is_active=True)
    return render(request, "store/product_detail.html", {
        "store": store,
        "product": product,
    })
