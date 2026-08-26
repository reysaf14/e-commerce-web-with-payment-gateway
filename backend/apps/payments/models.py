"""Payment: record of Midtrans transactions."""

from django.db import models


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"
        EXPIRED = "expired", "Expired"

    order = models.ForeignKey("orders.Order", on_delete=models.CASCADE, related_name="payments")
    midtrans_order_id = models.CharField(max_length=100)
    midtrans_token = models.CharField(max_length=255, blank=True, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_type = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    fraud_status = models.CharField(max_length=20, blank=True, null=True)
    raw_response = models.JSONField(blank=True, null=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "payments"
        indexes = [
            models.Index(fields=["midtrans_order_id"], name="idx_payment_midtrans_id"),
            models.Index(fields=["order", "status"], name="idx_payment_order_status"),
            models.Index(fields=["status"], name="idx_payment_status"),
        ]

    def __str__(self):
        return f"Payment {self.midtrans_order_id} ({self.get_status_display()})"
