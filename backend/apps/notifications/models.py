"""Notification: in-app notifications for merchant and customer."""

from django.db import models


class Notification(models.Model):
    class RecipientType(models.TextChoices):
        MERCHANT = "merchant", "Merchant"
        CUSTOMER = "customer", "Customer"

    store = models.ForeignKey("store.StoreSettings", on_delete=models.CASCADE, related_name="notifications")
    recipient_type = models.CharField(max_length=20, choices=RecipientType.choices)
    recipient_id = models.PositiveBigIntegerField()
    type = models.CharField(max_length=30)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "notifications"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["recipient_type", "recipient_id", "is_read"], name="idx_notif_recipient_unread"),
            models.Index(fields=["store", "created_at"], name="idx_notif_store_date"),
        ]

    def __str__(self):
        return f"[{self.type}] {self.title}"
