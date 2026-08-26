"""Store settings serializers."""
from rest_framework import serializers
from .models import StoreSettings


class StoreSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreSettings
        fields = [
            "id", "store_name", "slug", "logo_url", "favicon_url",
            "description", "whatsapp_number", "email_contact", "instagram_handle",
            "return_policy", "shipping_policy", "shipping_method",
            "shipping_cost", "free_shipping_min",
        ]
        read_only_fields = ["id"]


class StorePublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreSettings
        fields = ["store_name", "slug", "logo_url", "description",
                  "whatsapp_number", "email_contact", "instagram_handle",
                  "return_policy", "shipping_policy"]
