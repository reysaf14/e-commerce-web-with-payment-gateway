"""Customer: CRM data. Auto-populated from checkout."""

from django.db import models


class Customer(models.Model):
    store = models.ForeignKey("store.StoreSettings", on_delete=models.CASCADE, related_name="customers")
    full_name = models.CharField(max_length=150)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=10, blank=True, null=True)
    total_spent = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    order_count = models.IntegerField(default=0)
    notes = models.TextField(blank=True, null=True, help_text="Merchant notes about this customer")
    last_order_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "customers"
        ordering = ["-last_order_at"]
        constraints = [
            models.UniqueConstraint(fields=["store", "phone"], name="unique_customer_phone_per_store"),
        ]
        indexes = [
            models.Index(fields=["store", "last_order_at"], name="idx_customer_last_order"),
        ]

    def __str__(self):
        return f"{self.full_name} ({self.phone})"
