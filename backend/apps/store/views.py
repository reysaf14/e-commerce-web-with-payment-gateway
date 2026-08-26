"""Store settings views (merchant only)."""
from rest_framework import generics, permissions
from .models import StoreSettings
from .serializers import StoreSettingsSerializer
from apps.authentication.permissions import IsMerchant


class StoreSettingsView(generics.RetrieveUpdateAPIView):
    serializer_class = StoreSettingsSerializer
    permission_classes = [permissions.IsAuthenticated, IsMerchant]

    def get_object(self):
        return self.request.user.store_settings
