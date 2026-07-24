"""NewsletterSubscriber model."""
from django.db import models


class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "مشترك بالنشرة"
        verbose_name_plural = "مشتركون بالنشرة"

    def __str__(self):
        return self.email
