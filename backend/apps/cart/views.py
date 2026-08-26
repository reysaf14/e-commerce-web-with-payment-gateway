"""Cart views."""

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.db import transaction
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer


def _get_or_create_cart(request):
    session_id = request.session.session_key
    if not session_id:
        request.session.create()
        session_id = request.session.session_key
    cart, _ = Cart.objects.get_or_create(session_id=session_id)
    return cart


class CartView(generics.RetrieveDestroyAPIView):
    serializer_class = CartSerializer
    permission_classes = [permissions.AllowAny]

    def get_object(self):
        return _get_or_create_cart(self.request)

    def delete(self, request, *args, **kwargs):
        """Clear entire cart."""
        cart = self.get_object()
        cart.items.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AddCartItemView(generics.CreateAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        cart = _get_or_create_cart(request)
        variant_id = request.data.get("variant")
        quantity = int(request.data.get("quantity", 1))

        # Check stock
        from apps.products.models import Variant
        try:
            variant = Variant.objects.get(pk=variant_id, is_active=True)
        except Variant.DoesNotExist:
            return Response({"error": "Varian tidak ditemukan."}, status=status.HTTP_400_BAD_REQUEST)

        if variant.stock < quantity:
            return Response({"error": "Stok tidak cukup."}, status=status.HTTP_400_BAD_REQUEST)

        # If item already in cart, increase quantity
        existing = CartItem.objects.filter(cart=cart, variant_id=variant_id).first()
        if existing:
            new_qty = existing.quantity + quantity
            if new_qty > variant.stock:
                return Response({"error": "Stok tidak cukup."}, status=status.HTTP_400_BAD_REQUEST)
            existing.quantity = new_qty
            existing.save()
            return Response(CartItemSerializer(existing, context={"request": request}).data, status=status.HTTP_200_OK)

        item = CartItem.objects.create(cart=cart, variant_id=variant_id, quantity=quantity)
        return Response(CartItemSerializer(item, context={"request": request}).data, status=status.HTTP_201_CREATED)


class CartItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        cart = _get_or_create_cart(self.request)
        return CartItem.objects.filter(cart=cart)

    def update(self, request, *args, **kwargs):
        item = self.get_object()
        quantity = int(request.data.get("quantity", item.quantity))
        if quantity < 1:
            item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        if quantity > item.variant.stock:
            return Response({"error": "Stok tidak cukup."}, status=status.HTTP_400_BAD_REQUEST)
        item.quantity = quantity
        item.save()
        return Response(CartItemSerializer(item, context={"request": request}).data)
