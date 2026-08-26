"""Signals: auto-create StoreSettings when new merchant registers."""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify
from .models import User


@receiver(post_save, sender=User)
def create_store_settings(sender, instance, created, **kwargs):
    if created and instance.role == User.Role.MERCHANT:
        from apps.store.models import StoreSettings
        base_slug = slugify(instance.full_name.replace(" ", "-"))
        slug = base_slug
        counter = 1
        while StoreSettings.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        StoreSettings.objects.create(user=instance, store_name=f"Toko {instance.full_name}", slug=slug)
