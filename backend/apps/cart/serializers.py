"""Cart serializers."""

from rest_framework import serializers
from .models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    variant_name = serializers.CharField(source="variant.name", read_only=True)
    product_name = serializers.CharField(source="variant.product.name", read_only=True)
    product_slug = serializers.CharField(source="variant.product.slug", read_only=True)
    unit_price = serializers.DecimalField(source="variant.display_price", max_digits=10, decimal_places=2, read_only=True)
    line_total = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    in_stock = serializers.BooleanField(source="variant.in_stock", read_only=True)
    max_stock = serializers.IntegerField(source="variant.stock", read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ["id", "variant", "variant_name", "product_name", "product_slug",
                  "unit_price", "quantity", "line_total", "in_stock", "max_stock", "image_url"]

    def get_image_url(self, obj):
        img = obj.variant.product.images.filter(sort_order=0).first()
        if img and img.image_url:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(img.image_url.url)
            return img.image_url.url
        return None

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("Jumlah minimal 1.")
        return value


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    item_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Cart
        fields = ["id", "items", "subtotal", "item_count", "updated_at"]
