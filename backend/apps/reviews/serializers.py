"""Review serializers."""

from rest_framework import serializers
from .models import ProductReview, Wishlist


class ReviewSerializer(serializers.ModelSerializer):
    display_name = serializers.CharField(read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = ProductReview
        fields = ["id", "product", "product_name", "rating", "comment",
                  "is_anonymous", "display_name", "created_at"]
        read_only_fields = ["id", "display_name", "created_at"]

    def validate_rating(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError("Rating harus antara 1 dan 5.")
        return value


class WishlistSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    product_slug = serializers.CharField(source="product.slug", read_only=True)
    product_price = serializers.DecimalField(source="product.price", max_digits=10, decimal_places=2, read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Wishlist
        fields = ["id", "product", "product_name", "product_slug", "product_price", "image_url", "created_at"]
        read_only_fields = ["id", "product_name", "product_slug", "product_price", "image_url", "created_at"]

    def get_image_url(self, obj):
        img = obj.product.images.filter(sort_order=0).first()
        if img and img.image_url:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(img.image_url.url)
            return img.image_url.url
        return None
