"""Payment views — create payment + webhook handler."""

import hashlib
import json
from django.conf import settings
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from apps.orders.models import Order
from apps.products.models import Variant
from apps.notifications.services import create_notification
from .models import Payment
from .serializers import PaymentSerializer
from . import services as midtrans_service


@csrf_exempt
@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def create_payment(request):
    """Create Midtrans Snap transaction for an order."""
    order_number = request.data.get("order_number")
    if not order_number:
        return Response({"error": "order_number wajib diisi."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        order = Order.objects.get(order_number=order_number)
    except Order.DoesNotExist:
        return Response({"error": "Pesanan tidak ditemukan."}, status=status.HTTP_404_NOT_FOUND)

    if order.payment_status == "paid":
        return Response({"error": "Pesanan sudah dibayar."}, status=status.HTTP_400_BAD_REQUEST)

    # Check if there's already a pending payment
    existing = Payment.objects.filter(order=order, status="pending").first()
    if existing:
        # Return existing token
        callback_url = request.build_absolute_uri(f"/order/{order.order_number}/")
        return Response({
            "snap_token": existing.midtrans_token,
            "redirect_url": existing.midtrans_redirect_url,
            "order_number": order.order_number,
        })

    # Get order items
    items = order.items.all()
    if not items.exists():
        return Response({"error": "Pesanan tidak memiliki item."}, status=status.HTTP_400_BAD_REQUEST)

    callback_url = request.build_absolute_uri(f"/order/{order.order_number}/")
    webhook_url = request.build_absolute_uri(settings.MIDTRANS_WEBHOOK_URL)

    try:
        result = midtrans_service.create_transaction(
            order=order,
            items=items,
            callback_url=callback_url,
            webhooks_url=webhook_url,
        )

        # Save payment record
        payment = Payment.objects.create(
            order=order,
            store=order.store,
            midtrans_order_id=order.order_number,
            midtrans_token=result["token"],
            midtrans_redirect_url=result["redirect_url"],
            amount=order.total_amount,
            status="pending",
        )

        return Response({
            "snap_token": result["token"],
            "redirect_url": result["redirect_url"],
            "order_number": order.order_number,
        })

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_502_BAD_GATEWAY)


@csrf_exempt
@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def webhook_view(request):
    """Midtrans server-to-server webhook handler.

    Receives payment notification and updates order status.
    """
    # Verify signature
    notification = request.data
    order_id = notification.get("order_id")
    status_code = notification.get("status_code")
    gross_amount = notification.get("gross_amount")
    signature_key = notification.get("signature_key")
    transaction_status = notification.get("transaction_status")
    fraud_status = notification.get("fraud_status")
    payment_type = notification.get("payment_type")

    # Verify signature
    server_key = settings.MIDTRANS_SERVER_KEY
    expected_signature = hashlib.sha512(
        f"{order_id}{status_code}{gross_amount}{server_key}".encode()
    ).hexdigest()

    if signature_key != expected_signature:
        return JsonResponse({"status": "error", "message": "Invalid signature"}, status=403)

    with transaction.atomic():
        try:
            order = Order.objects.get(order_number=order_id)
        except Order.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Order not found"}, status=404)

        # Map Midtrans status to our status
        if transaction_status == "capture":
            if fraud_status == "accept":
                order.payment_status = "paid"
                order.status = "processing"
                # Reduce stock
                for item in order.items.select_related("variant"):
                    variant = item.variant
                    variant.stock = max(0, variant.stock - item.quantity)
                    variant.save()
            elif fraud_status == "challenge":
                order.payment_status = "challenge"
            else:
                order.payment_status = "fraud"

        elif transaction_status == "settlement":
            order.payment_status = "paid"
            order.status = "processing"
            for item in order.items.select_related("variant"):
                variant = item.variant
                variant.stock = max(0, variant.stock - item.quantity)
                variant.save()

        elif transaction_status == "pending":
            order.payment_status = "pending"

        elif transaction_status in ("deny", "expire"):
            order.payment_status = "failed"

        elif transaction_status == "cancel":
            order.payment_status = "cancelled"

        order.save()

        # Update payment record
        payment, _ = Payment.objects.get_or_create(
            order=order,
            defaults={
                "store": order.store,
                "midtrans_order_id": order_id,
                "amount": gross_amount,
            }
        )
        payment.status = transaction_status
        payment.payment_type = payment_type
        payment.fraud_status = fraud_status or ""
        if transaction_status in ("capture", "settlement") and fraud_status == "accept":
            from django.utils import timezone
            payment.paid_at = timezone.now()
        payment.save()

        # Notification
        if order.payment_status == "paid":
            create_notification(
                store=order.store,
                recipient_type="merchant",
                recipient_id=order.store.user.id,
                notif_type="payment",
                title=f"Pembayaran Diterima: {order.order_number}",
                message=f"Total: Rp {order.total_amount:,.0f}",
            )

    return JsonResponse({"status": "ok"})


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def payment_status_view(request, order_number):
    """Check payment status for an order."""
    try:
        order = Order.objects.get(order_number=order_number)
    except Order.DoesNotExist:
        return Response({"error": "Pesanan tidak ditemukan."}, status=status.HTTP_404_NOT_FOUND)

    payment = Payment.objects.filter(order=order).order_by("-created_at").first()

    return Response({
        "order_number": order.order_number,
        "order_status": order.status,
        "payment_status": order.payment_status,
        "total_amount": str(order.total_amount),
        "payment": PaymentSerializer(payment).data if payment else None,
    })
