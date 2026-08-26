"""Review views."""
from rest_framework import generics, permissions
from .models import ProductReview, Wishlist
from .serializers import ReviewSerializer, WishlistSerializer


class ReviewViewSet(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        product_id = self.kwargs.get("product_id")
        return ProductReview.objects.filter(product_id=product_id)


class WishlistView(generics.ListCreateAPIView):
    serializer_class = WishlistSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        session_id = self.request.session.session_key or ""
        return Wishlist.objects.filter(session_id=session_id)
