"""Customer views."""
from rest_framework import generics, permissions
from .models import Customer
from .serializers import CustomerSerializer


class CustomerListView(generics.ListAPIView):
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Customer.objects.filter(store=self.request.user.store_settings)


class CustomerDetailView(generics.RetrieveAPIView):
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Customer.objects.filter(store=self.request.user.store_settings)
