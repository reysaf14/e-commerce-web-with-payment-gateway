"""Product serializers."""

from rest_framework import serializers
from django.utils.text import slugify
from .models import Product, Category, Variant, ProductImage


# ── Category ───────────────────────────────────────────────

class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["id", "name", "slug", "sort_order", "product_count"]
        extra_kwargs = {"slug": {"required": False}}

    def get_product_count(self, obj):
        return obj.products.filter(is_active=True).count()

    def create(self, validated_data):
        slug = slugify(validated_data["name"])
        store = self.context["request"].user.store_settings
        if Category.objects.filter(store=store, slug=slug).exists():
            raise serializers.ValidationError({"name": "Kategori dengan nama ini sudah ada."})
        validated_data["slug"] = slug
        validated_data["store"] = store
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if "name" in validated_data:
            validated_data["slug"] = slugify(validated_data["name"])
        store = self.context["request"].user.store_settings
        new_slug = validated_data.get("slug", instance.slug)
        if Category.objects.filter(store=store, slug=new_slug).exclude(pk=instance.pk).exists():
            raise serializers.ValidationError({"name": "Kategori dengan nama ini sudah ada."})
        return super().update(instance, validated_data)


# ── Variant ────────────────────────────────────────────────

class VariantSerializer(serializers.ModelSerializer):
    display_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    in_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = Variant
        fields = ["id", "name", "sku", "price_override", "stock", "is_active",
                  "display_price", "in_stock", "created_at"]
        read_only_fields = ["id", "created_at"]

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("Stok tidak boleh negatif.")
        return value


# ── Product Image ──────────────────────────────────────────

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "image_url", "sort_order", "alt_text", "created_at"]
        read_only_fields = ["id", "created_at"]

    def validate_image_url(self, value):
        max_size_mb = 5
        if value.size > max_size_mb * 1024 * 1024:
            raise serializers.ValidationError(f"Ukuran gambar maksimal {max_size_mb}MB.")
        allowed_types = ["image/jpeg", "image/png", "image/webp"]
        if hasattr(value, "content_type") and value.content_type not in allowed_types:
            raise serializers.ValidationError("Format gambar harus JPEG, PNG, atau WebP.")
        return value


# ── Product ────────────────────────────────────────────────

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source="category", write_only=True,
        required=False, allow_null=True,
    )
    variants = VariantSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    display_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    in_stock = serializers.BooleanField(read_only=True)
    thumbnail = serializers.ImageField(read_only=True)

    class Meta:
        model = Product
        fields = [
            "id", "name", "slug", "description", "price", "is_active",
            "is_featured", "total_sold", "category", "category_id",
            "variants", "images", "display_price", "in_stock", "thumbnail",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "total_sold", "created_at", "updated_at"]
        extra_kwargs = {"slug": {"required": False}}

    def create(self, validated_data):
        store = self.context["request"].user.store_settings
        validated_data["store"] = store
        slug = slugify(validated_data["name"])
        if Product.objects.filter(store=store, slug=slug).exists():
            raise serializers.ValidationError({"name": "Produk dengan nama ini sudah ada."})
        validated_data["slug"] = slug
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if "name" in validated_data and "slug" not in validated_data:
            validated_data["slug"] = slugify(validated_data["name"])
        store = self.context["request"].user.store_settings
        new_slug = validated_data.get("slug", instance.slug)
        if Product.objects.filter(store=store, slug=new_slug).exclude(pk=instance.pk).exists():
            raise serializers.ValidationError({"name": "Produk dengan nama ini sudah ada."})
        return super().update(instance, validated_data)


class ProductListSerializer(serializers.ModelSerializer):
    thumbnail = serializers.SerializerMethodField()
    in_stock = serializers.BooleanField(read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True, default=None)
    variant_count = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ["id", "name", "slug", "price", "thumbnail", "category_name",
                  "in_stock", "is_featured", "variant_count", "total_sold", "created_at"]

    def get_thumbnail(self, obj):
        img = obj.images.filter(sort_order=0).first()
        if img and img.image_url:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(img.image_url.url)
            return img.image_url.url
        return None

    def get_variant_count(self, obj):
        return obj.variants.filter(is_active=True).count()
