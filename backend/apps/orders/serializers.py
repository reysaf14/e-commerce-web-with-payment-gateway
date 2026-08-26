"""Order serializers."""
from rest_framework import serializers
from .models import Order, OrderItem


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
