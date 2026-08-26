"""Dashboard views — merchant panel."""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta

from apps.store.models import StoreSettings
from apps.products.models import Product, Category, ProductImage
from apps.orders.models import Order, OrderItem
from apps.payments.models import Payment
from apps.customers.models import Customer
from .forms import ProductForm, StoreSettingsForm


def _get_store(user):
    return get_object_or_404(StoreSettings, user=user)


# ── Auth ──────────────────────────────────────────────────

def dash_login(request):
    if request.user.is_authenticated:
        return redirect("dash-overview")
    if request.method == "POST":
        email = request.POST.get("username", "")
        password = request.POST.get("password", "")
        user = authenticate(request, email=email, password=password)
        if user:
            login(request, user)
            return redirect("dash-overview")
        messages.error(request, "Email atau password salah.")
    return render(request, "dashboard/login.html", {"active": "login"})


def dash_logout(request):
    logout(request)
    return redirect("dash-login")


# ── Overview ──────────────────────────────────────────────

@login_required(login_url="/dashboard/login/")
def overview(request):
    store = _get_store(request.user)
    today = timezone.now().date()

    stats = {
        "orders_today": Order.objects.filter(store=store, created_at__date=today).count(),
        "pending_payment": Order.objects.filter(store=store, payment_status="pending").count(),
        "total_revenue": Order.objects.filter(store=store, payment_status="paid").aggregate(total=Sum("total_amount"))["total"] or 0,
        "total_products": Product.objects.filter(store=store).count(),
    }

    recent_orders = Order.objects.filter(store=store).order_by("-created_at")[:10]
    top_products = Product.objects.filter(store=store, is_active=True).order_by("-stock")[:5]

    return render(request, "dashboard/overview.html", {
        "store": store, "active": "overview",
        "stats": stats, "recent_orders": recent_orders, "top_products": top_products,
    })


# ── Orders ────────────────────────────────────────────────

@login_required(login_url="/dashboard/login/")
def orders_list(request):
    store = _get_store(request.user)
    orders = Order.objects.filter(store=store).order_by("-created_at")
    return render(request, "dashboard/orders.html", {
        "store": store, "active": "orders", "orders": orders,
    })


@login_required(login_url="/dashboard/login/")
def order_detail(request, order_number):
    store = _get_store(request.user)
    order = get_object_or_404(Order, order_number=order_number, store=store)
    status_choices = Order.STATUS_CHOICES
    return render(request, "dashboard/order_detail.html", {
        "store": store, "active": "orders", "order": order, "status_choices": status_choices,
    })


@login_required(login_url="/dashboard/login/")
def order_update_status(request, order_number):
    store = _get_store(request.user)
    order = get_object_or_404(Order, order_number=order_number, store=store)
    if request.method == "POST":
        new_status = request.POST.get("status")
        valid_statuses = [c[0] for c in Order.STATUS_CHOICES]
        if new_status in valid_statuses:
            order.status = new_status
            order.save()
            messages.success(request, f"Status pesanan {order.order_number} diperbarui.")
    return redirect("dash-order-detail", order_number=order_number)


# ── Products ──────────────────────────────────────────────

@login_required(login_url="/dashboard/login/")
def products_list(request):
    store = _get_store(request.user)
    products = Product.objects.filter(store=store).order_by("-created_at")
    return render(request, "dashboard/products.html", {
        "store": store, "active": "products", "products": products,
    })


@login_required(login_url="/dashboard/login/")
def product_add(request):
    store = _get_store(request.user)
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.store = store
            product.save()
            messages.success(request, f"Produk '{product.name}' berhasil ditambahkan.")
            return redirect("dash-products")
    else:
        form = ProductForm()
    form.fields["category"].queryset = Category.objects.filter(store=store)
    return render(request, "dashboard/product_form.html", {
        "store": store, "active": "products", "form": form, "product": None,
    })


@login_required(login_url="/dashboard/login/")
def product_edit(request, product_id):
    store = _get_store(request.user)
    product = get_object_or_404(Product, id=product_id, store=store)
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f"Produk '{product.name}' berhasil diupdate.")
            return redirect("dash-products")
    else:
        form = ProductForm(instance=product)
    form.fields["category"].queryset = Category.objects.filter(store=store)
    return render(request, "dashboard/product_form.html", {
        "store": store, "active": "products", "form": form, "product": product,
    })


# ── Categories ────────────────────────────────────────────

@login_required(login_url="/dashboard/login/")
def categories_list(request):
    store = _get_store(request.user)
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        if name:
            from django.utils.text import slugify
            slug = slugify(name)
            # Ensure unique slug
            base_slug = slug
            counter = 1
            while Category.objects.filter(store=store, slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            Category.objects.create(store=store, name=name, slug=slug)
            messages.success(request, f"Kategori '{name}' ditambahkan.")
        return redirect("dash-categories")

    categories = Category.objects.filter(store=store).annotate(product_count=Count("products"))
    return render(request, "dashboard/categories.html", {
        "store": store, "active": "categories", "categories": categories,
    })


@login_required(login_url="/dashboard/login/")
def category_delete(request, category_id):
    store = _get_store(request.user)
    cat = get_object_or_404(Category, id=category_id, store=store)
    if request.method == "POST":
        cat.delete()
        messages.success(request, f"Kategori '{cat.name}' dihapus.")
    return redirect("dash-categories")


# ── Settings ──────────────────────────────────────────────

@login_required(login_url="/dashboard/login/")
def settings_view(request):
    store = _get_store(request.user)
    if request.method == "POST":
        form = StoreSettingsForm(request.POST, instance=store)
        if form.is_valid():
            form.save()
            messages.success(request, "Pengaturan toko berhasil disimpan.")
            return redirect("dash-settings")
    else:
        form = StoreSettingsForm(instance=store)
    return render(request, "dashboard/settings.html", {
        "store": store, "active": "settings", "form": form,
    })


# ── Customers ─────────────────────────────────────────────

@login_required(login_url="/dashboard/login/")
def customers_list(request):
    store = _get_store(request.user)
    customers = Customer.objects.filter(store=store)
    return render(request, "dashboard/customers.html", {
        "store": store, "active": "customers", "customers": customers,
    })
