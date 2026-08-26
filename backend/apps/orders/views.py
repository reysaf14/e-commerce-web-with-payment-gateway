"""Order views — checkout + merchant order management."""

from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .models import Order, OrderItem
from .serializers import OrderSerializer, CheckoutSerializer
from apps.customers.models import Customer
from apps.notifications.services import create_notification


# ── Checkout ──────────────────────────────────────────────

@csrf_exempt
@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def checkout_view(request):
    serializer = CheckoutSerializer(data=request.data, context={"request": request})
    serializer.is_valid(raise_exception=True)

    cart = serializer.validated_data["cart"]
    store = serializer.validated_data["store"]

    with transaction.atomic():
        subtotal = sum(item.line_total for item in cart.items.all())
        shipping_cost = store.shipping_cost
        total_amount = subtotal + shipping_cost

        phone = serializer.validated_data["shipping_phone"]
        customer, _ = Customer.objects.get_or_create(
            store=store, phone=phone,
            defaults={
                "full_name": serializer.validated_data["shipping_name"],
                "address": serializer.validated_data["shipping_address"],
                "city": serializer.validated_data["shipping_city"],
                "postal_code": serializer.validated_data.get("shipping_postal_code", ""),
            }
        )

        order = Order.objects.create(
            store=store, customer=customer, subtotal=subtotal,
            shipping_cost=shipping_cost, total_amount=total_amount,
            shipping_name=serializer.validated_data["shipping_name"],
            shipping_phone=phone,
            shipping_address=serializer.validated_data["shipping_address"],
            shipping_city=serializer.validated_data["shipping_city"],
            shipping_postal_code=serializer.validated_data.get("shipping_postal_code", ""),
            note_to_seller=serializer.validated_data.get("note_to_seller", ""),
        )

        for item in cart.items.select_related("variant", "variant__product"):
            OrderItem.objects.create(
                order=order, product=item.variant.product, variant=item.variant,
                product_name=item.variant.product.name, variant_name=item.variant.name,
                unit_price=item.variant.display_price, quantity=item.quantity,
                subtotal=item.line_total,
            )

        customer.order_count += 1
        customer.total_spent += total_amount
        from django.utils import timezone
        customer.last_order_at = timezone.now()
        customer.save()

        cart.items.all().delete()

        create_notification(
            store=store, recipient_type="merchant", recipient_id=store.user.id,
            notif_type="new_order", title=f"Pesanan Baru: {order.order_number}",
            message=f"Total: Rp {total_amount:,.0f} dari {order.shipping_name}",
        )

    return Response({
        "order_number": order.order_number,
        "total_amount": str(order.total_amount),
        "status": order.status,
    }, status=status.HTTP_201_CREATED)


# ── Merchant Order Management ─────────────────────────────

class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(store=self.request.user.store_settings)


class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "order_number"

    def get_queryset(self):
        return Order.objects.filter(store=self.request.user.store_settings)
