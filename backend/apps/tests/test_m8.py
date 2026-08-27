"""M8 Unit Tests — Comprehensive test suite."""

import json
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from apps.store.models import StoreSettings
from apps.products.models import Category, Product, Variant

User = get_user_model()


def _setup_user(client, email="t@t.com", password="testpass123"):
    """Register a new user via API, return (token, store)."""
    res = client.post("/api/v1/auth/register/", {
        "email": email, "password": password, "full_name": email.split("@")[0]
    }, content_type="application/json")
    if res.status_code == 201:
        token = res.json()["tokens"]["access"]
        store = StoreSettings.objects.get(user__email=email)
        return token, store
    # Already exists — login instead
    res = client.post("/api/v1/auth/login/", {"email": email, "password": password},
                      content_type="application/json")
    token = res.json()["tokens"]["access"]
    store = StoreSettings.objects.get(user__email=email)
    return token, store


class AuthTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_register(self):
        res = self.client.post("/api/v1/auth/register/", {
            "email": "test@test.com", "password": "testpass123", "full_name": "Test User"
        }, content_type="application/json")
        self.assertEqual(res.status_code, 201)
        data = res.json()
        self.assertIn("tokens", data)
        self.assertIn("access", data["tokens"])
        self.assertEqual(data["user"]["email"], "test@test.com")
        self.assertTrue(StoreSettings.objects.filter(user__email="test@test.com").exists())

    def test_register_duplicate_email(self):
        User.objects.create_user(email="dup@test.com", password="test123")
        res = self.client.post("/api/v1/auth/register/", {
            "email": "dup@test.com", "password": "test12345"
        }, content_type="application/json")
        self.assertEqual(res.status_code, 400)

    def test_register_short_password(self):
        res = self.client.post("/api/v1/auth/register/", {
            "email": "short@test.com", "password": "123"
        }, content_type="application/json")
        self.assertEqual(res.status_code, 400)

    def test_login(self):
        User.objects.create_user(email="login@test.com", password="testpass123")
        res = self.client.post("/api/v1/auth/login/", {
            "email": "login@test.com", "password": "testpass123"
        }, content_type="application/json")
        self.assertEqual(res.status_code, 200)
        self.assertIn("tokens", res.json())
        self.assertIn("access", res.json()["tokens"])

    def test_login_wrong_password(self):
        User.objects.create_user(email="wrong@test.com", password="testpass123")
        res = self.client.post("/api/v1/auth/login/", {
            "email": "wrong@test.com", "password": "wrongpassword"
        }, content_type="application/json")
        self.assertEqual(res.status_code, 401)

    def test_me_unauthenticated(self):
        res = self.client.get("/api/v1/auth/me/")
        self.assertEqual(res.status_code, 401)

    def test_me_authenticated(self):
        token, _ = _setup_user(self.client, "me@test.com")
        res = self.client.get("/api/v1/auth/me/", HTTP_AUTHORIZATION=f"Bearer {token}")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["email"], "me@test.com")


class StoreSettingsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.token, self.store = _setup_user(self.client, "store@test.com")

    def test_get_settings(self):
        res = self.client.get("/api/v1/settings/", HTTP_AUTHORIZATION=f"Bearer {self.token}")
        self.assertEqual(res.status_code, 200)

    def test_update_settings(self):
        res = self.client.put("/api/v1/settings/", json.dumps({
            "store_name": "Toko Baru", "slug": "toko-baru",
        }), content_type="application/json", HTTP_AUTHORIZATION=f"Bearer {self.token}")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["store_name"], "Toko Baru")


class ProductTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.token, self.store = _setup_user(self.client, "prod@test.com")
        self.category = Category.objects.create(store=self.store, name="Hijab", slug="hijab")
        self.product = Product.objects.create(
            store=self.store, name="Hijab Pashmina", slug="hijab-pashmina",
            price=85000, category=self.category
        )
        self.variant = Variant.objects.create(
            product=self.product, name="Pink", stock=10, sku="HP-PINK"
        )

    def test_create_category(self):
        res = self.client.post("/api/v1/products/categories/", json.dumps({
            "name": "Gamis"
        }), content_type="application/json", HTTP_AUTHORIZATION=f"Bearer {self.token}")
        self.assertEqual(res.status_code, 201)

    def test_create_product(self):
        res = self.client.post("/api/v1/products/merchant/", json.dumps({
            "name": "Gamis Syari", "price": 150000, "category": self.category.id,
        }), content_type="application/json", HTTP_AUTHORIZATION=f"Bearer {self.token}")
        self.assertEqual(res.status_code, 201)

    def test_create_variant(self):
        res = self.client.post(f"/api/v1/products/merchant/{self.product.id}/variants/", json.dumps({
            "name": "Navy", "stock": 5,
        }), content_type="application/json", HTTP_AUTHORIZATION=f"Bearer {self.token}")
        self.assertEqual(res.status_code, 201)

    def test_public_catalog(self):
        res = self.client.get(f"/api/v1/catalog/{self.store.slug}/")
        self.assertEqual(res.status_code, 200)

    def test_product_search(self):
        res = self.client.get(f"/api/v1/catalog/{self.store.slug}/?q=Pashmina")
        self.assertEqual(res.status_code, 200)

    def test_product_sort(self):
        res = self.client.get(f"/api/v1/catalog/{self.store.slug}/?sort=price_asc")
        self.assertEqual(res.status_code, 200)


class CartTest(TestCase):
    def setUp(self):
        self.client = Client()
        _, self.store = _setup_user(self.client, "cart@test.com")
        self.product = Product.objects.create(
            store=self.store, name="Test Product", slug="test-product", price=50000
        )
        self.variant = Variant.objects.create(
            product=self.product, name="Size M", stock=10
        )

    def test_get_empty_cart(self):
        res = self.client.get("/api/v1/cart/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["item_count"], 0)

    def test_add_to_cart(self):
        res = self.client.post("/api/v1/cart/items/", json.dumps({
            "variant": self.variant.id, "quantity": 2
        }), content_type="application/json")
        self.assertEqual(res.status_code, 201)

    def test_add_duplicate_item(self):
        self.client.post("/api/v1/cart/items/", json.dumps({
            "variant": self.variant.id, "quantity": 1
        }), content_type="application/json")
        res = self.client.post("/api/v1/cart/items/", json.dumps({
            "variant": self.variant.id, "quantity": 2
        }), content_type="application/json")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["quantity"], 3)

    def test_add_exceeds_stock(self):
        res = self.client.post("/api/v1/cart/items/", json.dumps({
            "variant": self.variant.id, "quantity": 20
        }), content_type="application/json")
        self.assertEqual(res.status_code, 400)

    def test_clear_cart(self):
        self.client.post("/api/v1/cart/items/", json.dumps({
            "variant": self.variant.id, "quantity": 1
        }), content_type="application/json")
        res = self.client.delete("/api/v1/cart/")
        self.assertEqual(res.status_code, 204)


class CheckoutTest(TestCase):
    def setUp(self):
        self.client = Client()
        _, self.store = _setup_user(self.client, "checkout@test.com")
        self.product = Product.objects.create(
            store=self.store, name="Checkout Product", slug="checkout-product", price=100000
        )
        self.variant = Variant.objects.create(
            product=self.product, name="Standard", stock=5
        )
        self.client.post("/api/v1/cart/items/", json.dumps({
            "variant": self.variant.id, "quantity": 2
        }), content_type="application/json")

    def test_checkout_success(self):
        res = self.client.post("/api/v1/checkout/", json.dumps({
            "shipping_name": "Budi", "shipping_phone": "081234567890",
            "shipping_address": "Jl. Sudirman 123", "shipping_city": "Jakarta",
        }), content_type="application/json")
        self.assertEqual(res.status_code, 201)
        self.assertIn("order_number", res.json())

    def test_checkout_empty_cart(self):
        self.client.delete("/api/v1/cart/")
        res = self.client.post("/api/v1/checkout/", json.dumps({
            "shipping_name": "Budi", "shipping_phone": "081234567890",
            "shipping_address": "Jl. Sudirman 123", "shipping_city": "Jakarta",
        }), content_type="application/json")
        self.assertEqual(res.status_code, 400)


class WishlistTest(TestCase):
    def setUp(self):
        self.client = Client()
        _, self.store = _setup_user(self.client, "wish@test.com")
        self.product = Product.objects.create(
            store=self.store, name="Wish Product", slug="wish-product", price=50000
        )

    def test_wishlist_toggle_add(self):
        res = self.client.post("/api/v1/reviews/wishlist/toggle/", json.dumps({
            "product": self.product.id
        }), content_type="application/json")
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json()["wishlisted"])

    def test_wishlist_toggle_remove(self):
        self.client.post("/api/v1/reviews/wishlist/toggle/", json.dumps({
            "product": self.product.id
        }), content_type="application/json")
        res = self.client.post("/api/v1/reviews/wishlist/toggle/", json.dumps({
            "product": self.product.id
        }), content_type="application/json")
        self.assertFalse(res.json()["wishlisted"])

    def test_wishlist_check(self):
        res = self.client.get(f"/api/v1/reviews/wishlist/check/{self.product.id}/")
        self.assertFalse(res.json()["wishlisted"])
        self.client.post("/api/v1/reviews/wishlist/toggle/", json.dumps({
            "product": self.product.id
        }), content_type="application/json")
        res = self.client.get(f"/api/v1/reviews/wishlist/check/{self.product.id}/")
        self.assertTrue(res.json()["wishlisted"])


class PaymentWebhookTest(TestCase):
    """Test Midtrans webhook: signature verification + idempotency."""

    def setUp(self):
        self.client = Client()
        _, self.store = _setup_user(self.client, "webhook@test.com")
        self.product = Product.objects.create(
            store=self.store, name="Hook Product", slug="hook-product", price=75000
        )
        self.variant = Variant.objects.create(
            product=self.product, name="Reguler", stock=10
        )
        self.client.post("/api/v1/cart/items/", json.dumps({
            "variant": self.variant.id, "quantity": 2
        }), content_type="application/json")
        res = self.client.post("/api/v1/checkout/", json.dumps({
            "shipping_name": "Tono", "shipping_phone": "081111222333",
            "shipping_address": "Jl. Merdeka 1", "shipping_city": "Bandung",
        }), content_type="application/json")
        self.order_number = res.json()["order_number"]

    def _signed_payload(self, status_code="200", gross="150000", transaction_status="settlement", fraud_status="accept"):
        """Build valid signed webhook payload."""
        import hashlib
        from django.conf import settings
        server_key = settings.MIDTRANS_SERVER_KEY
        sig = hashlib.sha512(
            f"{self.order_number}{status_code}{gross}{server_key}".encode()
        ).hexdigest()
        return {
            "order_id": self.order_number,
            "status_code": status_code,
            "gross_amount": gross,
            "signature_key": sig,
            "transaction_status": transaction_status,
            "fraud_status": fraud_status,
            "payment_type": "bank_transfer",
        }

    def test_webhook_rejects_bad_signature(self):
        payload = self._signed_payload()
        payload["signature_key"] = "wrongsignature"
        res = self.client.post("/api/v1/payments/webhook/", json.dumps(payload),
                               content_type="application/json")
        self.assertEqual(res.status_code, 403)
        # Order must not be marked paid
        from apps.orders.models import Order
        order = Order.objects.get(order_number=self.order_number)
        self.assertNotEqual(order.payment_status, "paid")

    def test_webhook_settlement_marks_paid_and_reduces_stock(self):
        payload = self._signed_payload()
        res = self.client.post("/api/v1/payments/webhook/", json.dumps(payload),
                               content_type="application/json")
        self.assertEqual(res.status_code, 200)
        from apps.orders.models import Order
        order = Order.objects.get(order_number=self.order_number)
        self.assertEqual(order.payment_status, "paid")
        self.assertEqual(order.status, "processing")
        # Stock reduced: 10 - 2 = 8
        self.variant.refresh_from_db()
        self.assertEqual(self.variant.stock, 8)

    def test_webhook_idempotent_duplicate_settlement(self):
        payload = self._signed_payload()
        # First webhook
        res1 = self.client.post("/api/v1/payments/webhook/", json.dumps(payload),
                                content_type="application/json")
        self.assertEqual(res1.status_code, 200)
        # Duplicate webhook (same settlement)
        res2 = self.client.post("/api/v1/payments/webhook/", json.dumps(payload),
                                content_type="application/json")
        self.assertEqual(res2.status_code, 200)
        # Stock must NOT be reduced twice: still 8
        self.variant.refresh_from_db()
        self.assertEqual(self.variant.stock, 8)

    def test_paid_order_cannot_be_downgraded_by_expire(self):
        """QA REGRESSION: paid → expire must NOT change status."""
        # Settle first
        res = self.client.post("/api/v1/payments/webhook/", json.dumps(self._signed_payload()),
                               content_type="application/json")
        self.assertEqual(res.status_code, 200)
        # Now send expire
        payload = self._signed_payload(status_code="201", transaction_status="expire", fraud_status="")
        res = self.client.post("/api/v1/payments/webhook/", json.dumps(payload),
                               content_type="application/json")
        self.assertEqual(res.status_code, 200)
        from apps.orders.models import Order
        order = Order.objects.get(order_number=self.order_number)
        # Order must REMAIN paid
        self.assertEqual(order.payment_status, "paid")
        self.assertEqual(order.status, "processing")
        # Stock must NOT change
        self.variant.refresh_from_db()
        self.assertEqual(self.variant.stock, 8)

    def test_paid_order_cannot_be_downgraded_by_cancel(self):
        """QA REGRESSION: paid → cancel must NOT change status."""
        res = self.client.post("/api/v1/payments/webhook/", json.dumps(self._signed_payload()),
                               content_type="application/json")
        self.assertEqual(res.status_code, 200)
        payload = self._signed_payload(status_code="406", transaction_status="cancel", fraud_status="")
        res = self.client.post("/api/v1/payments/webhook/", json.dumps(payload),
                               content_type="application/json")
        self.assertEqual(res.status_code, 200)
        from apps.orders.models import Order
        order = Order.objects.get(order_number=self.order_number)
        self.assertEqual(order.payment_status, "paid")
        self.variant.refresh_from_db()
        self.assertEqual(self.variant.stock, 8)

    def test_settle_expire_settle_no_double_deduct(self):
        """QA REGRESSION: settle → expire → settle = stock -2 total (not -4)."""
        # 1st settlement
        res = self.client.post("/api/v1/payments/webhook/", json.dumps(self._signed_payload()),
                               content_type="application/json")
        self.assertEqual(res.status_code, 200)
        # expire (ignored — paid is final)
        payload = self._signed_payload(status_code="201", transaction_status="expire", fraud_status="")
        self.client.post("/api/v1/payments/webhook/", json.dumps(payload),
                         content_type="application/json")
        # 2nd settlement (duplicate)
        res = self.client.post("/api/v1/payments/webhook/", json.dumps(self._signed_payload()),
                               content_type="application/json")
        self.assertEqual(res.status_code, 200)
        # Stock reduced exactly ONCE: 10 - 2 = 8
        self.variant.refresh_from_db()
        self.assertEqual(self.variant.stock, 8)

    def test_stock_restored_on_expire_unpaid_order(self):
        """QA REGRESSION: unpaid order expires → stock restored."""
        # No settlement — order still waiting_payment, stock intact
        payload = self._signed_payload(status_code="201", transaction_status="expire", fraud_status="")
        res = self.client.post("/api/v1/payments/webhook/", json.dumps(payload),
                               content_type="application/json")
        self.assertEqual(res.status_code, 200)
        from apps.orders.models import Order
        order = Order.objects.get(order_number=self.order_number)
        self.assertEqual(order.payment_status, "failed")
        # Stock unchanged (never deducted)
        self.variant.refresh_from_db()
        self.assertEqual(self.variant.stock, 10)


class WebpageTest(TestCase):
    def setUp(self):
        self.client = Client()
        _, self.store = _setup_user(self.client, "page@test.com")
        self.user = User.objects.get(email="page@test.com")

    def test_home_page(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)

    def test_catalog_page(self):
        res = self.client.get("/catalog/")
        self.assertEqual(res.status_code, 200)

    def test_cart_page(self):
        res = self.client.get("/cart/")
        self.assertEqual(res.status_code, 200)

    def test_checkout_page(self):
        res = self.client.get("/checkout/")
        self.assertEqual(res.status_code, 200)

    def test_dashboard_login_page(self):
        res = self.client.get("/dashboard/login/")
        self.assertEqual(res.status_code, 200)

    def test_dashboard_requires_login(self):
        res = self.client.get("/dashboard/")
        self.assertIn(res.status_code, [302, 301])

    def test_dashboard_overview(self):
        self.client.force_login(self.user)
        res = self.client.get("/dashboard/")
        self.assertEqual(res.status_code, 200)


class SecurityRegressionTest(TestCase):
    """Security audit fixes — IDOR, amount tampering, ownership token."""

    def setUp(self):
        self.client = Client()
        _, self.store = _setup_user(self.client, "sec@test.com")
        self.product = Product.objects.create(
            store=self.store, name="Sec Product", slug="sec-product", price=90000
        )
        self.variant = Variant.objects.create(
            product=self.product, name="Reguler", stock=10
        )
        self.client.post("/api/v1/cart/items/", json.dumps({
            "variant": self.variant.id, "quantity": 1
        }), content_type="application/json")
        res = self.client.post("/api/v1/checkout/", json.dumps({
            "shipping_name": "Siti Korban", "shipping_phone": "081299998888",
            "shipping_address": "Jl. Rahasia No 9", "shipping_city": "Bandung",
        }), content_type="application/json")
        self.order_number = res.json()["order_number"]
        self.access_token = res.json()["access_token"]
        from apps.orders.models import Order
        self.order = Order.objects.get(order_number=self.order_number)

    def _signed_payload(self, gross="90000", transaction_status="settlement", status_code="200"):
        """Build valid signed webhook payload for amount-tampering test."""
        import hashlib
        from django.conf import settings
        server_key = settings.MIDTRANS_SERVER_KEY
        sig = hashlib.sha512(
            f"{self.order_number}{status_code}{gross}{server_key}".encode()
        ).hexdigest()
        return {
            "order_id": self.order_number, "status_code": status_code,
            "gross_amount": gross, "signature_key": sig,
            "transaction_status": transaction_status, "fraud_status": "accept",
            "payment_type": "bank_transfer",
        }

    def test_amount_tampering_rejected(self):
        """SK #4 — bayar Rp 100 utk order Rp 90.000 harus DITOLAK."""
        payload = self._signed_payload(gross="100")
        res = self.client.post("/api/v1/payments/webhook/", json.dumps(payload),
                               content_type="application/json")
        # Amount mismatch utk capture/settlement => 400
        self.assertEqual(res.status_code, 400)
        self.order.refresh_from_db()
        self.assertNotEqual(self.order.payment_status, "paid")

    def test_order_confirmation_IDOR_blocked_without_token(self):
        """SK #2 — akses halaman order tanpa access_token => 404 (PII aman)."""
        # Tanpa token
        res = self.client.get(f"/order/{self.order_number}/")
        self.assertEqual(res.status_code, 404)
        # Token salah
        res = self.client.get(f"/order/{self.order_number}/?token=wrongtoken")
        self.assertEqual(res.status_code, 404)

    def test_order_confirmation_with_valid_token(self):
        """SK #2 — pemilik dgn token valid bisa lihat halaman konfirmasi."""
        res = self.client.get(f"/order/{self.order_number}/?token={self.access_token}")
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Siti Korban")

    def test_payment_status_requires_token(self):
        """SK #3 — endpoint status tanpa access_token => 404."""
        res = self.client.get(f"/api/v1/payments/{self.order_number}/status/")
        self.assertEqual(res.status_code, 404)
        res = self.client.get(
            f"/api/v1/payments/{self.order_number}/status/?token={self.access_token}")
        self.assertEqual(res.status_code, 200)

    def test_create_payment_requires_token(self):
        """SK #3 — create payment tanpa access_token => 404."""
        res = self.client.post("/api/v1/payments/create/", json.dumps({
            "order_number": self.order_number
        }), content_type="application/json")
        self.assertEqual(res.status_code, 404)

    def test_access_token_not_guessable(self):
        """SK #3 — access_token acak & panjang (bukan sequential)."""
        self.assertIsNotNone(self.order.access_token)
        self.assertGreaterEqual(len(self.order.access_token), 30)
