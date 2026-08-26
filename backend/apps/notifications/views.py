"""Notification views."""
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .models import Notification
from .serializers import NotificationSerializer


class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(
            store=self.request.user.store_settings,
            recipient_type="merchant",
            recipient_id=self.request.user.id,
        )


@api_view(["PATCH"])
@permission_classes([permissions.IsAuthenticated])
def mark_as_read_view(request, pk):
    try:
        notif = Notification.objects.get(pk=pk, store=request.user.store_settings)
        notif.is_read = True
        notif.save()
        return Response({"status": "ok"})
    except Notification.DoesNotExist:
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)
