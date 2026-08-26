"""Payment views."""
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def webhook_view(request):
    """Midtrans webhook handler. Will be implemented in M5."""
    return Response({"status": "ok"}, status=status.HTTP_200_OK)
