"""Product serializers."""
from rest_framework import serializers
from .models import Product, Category, Variant, ProductImage


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug", "sort_order"]


class VariantSerializer(serializers.ModelSerializer):
    display_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    in_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = Variant
        fields = ["id", "name", "sku", "price_override", "stock", "is_active", "display_price", "in_stock"]


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "image_url", "sort_order", "alt_text"]


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    variants = VariantSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    display_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    in_stock = serializers.BooleanField(read_only=True)
    thumbnail = serializers.ImageField(read_only=True)

    class Meta:
        model = Product
        fields = ["id", "name", "slug", "description", "price", "is_active",
                  "is_featured", "total_sold", "category", "variants", "images",
                  "display_price", "in_stock", "thumbnail", "created_at", "updated_at"]


class ProductListSerializer(serializers.ModelSerializer):
    thumbnail = serializers.ImageField(read_only=True)
    in_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = Product
        fields = ["id", "name", "slug", "price", "thumbnail", "in_stock", "is_featured", "created_at"]
