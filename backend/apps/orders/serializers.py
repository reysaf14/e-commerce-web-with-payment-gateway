"""Order serializers."""

from rest_framework import serializers
from .models import Order, OrderItem
from apps.cart.models import Cart


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["id", "product_name", "variant_name", "unit_price", "quantity", "subtotal"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Order
        fields = ["id", "order_number", "status", "status_display", "subtotal", "shipping_cost",
                  "total_amount", "shipping_name", "shipping_phone", "shipping_address",
                  "payment_method", "payment_status", "tracking_number", "items", "created_at", "updated_at"]


class CheckoutSerializer(serializers.Serializer):
    shipping_name = serializers.CharField(max_length=150)
    shipping_phone = serializers.CharField(max_length=20)
    shipping_address = serializers.CharField()
    shipping_city = serializers.CharField(max_length=100)
    shipping_postal_code = serializers.CharField(max_length=10, required=False, allow_blank=True)
    note_to_seller = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        session_id = self.context["request"].session.session_key
        if not session_id:
            raise serializers.ValidationError({"cart": "Keranjang kosong."})
        try:
            cart = Cart.objects.get(session_id=session_id)
        except Cart.DoesNotExist:
            raise serializers.ValidationError({"cart": "Keranjang kosong."})
        if cart.items.count() == 0:
            raise serializers.ValidationError({"cart": "Keranjang kosong."})
        for item in cart.items.select_related("variant"):
            if item.variant.stock < item.quantity:
                raise serializers.ValidationError(
                    {"stock": f"Stok {item.variant.product.name} - {item.variant.name} tidak cukup."}
                )
        attrs["cart"] = cart
        attrs["store"] = cart.items.first().variant.product.store
        return attrs
