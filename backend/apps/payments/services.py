"""Midtrans payment service — Snap API integration.

Uses HTTP requests directly (no SDK dependency) to keep
requirements minimal for VPS deployment.
"""

import hashlib
import hmac
import base64
import requests
from django.conf import settings


def _get_api_url():
    if settings.MIDTRANS_IS_PRODUCTION:
        return "https://api.midtrans.com/v2"
    return "https://api.sandbox.midtrans.com/v2"


def _get_snap_url():
    if settings.MIDTRANS_IS_PRODUCTION:
        return "https://app.midtrans.com/snap"
    return "https://app.sandbox.midtrans.com/snap"


def _get_auth_header():
    server_key = settings.MIDTRANS_SERVER_KEY
    return base64.b64encode(f"{server_key}:".encode()).decode()


def create_transaction(order, items, callback_url, webhooks_url):
    """Create Midtrans Snap transaction.

    Returns dict with {token, redirect_url} or raises.
    """
    url = f"{_get_snap_url()}/transactions"
    headers = {
        "Authorization": f"Basic {_get_auth_header()}",
        "Content-Type": "application/json",
    }

    item_details = []
    for item in items:
        item_details.append({
            "id": item.variant.sku or f"item-{item.id}",
            "price": int(item.unit_price),
            "quantity": item.quantity,
            "name": f"{item.product_name} - {item.variant_name}",
        })

    # Add shipping as an item
    if order.shipping_cost > 0:
        item_details.append({
            "id": "SHIPPING",
            "price": int(order.shipping_cost),
            "quantity": 1,
            "name": "Biaya Pengiriman",
        })

    payload = {
        "transaction_details": {
            "order_id": order.order_number,
            "gross_amount": int(order.total_amount),
        },
        "item_details": item_details,
        "customer_details": {
            "first_name": order.shipping_name,
            "phone": order.shipping_phone,
            "email": order.customer.email if order.customer and order.customer.email else None,
            "shipping_address": {
                "first_name": order.shipping_name,
                "phone": order.shipping_phone,
                "address": order.shipping_address,
                "city": order.shipping_city,
                "postal_code": order.shipping_postal_code,
            },
        },
        "callbacks": {
            "finish": callback_url,
        },
        "expiry": {
            "unit": "day",
            "duration": 1,
        },
    }

    # Remove None values
    if payload["customer_details"].get("email") is None:
        del payload["customer_details"]["email"]

    response = requests.post(url, json=payload, headers=headers, timeout=30)
    data = response.json()

    if response.status_code != 201:
        error_msg = data.get("error_messages", [data.get("status_message", "Unknown error")])
        raise Exception(f"Midtrans error: {error_msg}")

    return {
        "token": data.get("token"),
        "redirect_url": data.get("redirect_url"),
    }


def check_transaction_status(order_number):
    """Check transaction status from Midtrans API."""
    url = f"{_get_api_url()}/{order_number}/status"
    headers = {
        "Authorization": f"Basic {_get_auth_header()}",
    }

    response = requests.get(url, headers=headers, timeout=30)
    if response.status_code == 200:
        return response.json()
    return None


def verify_webhook_signature(order_id, status_code, gross_amount, server_key):
    """Verify Midtrans webhook (notification) signature.

    Signature = SHA512(order_id + status_code + gross_amount + server_key)
    """
    # Build signature string (Midtrans format)
    # The actual fields from notification depend on transaction type
    # Midtrans sends: order_id, status_code, gross_amount, signature_key, ...
    pass  # Will be handled in webhook_view with the actual notification fields
