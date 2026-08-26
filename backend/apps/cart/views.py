"""Cart views."""
from rest_framework import generics, permissions
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer


class CartView(generics.RetrieveDestroyAPIView):
    serializer_class = CartSerializer
    permission_classes = [permissions.AllowAny]

    def get_object(self):
        session_id = self.request.session.session_key
        if not session_id:
            self.request.session.create()
            session_id = self.request.session.session_key
        cart, _ = Cart.objects.get_or_create(session_id=session_id)
        return cart


class AddCartItemView(generics.CreateAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        session_id = self.request.session.session_key
        if not session_id:
            self.request.session.create()
            session_id = self.request.session.session_key
        cart, _ = Cart.objects.get_or_create(session_id=session_id)
        serializer.save(cart=cart)
