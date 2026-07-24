"""CartItem serializer."""
from rest_framework import serializers
from api.models import CartItem


class CartItemSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = CartItem
        fields = ('id', 'product_id', 'title', 'title_ar', 'price', 'image', 'color', 'size', 'quantity', 'weight')
