"""StoreSettings: one-to-one with User. Branding & operational config."""

from django.db import models


class StoreSettings(models.Model):
    class ShippingMethod(models.TextChoices):
        FLAT_RATE = "flat_rate", "Flat Rate"
        PER_CITY = "per_kota", "Per Kota"
        FREE_ONS = "gratis_ons", "Gratis Ongkir Minimum"

    user = models.OneToOneField(
        "authentication.User",
        on_delete=models.CASCADE,
        related_name="store_settings",
    )
    store_name = models.CharField(max_length=200, verbose_name="Nama Toko")
    slug = models.SlugField(max_length=200, unique=True)
    logo_url = models.ImageField(upload_to="store/logos/", blank=True, null=True)
    favicon_url = models.ImageField(upload_to="store/favicons/", blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    whatsapp_number = models.CharField(max_length=20, blank=True, null=True)
    email_contact = models.EmailField(blank=True, null=True)
    instagram_handle = models.CharField(max_length=100, blank=True, null=True)
    return_policy = models.TextField(blank=True, null=True)
    shipping_policy = models.TextField(blank=True, null=True)
    shipping_method = models.CharField(
        max_length=20, choices=ShippingMethod.choices, default=ShippingMethod.FLAT_RATE,
    )
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    free_shipping_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "store_settings"

    def __str__(self):
        return self.store_name
