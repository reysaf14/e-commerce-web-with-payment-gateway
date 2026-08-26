"""Product catalog: Category, Product, Variant, ProductImage."""

from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    store = models.ForeignKey("store.StoreSettings", on_delete=models.CASCADE, related_name="categories")
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120)
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "categories"
        ordering = ["sort_order", "name"]
        constraints = [
            models.UniqueConstraint(fields=["store", "slug"], name="unique_category_slug_per_store"),
        ]

    def __str__(self):
        return f"{self.name} ({self.store.store_name})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    store = models.ForeignKey("store.StoreSettings", on_delete=models.CASCADE, related_name="products")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="products")
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=280)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    total_sold = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "products"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["store", "slug"], name="unique_product_slug_per_store"),
        ]
        indexes = [
            models.Index(fields=["store", "is_active", "created_at"], name="idx_product_catalog"),
            models.Index(fields=["store", "is_featured"], name="idx_product_featured"),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def display_price(self):
        first = self.variants.filter(is_active=True).first()
        if first and first.price_override is not None:
            return first.price_override
        return self.price

    @property
    def min_price(self):
        prices = self.variants.filter(is_active=True).values_list("price_override", flat=True)
        valid = [p for p in prices if p is not None]
        return min(valid) if valid else self.price

    @property
    def in_stock(self):
        return self.variants.filter(is_active=True, stock__gt=0).exists()

    @property
    def thumbnail(self):
        img = self.images.filter(sort_order=0).first()
        return img.image_url if img else None


class Variant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")
    name = models.CharField(max_length=150)
    sku = models.CharField(max_length=50, blank=True, null=True)
    price_override = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "variants"
        indexes = [
            models.Index(fields=["product", "is_active"], name="idx_variant_active"),
        ]

    def __str__(self):
        return f"{self.product.name} - {self.name}"

    @property
    def display_price(self):
        return self.price_override if self.price_override is not None else self.product.price

    @property
    def in_stock(self):
        return self.stock > 0


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image_url = models.ImageField(upload_to="products/")
    sort_order = models.IntegerField(default=0)
    alt_text = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "product_images"
        ordering = ["sort_order"]

    def __str__(self):
        return f"Image {self.sort_order} of {self.product.name}"
