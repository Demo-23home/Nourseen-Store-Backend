from django.contrib import admin
from .models import Product, Order, UserProfile, Category, NewsletterSubscriber, CartItem

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone')
    search_fields = ('user__username', 'user__email', 'phone')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'price', 'originalPrice', 'weight', 'can_be_returned')
    list_filter = ('category', 'can_be_returned')
    search_fields = ('title', 'title_ar', 'description')
    ordering = ('-id',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'payment_method', 'status', 'total', 'date')
    list_filter = ('status', 'payment_method')
    search_fields = ('id', 'shippingInfo', 'date')
    ordering = ('-date',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'name_ar', 'slug')
    search_fields = ('name', 'name_ar', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'created_at')
    search_fields = ('email',)
    ordering = ('-created_at',)


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'quantity', 'price')
    search_fields = ('title', 'user__username', 'user__email')
    list_filter = ('size', 'color')
