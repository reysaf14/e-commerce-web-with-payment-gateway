"""Order URLs (merchant)."""
from django.urls import path
from . import views

urlpatterns = [
    path("", views.OrderListView.as_view(), name="order-list"),
    path("<str:order_number>/", views.OrderDetailView.as_view(), name="order-detail"),
]
