"""Web page views — renders Django templates for storefront."""

from django.shortcuts import render, get_object_or_404
from django.http import Http404
from apps.store.models import StoreSettings
from apps.products.models import Product, Category
from apps.orders.models import Order


def _get_store(slug=None):
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


def cart_view(request):
    store = _get_store()
    if not store:
        return render(request, "store/empty_home.html")
    return render(request, "store/cart.html", {"store": store})


def checkout_view(request):
    store = _get_store()
    if not store:
        return render(request, "store/empty_home.html")
    return render(request, "store/checkout.html", {"store": store})


def order_confirmation_view(request, order_number):
    store = _get_store()
    if not store:
        return render(request, "store/empty_home.html")
    try:
        order = Order.objects.get(order_number=order_number, store=store)
    except Order.DoesNotExist:
        raise Http404("Pesanan tidak ditemukan.")
    return render(request, "store/order_confirmation.html", {
        "store": store,
        "order": order,
    })
