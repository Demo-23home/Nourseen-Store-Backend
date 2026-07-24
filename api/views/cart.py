"""CartItemViewSet — per-user server-side cart."""
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from api.models import CartItem
from api.serializers import CartItemSerializer


class CartItemViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    serializer_class = CartItemSerializer

    def get_queryset(self):
        user = self.request.user
        if user and user.is_authenticated:
            return CartItem.objects.filter(user=user).order_by('id')
        return CartItem.objects.none()

    def perform_create(self, serializer):
        user = self.request.user if (self.request.user and self.request.user.is_authenticated) else None
        serializer.save(user=user)

    @action(detail=False, methods=['delete', 'post'])
    def clear(self, request):
        if request.user and request.user.is_authenticated:
            CartItem.objects.filter(user=request.user).delete()
        return Response({"message": "Cart cleared successfully."}, status=200)
