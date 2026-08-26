"""Review serializers."""
from rest_framework import serializers
from .models import ProductReview, Wishlist


class ReviewSerializer(serializers.ModelSerializer):
    display_name = serializers.CharField(read_only=True)

    class Meta:
        model = ProductReview
        fields = ["id", "product", "rating", "comment", "is_anonymous", "display_name", "created_at"]
        read_only_fields = ["id", "display_name", "created_at"]


class WishlistSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    product_slug = serializers.CharField(source="product.slug", read_only=True)

    class Meta:
        model = Wishlist
        fields = ["id", "product", "product_name", "product_slug", "created_at"]
        read_only_fields = ["id", "product_name", "product_slug", "created_at"]
