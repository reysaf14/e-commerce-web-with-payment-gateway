"""Public storefront views."""
from rest_framework import generics, permissions
from .models import StoreSettings
from .serializers import StorePublicSerializer


class StorePublicView(generics.RetrieveAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = StorePublicSerializer
    lookup_field = "slug"

    def get_queryset(self):
        return StoreSettings.objects.all()
