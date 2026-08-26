"""Notification services."""
from .models import Notification


def create_notification(store, recipient_type, recipient_id, notif_type, title, message):
    return Notification.objects.create(
        store=store, recipient_type=recipient_type, recipient_id=recipient_id,
        type=notif_type, title=title, message=message,
    )
