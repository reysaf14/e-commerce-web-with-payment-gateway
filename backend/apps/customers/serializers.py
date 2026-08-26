"""Customer serializers."""
from rest_framework import serializers
from .models import Customer


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ["id", "full_name", "email", "phone", "total_spent", "order_count", "last_order_at", "created_at"]
        read_only_fields = ["id", "total_spent", "order_count", "last_order_at", "created_at"]
