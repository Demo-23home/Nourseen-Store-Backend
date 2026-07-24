"""Order model."""
from django.db import models
from django.contrib.auth.models import User


class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'قيد المراجعة (Pending)'),
        ('accepted', 'تم القبول (Accepted)'),
        ('preparing', 'جاري التجهيز (Preparing)'),
        ('on-delivery', 'جاري التوصيل (On Delivery)'),
        ('delivered', 'تم التسليم (Delivered)'),
        ('canceled', 'ملغى (Canceled)'),
    )

    id = models.CharField(max_length=50, primary_key=True)  # e.g. "NS-XXXXXX"
    date = models.CharField(max_length=100)
    items = models.JSONField(default=list)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    shippingInfo = models.JSONField(default=dict)
    payment_method = models.CharField(max_length=50, default="instapay")
    payment_receipt = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="pending")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')

    class Meta:
        verbose_name = "طلب"
        verbose_name_plural = "الطلبات"

    def __str__(self):
        return f"{self.id} ({self.get_status_display()})"
