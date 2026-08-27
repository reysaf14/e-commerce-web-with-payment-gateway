"""Order & OrderItem: order management with state machine."""

import datetime
from django.db import models


class Order(models.Model):
    class Status(models.TextChoices):
        WAITING_PAYMENT = "waiting_payment", "Menunggu Bayar"
        PAID = "paid", "Dibayar"
        SHIPPED = "shipped", "Dikirim"
        DELIVERED = "delivered", "Diterima"
        COMPLETED = "completed", "Selesai"
        FAILED = "failed", "Gagal"
        EXPIRED = "expired", "Expired"
        CANCELED = "canceled", "Dibatalkan"

    class PaymentStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"
        EXPIRED = "expired", "Expired"

    store = models.ForeignKey("store.StoreSettings", on_delete=models.CASCADE, related_name="orders")
    customer = models.ForeignKey("customers.Customer", on_delete=models.CASCADE, related_name="orders")
    order_number = models.CharField(max_length=30, unique=True)
    session_id = models.CharField(max_length=64, blank=True, null=True, help_text="Session cookie yang membuat order (ownership check)")
    access_token = models.CharField(
        max_length=64, blank=True, null=True, db_index=True,
        help_text="Token acak tak-tebakan (UUID) sbg kredensial akses order (anti-IDOR & anti-session-fixation)",
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.WAITING_PAYMENT)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    shipping_name = models.CharField(max_length=150)
    shipping_phone = models.CharField(max_length=20)
    shipping_address = models.TextField()
    shipping_city = models.CharField(max_length=100)
    shipping_postal_code = models.CharField(max_length=10, blank=True, null=True)
    note_to_seller = models.TextField(blank=True, null=True)
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    payment_status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    shipping_courier = models.CharField(max_length=50, blank=True, null=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "orders"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["store", "status"], name="idx_order_store_status"),
            models.Index(fields=["store", "created_at"], name="idx_order_store_date"),
            models.Index(fields=["customer"], name="idx_order_customer"),
            models.Index(fields=["payment_status"], name="idx_order_payment"),
        ]

    def __str__(self):
        return f"{self.order_number} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self._generate_order_number()
        if not self.access_token:
            import secrets
            self.access_token = secrets.token_urlsafe(32)
        super().save(*args, **kwargs)

    def _generate_order_number(self):
        today = datetime.date.today().strftime("%Y%m%d")
        last = Order.objects.filter(order_number__startswith=f"TKN-{today}").order_by("-order_number").first()
        seq = int(last.order_number.split("-")[-1]) + 1 if last else 1
        return f"TKN-{today}-{seq:04d}"

    @property
    def can_be_canceled(self):
        return self.status == self.Status.WAITING_PAYMENT

    @property
    def can_be_shipped(self):
        return self.status == self.Status.PAID


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey("products.Product", on_delete=models.SET_NULL, null=True, blank=True)
    variant = models.ForeignKey("products.Variant", on_delete=models.SET_NULL, null=True, blank=True)
    product_name = models.CharField(max_length=255)
    variant_name = models.CharField(max_length=150, blank=True, null=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        db_table = "order_items"

    def __str__(self):
        return f"{self.product_name} x{self.quantity}"

    def save(self, *args, **kwargs):
        if not self.subtotal:
            self.subtotal = self.unit_price * self.quantity
        super().save(*args, **kwargs)
