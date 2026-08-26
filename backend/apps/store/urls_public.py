"""Public storefront URLs."""
from django.urls import path
from . import views_public

urlpatterns = [
    path("", views_public.StorePublicView.as_view(), name="store-public"),
]
