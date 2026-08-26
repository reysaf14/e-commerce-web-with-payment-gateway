"""Customer serializers."""

from rest_framework import serializers
from .models import Customer


class CustomerSerializer(serializers.ModelSerializer):
    order_count_display = serializers.IntegerField(source="order_count", read_only=True)

    class Meta:
        model = Customer
        fields = ["id", "full_name", "email", "phone", "address", "city", "postal_code",
                  "total_spent", "order_count", "order_count_display", "notes", "last_order_at", "created_at"]
        read_only_fields = ["id", "total_spent", "order_count", "last_order_at", "created_at"]
