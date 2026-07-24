"""CartItem model."""
from django.db import models
from django.contrib.auth.models import User


class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='cart_items')
    product_id = models.IntegerField()
    title = models.CharField(max_length=255)
    title_ar = models.CharField(max_length=255, blank=True, default="")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.TextField()
    color = models.CharField(max_length=50, blank=True, default="")
    size = models.CharField(max_length=50, blank=True, default="")
    quantity = models.IntegerField(default=1)
    weight = models.FloatField(default=0.3)

    class Meta:
        verbose_name = "عنصر بالسلة"
        verbose_name_plural = "عناصر السلة"

    def __str__(self):
        username = self.user.username if self.user else "Guest"
        return f"{username} - {self.title} x{self.quantity}"
