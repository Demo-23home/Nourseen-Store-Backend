"""Product and Category viewsets."""
from rest_framework import viewsets, permissions
from django.db.models import Q

from api.models import Product, Category
from api.serializers import ProductSerializer, CategorySerializer
from .permissions import IsSuperUser, StandardResultsSetPagination


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by('name')
    serializer_class = CategorySerializer
    pagination_class = None

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [IsSuperUser()]


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    pagination_class = StandardResultsSetPagination

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [IsSuperUser()]

    def get_queryset(self):
        queryset = Product.objects.all().order_by('id')

        category = self.request.query_params.get('category')
        if category and category != 'all':
            queryset = queryset.filter(category=category)

        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(title_ar__icontains=search) |
                Q(description__icontains=search) |
                Q(description_ar__icontains=search) |
                Q(code__icontains=search)
            )

        min_price = self.request.query_params.get('min_price')
        if min_price:
            try:
                queryset = queryset.filter(price__gte=float(min_price))
            except ValueError:
                pass

        max_price = self.request.query_params.get('max_price')
        if max_price:
            try:
                queryset = queryset.filter(price__lte=float(max_price))
            except ValueError:
                pass

        color = self.request.query_params.get('color')
        if color and color != 'all':
            queryset = queryset.filter(colors__icontains=color)

        size = self.request.query_params.get('size')
        if size and size != 'all':
            queryset = queryset.filter(sizes__icontains=size)

        min_weight = self.request.query_params.get('min_weight')
        if min_weight:
            try:
                queryset = queryset.filter(weight__gte=float(min_weight))
            except ValueError:
                pass

        max_weight = self.request.query_params.get('max_weight')
        if max_weight:
            try:
                queryset = queryset.filter(weight__lte=float(max_weight))
            except ValueError:
                pass

        sort = self.request.query_params.get('sort')
        if sort == 'price-low':
            queryset = queryset.order_by('price')
        elif sort == 'price-high':
            queryset = queryset.order_by('-price')
        elif sort == 'rating':
            queryset = queryset.order_by('-rating')

        return queryset
