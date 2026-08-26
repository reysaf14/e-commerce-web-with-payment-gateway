"""ProductReview & Wishlist."""

from django.db import models


class ProductReview(models.Model):
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE, related_name="reviews")
    order_item = models.OneToOneField("orders.OrderItem", on_delete=models.CASCADE, related_name="review")
    rating = models.IntegerField()
    comment = models.TextField(blank=True, null=True)
    is_anonymous = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "product_reviews"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Review {self.rating}/5 - {self.product.name}"

    def save(self, *args, **kwargs):
        if not 1 <= self.rating <= 5:
            raise ValueError("Rating harus antara 1 dan 5")
        super().save(*args, **kwargs)

    @property
    def display_name(self):
        if self.is_anonymous:
            return "Anonim"
        return self.order_item.order.customer.full_name


class Wishlist(models.Model):
    session_id = models.CharField(max_length=64)
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE, related_name="wishlisted_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "wishlists"
        constraints = [
            models.UniqueConstraint(fields=["session_id", "product"], name="unique_wishlist_per_session"),
        ]

    def __str__(self):
        return f"Wishlist: {self.product.name} ({self.session_id})"
