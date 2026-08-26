"""Product views."""

from rest_framework import viewsets, permissions, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Q
from .models import Product, Category, Variant, ProductImage
from .serializers import (
    ProductSerializer, ProductListSerializer,
    CategorySerializer, VariantSerializer, ProductImageSerializer,
)


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Category.objects.filter(store=self.request.user.store_settings)


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Product.objects.filter(store=self.request.user.store_settings)
        cat_id = self.request.query_params.get("category")
        if cat_id:
            qs = qs.filter(category_id=cat_id)
        active = self.request.query_params.get("active")
        if active is not None:
            qs = qs.filter(is_active=active.lower() in ("true", "1"))
        q = self.request.query_params.get("q")
        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q))
        sort = self.request.query_params.get("sort", "newest")
        sort_map = {
            "newest": "-created_at", "oldest": "created_at",
            "price_asc": "price", "price_desc": "-price",
            "popular": "-total_sold",
        }
        return qs.order_by(sort_map.get(sort, "-created_at"))

    def get_serializer_class(self):
        if self.action == "list":
            return ProductListSerializer
        return ProductSerializer

    # ── Variant CRUD ────────────────────────────────────────

    @action(detail=True, methods=["get", "post"], url_path="variants")
    def variants(self, request, pk=None):
        product = self.get_object()
        if request.method == "GET":
            serializer = VariantSerializer(product.variants.all(), many=True)
            return Response(serializer.data)
        serializer = VariantSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(product=product)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get", "put", "patch", "delete"],
            url_path=r"variants/(?P<variant_id>\d+)")
    def variant_detail(self, request, pk=None, variant_id=None):
        product = self.get_object()
        try:
            variant = product.variants.get(pk=variant_id)
        except Variant.DoesNotExist:
            return Response({"error": "Varian tidak ditemukan"}, status=status.HTTP_404_NOT_FOUND)
        if request.method == "GET":
            return Response(VariantSerializer(variant).data)
        if request.method == "DELETE":
            variant.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer = VariantSerializer(variant, data=request.data, partial=(request.method == "PATCH"))
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    # ── Image CRUD ──────────────────────────────────────────

    @action(detail=True, methods=["get", "post"], url_path="images",
            parser_classes=[MultiPartParser, FormParser])
    def images(self, request, pk=None):
        product = self.get_object()
        if request.method == "GET":
            serializer = ProductImageSerializer(product.images.all(), many=True,
                                                 context={"request": request})
            return Response(serializer.data)
        if product.images.count() >= 8:
            return Response({"error": "Maksimal 8 gambar per produk."},
                            status=status.HTTP_400_BAD_REQUEST)
        serializer = ProductImageSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save(product=product)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["delete"], url_path=r"images/(?P<image_id>\d+)")
    def image_delete(self, request, pk=None, image_id=None):
        product = self.get_object()
        try:
            image = product.images.get(pk=image_id)
        except ProductImage.DoesNotExist:
            return Response({"error": "Gambar tidak ditemukan"}, status=status.HTTP_404_NOT_FOUND)
        image.image_url.delete(save=False)
        image.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ── Public Catalog ─────────────────────────────────────────

class PublicCatalogView(generics.ListAPIView):
    serializer_class = ProductListSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        from apps.store.models import StoreSettings
        slug = self.kwargs.get("store_slug")
        try:
            store = StoreSettings.objects.get(slug=slug)
        except StoreSettings.DoesNotExist:
            return Product.objects.none()
        qs = Product.objects.filter(store=store, is_active=True)
        cat_id = self.request.query_params.get("category")
        if cat_id:
            qs = qs.filter(category_id=cat_id)
        q = self.request.query_params.get("q")
        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q))
        sort = self.request.query_params.get("sort", "newest")
        sort_map = {
            "newest": "-created_at", "oldest": "created_at",
            "price_asc": "price", "price_desc": "-price",
            "popular": "-total_sold",
        }
        return qs.order_by(sort_map.get(sort, "-created_at"))


class PublicProductDetailView(generics.RetrieveAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "slug"

    def get_queryset(self):
        from apps.store.models import StoreSettings
        slug = self.kwargs.get("store_slug")
        try:
            store = StoreSettings.objects.get(slug=slug)
        except StoreSettings.DoesNotExist:
            return Product.objects.none()
        return Product.objects.filter(store=store, is_active=True)
