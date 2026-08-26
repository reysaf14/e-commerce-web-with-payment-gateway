"""Review & Wishlist views."""

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.db import IntegrityError
from .models import ProductReview, Wishlist
from .serializers import ReviewSerializer, WishlistSerializer


# ── Reviews ───────────────────────────────────────────────

class ReviewListCreateView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        product_id = self.kwargs.get("product_id")
        return ProductReview.objects.filter(product_id=product_id)

    def perform_create(self, serializer):
        product_id = self.kwargs["product_id"]
        serializer.save(product_id=product_id)


# ── Wishlist ──────────────────────────────────────────────

def _get_session_id(request):
    sid = request.session.session_key
    if not sid:
        request.session.create()
        sid = request.session.session_key
    return sid


class WishlistListView(generics.ListAPIView):
    serializer_class = WishlistSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Wishlist.objects.filter(session_id=_get_session_id(self.request))


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def wishlist_toggle(request):
    """Toggle wishlist: add if not exists, remove if exists."""
    product_id = request.data.get("product")
    if not product_id:
        return Response({"error": "product wajib diisi."}, status=status.HTTP_400_BAD_REQUEST)

    session_id = _get_session_id(request)

    try:
        wl = Wishlist.objects.get(session_id=session_id, product_id=product_id)
        wl.delete()
        return Response({"action": "removed", "wishlisted": False})
    except Wishlist.DoesNotExist:
        try:
            Wishlist.objects.create(session_id=session_id, product_id=product_id)
            return Response({"action": "added", "wishlisted": True})
        except IntegrityError:
            return Response({"error": "Sudah ada di wishlist."}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def wishlist_check(request, product_id):
    """Check if product is in wishlist."""
    session_id = _get_session_id(request)
    exists = Wishlist.objects.filter(session_id=session_id, product_id=product_id).exists()
    return Response({"wishlisted": exists})
