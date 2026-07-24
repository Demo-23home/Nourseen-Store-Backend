"""
api.models package
==================
Re-exports all models so existing imports like:
    from api.models import Product, Order, ...
continue to work without modification.
"""
from .product import Product, Category
from .order import Order
from .cart import CartItem
from .newsletter import NewsletterSubscriber
from .user_profile import UserProfile

__all__ = [
    'Product',
    'Category',
    'Order',
    'CartItem',
    'NewsletterSubscriber',
    'UserProfile',
]
