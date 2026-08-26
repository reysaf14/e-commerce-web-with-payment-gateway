"""Payment URLs."""

from django.urls import path
from . import views

urlpatterns = [
    path("create/", views.create_payment, name="payment-create"),
    path("webhook/", views.webhook_view, name="payment-webhook"),
    path("<str:order_number>/status/", views.payment_status_view, name="payment-status"),
]
