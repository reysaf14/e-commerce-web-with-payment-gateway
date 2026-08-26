"""Review & Wishlist URLs."""

from django.urls import path
from . import views

urlpatterns = [
    path("wishlist/", views.WishlistListView.as_view(), name="wishlist-list"),
    path("wishlist/toggle/", views.wishlist_toggle, name="wishlist-toggle"),
    path("wishlist/check/<int:product_id>/", views.wishlist_check, name="wishlist-check"),
    path("<int:product_id>/", views.ReviewListCreateView.as_view(), name="review-list"),
]
