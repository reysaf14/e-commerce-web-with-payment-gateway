"""
Root URL configuration.
All API endpoints use /api/v1/ prefix for versioning.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin (useful for dev & fallback dashboard)
    path("admin/", admin.site.urls),

    # API v1
    path("api/v1/auth/", include("apps.authentication.urls")),
    path("api/v1/settings/", include("apps.store.urls")),
    path("api/v1/products/", include("apps.products.urls")),
    path("api/v1/categories/", include("apps.products.urls_categories")),
    path("api/v1/cart/", include("apps.cart.urls")),
    path("api/v1/checkout/", include("apps.orders.urls_checkout")),
    path("api/v1/orders/", include("apps.orders.urls")),
    path("api/v1/payments/", include("apps.payments.urls")),
    path("api/v1/customers/", include("apps.customers.urls")),
    path("api/v1/notifications/", include("apps.notifications.urls")),
    path("api/v1/reviews/", include("apps.reviews.urls")),
    path("api/v1/media/", include("apps.products.urls_media")),
    path("api/v1/store/", include("apps.store.urls_public")),

    # Web pages (storefront & merchant dashboard)
    path("", include("apps.store.urls_pages")),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
