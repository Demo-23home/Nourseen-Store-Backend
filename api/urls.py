from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RegisterView,
    LoginView,
    UserMeView,
    PasswordResetView,
    CategoryViewSet,
    ProductViewSet,
    OrderViewSet,
    AdminAnalyticsView,
    NewsletterSubscribeView,
    CartItemViewSet
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'cart', CartItemViewSet, basename='cart')

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='auth_register'),
    path('auth/login/', LoginView.as_view(), name='auth_login'),
    path('auth/me/', UserMeView.as_view(), name='auth_me'),
    path('auth/password-reset/', PasswordResetView.as_view(), name='auth_password_reset'),
    path('admin/analytics/', AdminAnalyticsView.as_view(), name='admin_analytics'),
    path('newsletter/subscribe/', NewsletterSubscribeView.as_view(), name='newsletter_subscribe'),
    path('', include(router.urls)),
]
