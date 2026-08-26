"""Public catalog URLs — storefront."""

from django.urls import path
from . import views

urlpatterns = [
    path("", views.PublicCatalogView.as_view(), name="public-catalog"),
    path("<slug:slug>/", views.PublicProductDetailView.as_view(), name="public-product-detail"),
]
