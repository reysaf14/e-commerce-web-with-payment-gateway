"""Cart & CartItem: persistent shopping cart."""

from django.db import models


class Cart(models.Model):
    session_id = models.CharField(max_length=64, blank=True, null=True)
    user = models.OneToOneField("authentication.User", on_delete=models.CASCADE, null=True, blank=True, related_name="cart")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "carts"

    def __str__(self):
        return f"Cart: {self.user.email}" if self.user else f"Cart: {self.session_id}"

    @property
    def subtotal(self):
        return sum(item.line_total for item in self.items.all())

    @property
    def item_count(self):
        return self.items.count()


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    variant = models.ForeignKey("products.Variant", on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "cart_items"
        constraints = [
            models.UniqueConstraint(fields=["cart", "variant"], name="unique_cart_item_per_variant"),
        ]

    def __str__(self):
        return f"{self.variant.name} x{self.quantity}"

    @property
    def line_total(self):
        return self.variant.display_price * self.quantity
