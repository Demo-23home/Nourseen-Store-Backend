"""OrderViewSet — creation (with profile sync), status updates, and cancel action."""
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User

from api.models import Order, UserProfile
from api.serializers import OrderSerializer
from api.services.order_service import OrderService
from .permissions import IsSuperUser, StandardResultsSetPagination


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    pagination_class = StandardResultsSetPagination

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Order.objects.all().order_by('-id')
        elif user.is_authenticated:
            return Order.objects.filter(user=user).order_by('-id')
        return Order.objects.none()

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None

        # Associate guest orders with their account if email matches
        shipping_info = self.request.data.get('shippingInfo', {})
        if not user and isinstance(shipping_info, dict) and shipping_info.get('email'):
            email = str(shipping_info.get('email')).strip().lower()
            if email:
                user = User.objects.filter(email=email).first()

        order = serializer.save(user=user)

        # Sync phone & address to UserProfile
        if user:
            phone, address = OrderService.extract_contact_from_order(order, self.request.data)
            OrderService.sync_user_profile(user, phone, address)

    def update(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return Response(
                {"error": "Only administrators can update order details or status."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return Response(
                {"error": "Only administrators can update order status."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().partial_update(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        order = self.get_object()
        if order.status in ['on-delivery', 'delivered']:
            return Response(
                {"error": "Order cannot be canceled once it has reached on-delivery or delivered status."},
                status=status.HTTP_400_BAD_REQUEST
            )
        if order.status == 'canceled':
            return Response({"error": "Order is already canceled."}, status=status.HTTP_400_BAD_REQUEST)

        order.status = 'canceled'
        order.save()
        return Response(OrderSerializer(order).data, status=status.HTTP_200_OK)
