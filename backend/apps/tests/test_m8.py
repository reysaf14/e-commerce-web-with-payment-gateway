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
