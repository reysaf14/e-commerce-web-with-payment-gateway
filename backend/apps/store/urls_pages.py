"""Web page URLs — storefront pages."""

from django.urls import path
from . import views_pages

urlpatterns = [
    path("", views_pages.home_view, name="store-home"),
    path("catalog/", views_pages.catalog_view, name="store-catalog"),
    path("cart/", views_pages.cart_view, name="store-cart"),
    path("checkout/", views_pages.checkout_view, name="store-checkout"),
    path("order/<str:order_number>/", views_pages.order_confirmation_view, name="store-order-confirmation"),
    path("<slug:slug>/", views_pages.product_detail_view, name="store-product-detail"),
]
