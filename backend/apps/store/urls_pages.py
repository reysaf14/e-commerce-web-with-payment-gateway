"""Web page URLs — storefront pages."""

from django.urls import path
from . import views_pages

urlpatterns = [
    path("", views_pages.home_view, name="store-home"),
    path("catalog/", views_pages.catalog_view, name="store-catalog"),
    path("<slug:slug>/", views_pages.product_detail_view, name="store-product-detail"),
]
