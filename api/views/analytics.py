"""Admin analytics view."""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from api.models import Order, Product
from .permissions import IsSuperUser


class AdminAnalyticsView(APIView):
    permission_classes = [IsSuperUser]

    def get(self, request):
        orders = Order.objects.all()
        products = Product.objects.all()

        total_orders = orders.count()
        total_revenue = sum(float(o.total) for o in orders)
        pending_orders = orders.filter(status='pending').count()
        delivered_orders = orders.filter(status='delivered').count()

        aov = (total_revenue / total_orders) if total_orders > 0 else 0
        fulfillment_rate = ((delivered_orders / total_orders) * 100) if total_orders > 0 else 0

        status_counts = {
            'pending': orders.filter(status='pending').count(),
            'accepted': orders.filter(status='accepted').count(),
            'preparing': orders.filter(status='preparing').count(),
            'on-delivery': orders.filter(status='on-delivery').count(),
            'delivered': orders.filter(status='delivered').count(),
            'canceled': orders.filter(status='canceled').count(),
        }

        payment_counts = {
            'instapay': orders.filter(payment_method='instapay').count(),
            'vf_cash': orders.filter(payment_method='vf_cash').count(),
        }

        return Response({
            "total_revenue": total_revenue,
            "total_orders": total_orders,
            "pending_orders": pending_orders,
            "delivered_orders": delivered_orders,
            "aov": round(aov, 2),
            "fulfillment_rate": round(fulfillment_rate, 2),
            "total_products": products.count(),
            "status_counts": status_counts,
            "payment_counts": payment_counts,
        }, status=status.HTTP_200_OK)
