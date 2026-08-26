"""Payment serializers."""
from rest_framework import serializers
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ["id", "midtrans_order_id", "amount", "payment_type", "status", "fraud_status", "paid_at", "created_at"]
