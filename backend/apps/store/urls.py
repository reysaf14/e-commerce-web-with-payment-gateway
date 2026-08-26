"""Store settings URLs (merchant)."""
from django.urls import path
from . import views

urlpatterns = [
    path("", views.StoreSettingsView.as_view(), name="store-settings"),
]
