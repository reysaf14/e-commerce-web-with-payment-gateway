"""Web page views — renders Django templates for storefront."""

import hmac
from django.shortcuts import render, get_object_or_404
from django.http import Http404
from django.conf import settings
from apps.store.models import StoreSettings
from apps.products.models import Product, Category
from apps.orders.models import Order
from apps.payments.models import Payment


def _get_store(slug=None):
    if slug:
        return get_object_or_404(StoreSettings, slug=slug)
    return StoreSettings.objects.first()


def home_view(request):
    store = _get_store()
    if not store:
        return render(request, "store/empty_home.html")
    products = Product.objects.filter(store=store, is_active=True)
    featured = products.filter(is_featured=True)[:4]
    products = products[:12]
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

    from django.db.models import Avg, Count
    review_stats = product.reviews.aggregate(avg=Avg("rating"), count=Count("id"))
    avg_rating = round(review_stats["avg"] or 0)
    review_count = review_stats["count"]

    return render(request, "store/product_detail.html", {
        "store": store,
        "product": product,
        "avg_rating": avg_rating,
        "review_count": review_count,
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

    # 🔐 OWNERSHIP CHECK — halaman konfirmasi berisi PII pembeli
    # (nama, telepon, alamat) + snap_token. Hanya pemilik order yg
    # punya access_token (SK √2). Bukan pemilik => 404 (tidak
    # membocorkan keberadaan order).
    supplied = request.GET.get("token", "")
    if not order.access_token or not supplied or not hmac.compare_digest(supplied, order.access_token):
        raise Http404("Pesanan tidak ditemukan.")

    # Payment context
    snap_url = (settings.MIDTRANS_SNAP_SANDBOX_URL
                if not settings.MIDTRANS_IS_PRODUCTION
                else settings.MIDTRANS_SNAP_URL)
    snap_token = ""
    if order.payment_status == "pending":
        payment = Payment.objects.filter(order=order).order_by("-created_at").first()
        if payment and payment.midtrans_token:
            snap_token = payment.midtrans_token

    return render(request, "store/order_confirmation.html", {
        "store": store,
        "order": order,
        "snap_url": snap_url,
        "snap_token": snap_token,
        "access_token": order.access_token,
    })
