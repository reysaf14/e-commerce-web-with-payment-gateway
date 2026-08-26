"""Cart URLs."""
from django.urls import path
from . import views

urlpatterns = [
    path("", views.CartView.as_view(), name="cart-detail"),
    path("items/", views.AddCartItemView.as_view(), name="cart-add-item"),
]
