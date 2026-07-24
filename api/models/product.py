"""Product and Category models."""
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100)
    name_ar = models.CharField(max_length=100, blank=True, default="")
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        verbose_name = "تصنيف"
        verbose_name_plural = "التصنيفات"

    def __str__(self):
        return self.name or self.name_ar


class Product(models.Model):
    code = models.CharField(max_length=50, blank=True, default="")
    title = models.CharField(max_length=255)
    title_ar = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    originalPrice = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    rating = models.FloatField(default=4.5)
    badge = models.CharField(max_length=50, blank=True, default="")
    badgeType = models.CharField(max_length=50, blank=True, default="")
    image = models.TextField()
    description = models.TextField()
    description_ar = models.TextField()
    sizes = models.JSONField(default=list, blank=True)
    colors = models.JSONField(default=list, blank=True)
    variants = models.JSONField(default=list, blank=True)
    weight = models.FloatField(default=0.3)
    can_be_returned = models.BooleanField(default=True)
    valid_from = models.CharField(max_length=50, blank=True, null=True, default="")
    valid_to = models.CharField(max_length=50, blank=True, null=True, default="")

    class Meta:
        verbose_name = "منتج"
        verbose_name_plural = "المنتجات"

    def __str__(self):
        return self.title or self.title_ar or f"Product #{self.id}"
