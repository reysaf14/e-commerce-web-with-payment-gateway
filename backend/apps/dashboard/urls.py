"""Dashboard URLs."""

from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.dash_login, name="dash-login"),
    path("logout/", views.dash_logout, name="dash-logout"),
    path("", views.overview, name="dash-overview"),
    path("orders/", views.orders_list, name="dash-orders"),
    path("orders/<str:order_number>/", views.order_detail, name="dash-order-detail"),
    path("orders/<str:order_number>/update-status/", views.order_update_status, name="dash-order-update-status"),
    path("products/", views.products_list, name="dash-products"),
    path("products/add/", views.product_add, name="dash-product-add"),
    path("products/<int:product_id>/edit/", views.product_edit, name="dash-product-edit"),
    path("categories/", views.categories_list, name="dash-categories"),
    path("categories/<int:category_id>/delete/", views.category_delete, name="dash-category-delete"),
    path("settings/", views.settings_view, name="dash-settings"),
    path("customers/", views.customers_list, name="dash-customers"),
]
