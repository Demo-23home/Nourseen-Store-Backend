"""
api.views package
==================
Re-exports all viewsets and views for backward compatibility.
"""
from .auth import RegisterView, LoginView, UserMeView, PasswordResetView
from .products import ProductViewSet, CategoryViewSet
from .orders import OrderViewSet
from .cart import CartItemViewSet
from .analytics import AdminAnalyticsView
from .newsletter import NewsletterSubscribeView
from .permissions import IsSuperUser, StandardResultsSetPagination

__all__ = [
    'RegisterView',
    'LoginView',
    'UserMeView',
    'PasswordResetView',
    'ProductViewSet',
    'CategoryViewSet',
    'OrderViewSet',
    'CartItemViewSet',
    'AdminAnalyticsView',
    'NewsletterSubscribeView',
    'IsSuperUser',
    'StandardResultsSetPagination',
]
