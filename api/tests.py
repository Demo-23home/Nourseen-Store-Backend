"""
NourseenStore Backend — Comprehensive Test Suite
=================================================
Covers every API endpoint, model behaviour, permission boundary,
serialiser logic, and edge-case documented in the codebase.

Run with:
    python manage.py test api
"""

from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token

from api.models import (
    Product, Order, Category, NewsletterSubscriber, CartItem, UserProfile
)
from api.serializers import UserSerializer, ProductSerializer, OrderSerializer


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def make_order_payload(order_id, shipping_info=None, **kwargs):
    """Returns a minimal valid order POST body."""
    return {
        'id': order_id,
        'date': '2026-07-21',
        'items': [],
        'subtotal': '100.00',
        'tax': '8.00',
        'total': '108.00',
        'shippingInfo': shipping_info or {'name': 'Test User', 'email': 'u@test.com', 'phone': '01000000000', 'address': 'Cairo'},
        'payment_method': 'instapay',
        **kwargs
    }


def make_product(**kwargs):
    defaults = dict(
        title='Linen Dress', title_ar='فستان كتان',
        category='women', price=100.00,
        image='img.jpg',
        description='A nice dress', description_ar='فستان جميل',
        can_be_returned=True,
    )
    defaults.update(kwargs)
    return Product.objects.create(**defaults)


# ─────────────────────────────────────────────────────────────────────────────
# Model Tests
# ─────────────────────────────────────────────────────────────────────────────

class UserProfileModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='u@test.com', email='u@test.com', password='pass123'
        )

    def test_create_profile(self):
        profile = UserProfile.objects.create(user=self.user, phone='010', address='Cairo')
        self.assertEqual(profile.phone, '010')
        self.assertEqual(profile.address, 'Cairo')

    def test_str_representation(self):
        profile = UserProfile.objects.create(user=self.user, phone='01011111111')
        self.assertIn('01011111111', str(profile))

    def test_cascade_delete(self):
        UserProfile.objects.create(user=self.user, phone='010')
        self.user.delete()
        self.assertEqual(UserProfile.objects.count(), 0)

    def test_blank_defaults(self):
        profile = UserProfile.objects.create(user=self.user)
        self.assertEqual(profile.phone, '')
        self.assertEqual(profile.address, '')


class ProductModelTests(TestCase):
    def test_str_uses_title(self):
        p = make_product(title='Summer Dress')
        self.assertEqual(str(p), 'Summer Dress')

    def test_str_fallback_title_ar(self):
        p = make_product(title='', title_ar='فستان')
        self.assertEqual(str(p), 'فستان')

    def test_valid_from_to_fields(self):
        p = make_product(valid_from='2026-01-01', valid_to='2026-12-31')
        self.assertEqual(p.valid_from, '2026-01-01')
        self.assertEqual(p.valid_to, '2026-12-31')

    def test_json_defaults(self):
        p = make_product()
        self.assertEqual(p.sizes, [])
        self.assertEqual(p.colors, [])
        self.assertEqual(p.variants, [])

    def test_can_be_returned_default(self):
        p = make_product()
        self.assertTrue(p.can_be_returned)


class CategoryModelTests(TestCase):
    def test_create_and_str(self):
        cat = Category.objects.create(name='Women', name_ar='نسائي', slug='women')
        self.assertEqual(str(cat), 'Women')

    def test_slug_unique(self):
        Category.objects.create(name='Women', slug='women')
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Category.objects.create(name='Women 2', slug='women')


class OrderModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='u@test.com', email='u@test.com', password='pass')

    def test_create_order(self):
        order = Order.objects.create(
            id='NS-001', date='2026-07-21', items=[], subtotal=100,
            tax=8, total=108, status='pending', user=self.user
        )
        self.assertEqual(order.status, 'pending')

    def test_str_representation(self):
        order = Order.objects.create(
            id='NS-002', date='2026-07-21', items=[], subtotal=50,
            tax=4, total=54, status='delivered', user=self.user
        )
        self.assertIn('NS-002', str(order))

    def test_user_set_null_on_delete(self):
        order = Order.objects.create(
            id='NS-003', date='2026-07-21', items=[], subtotal=50,
            tax=4, total=54, status='pending', user=self.user
        )
        self.user.delete()
        order.refresh_from_db()
        self.assertIsNone(order.user)

    def test_default_status_is_pending(self):
        order = Order.objects.create(
            id='NS-004', date='2026-07-21', items=[], subtotal=50, tax=4, total=54
        )
        self.assertEqual(order.status, 'pending')


class NewsletterSubscriberModelTests(TestCase):
    def test_create_subscriber(self):
        s = NewsletterSubscriber.objects.create(email='test@test.com')
        self.assertEqual(str(s), 'test@test.com')

    def test_email_unique(self):
        NewsletterSubscriber.objects.create(email='dup@test.com')
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            NewsletterSubscriber.objects.create(email='dup@test.com')


class CartItemModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='cart@test.com', email='cart@test.com', password='pass')

    def test_create_cart_item(self):
        item = CartItem.objects.create(
            user=self.user, product_id=1, title='Dress', price=50, image='img.jpg', quantity=2
        )
        self.assertEqual(item.quantity, 2)

    def test_str_includes_username_and_title(self):
        item = CartItem.objects.create(
            user=self.user, product_id=1, title='Dress', price=50, image='img.jpg'
        )
        self.assertIn('cart@test.com', str(item))
        self.assertIn('Dress', str(item))

    def test_null_user_shows_guest(self):
        item = CartItem.objects.create(
            user=None, product_id=1, title='Scarf', price=25, image='img.jpg'
        )
        self.assertIn('Guest', str(item))


# ─────────────────────────────────────────────────────────────────────────────
# Serializer Tests
# ─────────────────────────────────────────────────────────────────────────────

class UserSerializerTests(TestCase):
    def test_create_user_via_serializer(self):
        data = {'email': 'new@test.com', 'name': 'New User', 'password': 'abc123'}
        s = UserSerializer(data=data)
        self.assertTrue(s.is_valid(), s.errors)
        user = s.save()
        self.assertEqual(user.email, 'new@test.com')
        self.assertEqual(user.first_name, 'New User')

    def test_duplicate_email_rejected(self):
        """Duplicate email is caught on save() via create(), not is_valid()."""
        User.objects.create_user(username='exist@test.com', email='exist@test.com', password='pass')
        data = {'email': 'exist@test.com', 'password': 'newpass'}
        s = UserSerializer(data=data)
        self.assertTrue(s.is_valid())  # passes is_valid
        from rest_framework import serializers as drf_serializers
        with self.assertRaises(drf_serializers.ValidationError):
            s.save()

    def test_phone_returns_empty_string_without_profile(self):
        user = User.objects.create_user(username='noprofile@test.com', email='noprofile@test.com', password='p')
        s = UserSerializer(user)
        self.assertEqual(s.data['phone'], '')

    def test_phone_returned_from_profile(self):
        user = User.objects.create_user(username='hasphoone@test.com', email='hasphoone@test.com', password='p')
        UserProfile.objects.create(user=user, phone='01099999999')
        s = UserSerializer(user)
        self.assertEqual(s.data['phone'], '01099999999')

    def test_address_returned_from_profile(self):
        user = User.objects.create_user(username='addr@test.com', email='addr@test.com', password='p')
        UserProfile.objects.create(user=user, address='Alexandria')
        s = UserSerializer(user)
        self.assertEqual(s.data['address'], 'Alexandria')

    def test_role_user(self):
        user = User.objects.create_user(username='u@test.com', email='u@test.com', password='p')
        s = UserSerializer(user)
        self.assertEqual(s.data['role'], 'user')

    def test_role_admin(self):
        user = User.objects.create_superuser(username='a@test.com', email='a@test.com', password='p')
        s = UserSerializer(user)
        self.assertEqual(s.data['role'], 'admin')

    def test_update_email_normalised(self):
        user = User.objects.create_user(username='old@test.com', email='old@test.com', password='p')
        s = UserSerializer(user, data={'email': '  NEW@Test.COM  '}, partial=True)
        self.assertTrue(s.is_valid(), s.errors)
        s.save()
        user.refresh_from_db()
        self.assertEqual(user.email, 'new@test.com')

    def test_update_duplicate_email_rejected(self):
        User.objects.create_user(username='taken@test.com', email='taken@test.com', password='p')
        user2 = User.objects.create_user(username='user2@test.com', email='user2@test.com', password='p')
        s = UserSerializer(user2, data={'email': 'taken@test.com'}, partial=True)
        self.assertTrue(s.is_valid())  # Validation ok but save raises
        with self.assertRaises(Exception):
            s.save()


class ProductSerializerTests(TestCase):
    def test_all_fields_serialised(self):
        p = make_product(title='Scarf', price=30)
        s = ProductSerializer(p)
        self.assertEqual(s.data['title'], 'Scarf')
        self.assertIn('price', s.data)

    def test_create_via_serializer(self):
        data = {
            'title': 'New Dress', 'title_ar': 'فستان', 'category': 'women',
            'price': '120.00', 'image': 'x.jpg',
            'description': 'Desc', 'description_ar': 'وصف',
        }
        s = ProductSerializer(data=data)
        self.assertTrue(s.is_valid(), s.errors)
        product = s.save()
        self.assertEqual(product.price, 120)


# ─────────────────────────────────────────────────────────────────────────────
# Auth API Tests
# ─────────────────────────────────────────────────────────────────────────────

class RegisterAPITests(APITestCase):
    URL = '/api/auth/register/'

    def test_successful_registration(self):
        res = self.client.post(self.URL, {
            'name': 'Fatima', 'email': 'fatima@test.com', 'password': 'secret123'
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', res.data)
        self.assertEqual(res.data['user']['email'], 'fatima@test.com')
        self.assertEqual(res.data['user']['role'], 'user')

    def test_email_normalised_on_register(self):
        res = self.client.post(self.URL, {
            'name': 'Sara', 'email': '  SARA@TEST.COM  ', 'password': 'pass'
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['user']['email'], 'sara@test.com')

    def test_duplicate_email_rejected(self):
        self.client.post(self.URL, {'email': 'dupe@test.com', 'password': 'pass'}, format='json')
        res = self.client.post(self.URL, {'email': 'dupe@test.com', 'password': 'other'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', res.data)

    def test_missing_password_returns_error(self):
        res = self.client.post(self.URL, {'email': 'nopass@test.com'}, format='json')
        # Either 400 or created depending on allow_blank, but must not crash (500)
        self.assertNotEqual(res.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)


class LoginAPITests(APITestCase):
    URL = '/api/auth/login/'

    def setUp(self):
        self.user = User.objects.create_user(
            username='login@test.com', email='login@test.com', password='correctpass'
        )

    def test_successful_login(self):
        res = self.client.post(self.URL, {'email': 'login@test.com', 'password': 'correctpass'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('token', res.data)
        self.assertIn('user', res.data)

    def test_wrong_password_rejected(self):
        res = self.client.post(self.URL, {'email': 'login@test.com', 'password': 'wrongpass'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', res.data)

    def test_unknown_email_rejected(self):
        res = self.client.post(self.URL, {'email': 'ghost@test.com', 'password': 'pass'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_email_case_insensitive(self):
        res = self.client.post(self.URL, {'email': 'LOGIN@TEST.COM', 'password': 'correctpass'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)


class UserMeAPITests(APITestCase):
    URL = '/api/auth/me/'

    def setUp(self):
        self.user = User.objects.create_user(
            username='me@test.com', email='me@test.com', password='pass', first_name='Original'
        )
        self.token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_get_returns_user_data(self):
        res = self.client.get(self.URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['email'], 'me@test.com')
        self.assertIn('phone', res.data)
        self.assertIn('address', res.data)

    def test_unauthenticated_access_denied(self):
        self.client.credentials()  # clear auth
        res = self.client.get(self.URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_updates_name(self):
        res = self.client.patch(self.URL, {'name': 'Updated'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')

    def test_put_updates_phone_in_profile(self):
        res = self.client.put(self.URL, {'phone': '01011111111'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['phone'], '01011111111')
        profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(profile.phone, '01011111111')

    def test_put_updates_address_in_profile(self):
        res = self.client.put(self.URL, {'address': 'Giza'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['address'], 'Giza')
        profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(profile.address, 'Giza')

    def test_put_updates_both_phone_and_address(self):
        res = self.client.put(self.URL, {'phone': '01099', 'address': 'Luxor'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(profile.phone, '01099')
        self.assertEqual(profile.address, 'Luxor')

    def test_put_replaces_existing_profile_phone(self):
        UserProfile.objects.create(user=self.user, phone='01000')
        res = self.client.put(self.URL, {'phone': '01099'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.phone, '01099')

    def test_update_email_via_put(self):
        res = self.client.put(self.URL, {'email': 'newemail@test.com'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'newemail@test.com')
        self.assertEqual(self.user.username, 'newemail@test.com')

    def test_role_not_writable(self):
        """Sending role in body should NOT escalate to admin."""
        res = self.client.put(self.URL, {'role': 'admin'}, format='json')
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_superuser)


class PasswordResetAPITests(APITestCase):
    URL = '/api/auth/password-reset/'

    def setUp(self):
        self.user = User.objects.create_user(
            username='reset@test.com', email='reset@test.com', password='oldpass'
        )

    def test_password_reset_success(self):
        res = self.client.post(self.URL, {'email': 'reset@test.com', 'new_password': 'newpass123'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpass123'))

    def test_unknown_email_returns_200_no_leak(self):
        """Should not reveal whether email exists."""
        res = self.client.post(self.URL, {'email': 'ghost@test.com', 'new_password': 'pass'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_missing_email_returns_400(self):
        res = self.client.post(self.URL, {'new_password': 'pass'})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


# ─────────────────────────────────────────────────────────────────────────────
# Category API Tests
# ─────────────────────────────────────────────────────────────────────────────

class CategoryAPITests(APITestCase):
    URL = '/api/categories/'

    def setUp(self):
        self.admin = User.objects.create_superuser(
            username='admin@test.com', email='admin@test.com', password='admin'
        )
        self.admin_token, _ = Token.objects.get_or_create(user=self.admin)
        self.user = User.objects.create_user(
            username='user@test.com', email='user@test.com', password='user'
        )
        self.user_token, _ = Token.objects.get_or_create(user=self.user)

    def test_list_public(self):
        Category.objects.create(name='Women', name_ar='نسائي', slug='women')
        res = self.client.get(self.URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

    def test_list_empty_when_no_categories(self):
        res = self.client.get(self.URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 0)

    def test_create_by_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        res = self.client.post(self.URL, {'name': 'Kids', 'name_ar': 'أطفال', 'slug': 'kids'})
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 1)

    def test_create_denied_for_regular_user(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token.key)
        res = self.client.post(self.URL, {'name': 'X', 'slug': 'x'})
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_denied_for_anonymous(self):
        # DRF returns 401 for unauthenticated requests (no credentials at all)
        res = self.client.post(self.URL, {'name': 'X', 'slug': 'x'})
        self.assertIn(res.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_delete_by_admin(self):
        cat = Category.objects.create(name='Del', slug='del')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        res = self.client.delete(f'{self.URL}{cat.id}/')
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Category.objects.count(), 0)

    def test_update_by_admin(self):
        cat = Category.objects.create(name='OldName', slug='old')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        res = self.client.patch(f'{self.URL}{cat.id}/', {'name': 'NewName'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        cat.refresh_from_db()
        self.assertEqual(cat.name, 'NewName')


# ─────────────────────────────────────────────────────────────────────────────
# Product API Tests
# ─────────────────────────────────────────────────────────────────────────────

class ProductAPITests(APITestCase):
    URL = '/api/products/'

    def setUp(self):
        self.admin = User.objects.create_superuser(
            username='admin@test.com', email='admin@test.com', password='admin'
        )
        self.admin_token, _ = Token.objects.get_or_create(user=self.admin)
        self.user = User.objects.create_user(
            username='user@test.com', email='user@test.com', password='user'
        )
        self.user_token, _ = Token.objects.get_or_create(user=self.user)

        self.p1 = make_product(title='Linen Dress', category='women', price=200, rating=4.8)
        self.p2 = make_product(title='Kids Shirt', title_ar='قميص', category='kids', price=60, rating=4.2, code='KD001')
        self.p3 = make_product(title='Summer Scarf', category='accessories', price=30, rating=4.5)

    def test_list_public(self):
        res = self.client.get(self.URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        results = res.data.get('results', res.data)
        self.assertEqual(len(results), 3)

    def test_filter_by_category(self):
        res = self.client.get(f'{self.URL}?category=kids')
        results = res.data.get('results', res.data)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'Kids Shirt')

    def test_filter_category_all_returns_all(self):
        res = self.client.get(f'{self.URL}?category=all')
        results = res.data.get('results', res.data)
        self.assertEqual(len(results), 3)

    def test_filter_min_price(self):
        res = self.client.get(f'{self.URL}?min_price=100')
        results = res.data.get('results', res.data)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'Linen Dress')

    def test_filter_max_price(self):
        res = self.client.get(f'{self.URL}?max_price=50')
        results = res.data.get('results', res.data)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'Summer Scarf')

    def test_filter_price_range(self):
        res = self.client.get(f'{self.URL}?min_price=50&max_price=100')
        results = res.data.get('results', res.data)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'Kids Shirt')

    def test_search_by_title(self):
        res = self.client.get(f'{self.URL}?search=Linen')
        results = res.data.get('results', res.data)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'Linen Dress')

    def test_search_by_title_ar(self):
        res = self.client.get(f'{self.URL}?search=قميص')
        results = res.data.get('results', res.data)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'Kids Shirt')

    def test_search_by_code(self):
        res = self.client.get(f'{self.URL}?search=KD001')
        results = res.data.get('results', res.data)
        self.assertEqual(len(results), 1)

    def test_sort_price_low(self):
        res = self.client.get(f'{self.URL}?sort=price-low')
        results = res.data.get('results', res.data)
        prices = [float(r['price']) for r in results]
        self.assertEqual(prices, sorted(prices))

    def test_sort_price_high(self):
        res = self.client.get(f'{self.URL}?sort=price-high')
        results = res.data.get('results', res.data)
        prices = [float(r['price']) for r in results]
        self.assertEqual(prices, sorted(prices, reverse=True))

    def test_sort_by_rating(self):
        res = self.client.get(f'{self.URL}?sort=rating')
        results = res.data.get('results', res.data)
        ratings = [r['rating'] for r in results]
        self.assertEqual(ratings, sorted(ratings, reverse=True))

    def test_filter_by_color(self):
        make_product(title='Red Blouse', colors=['red', 'blue'])
        res = self.client.get(f'{self.URL}?color=red')
        results = res.data.get('results', res.data)
        self.assertTrue(any(r['title'] == 'Red Blouse' for r in results))

    def test_filter_by_size(self):
        make_product(title='XL Jacket', sizes=['XL', 'XXL'])
        res = self.client.get(f'{self.URL}?size=XL')
        results = res.data.get('results', res.data)
        self.assertTrue(any(r['title'] == 'XL Jacket' for r in results))

    def test_filter_by_weight(self):
        make_product(title='Heavy Coat', weight=2.5)
        res = self.client.get(f'{self.URL}?min_weight=2.0')
        results = res.data.get('results', res.data)
        self.assertTrue(any(r['title'] == 'Heavy Coat' for r in results))

    def test_create_product_by_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        data = {
            'title': 'New Dress', 'title_ar': 'فستان', 'category': 'women',
            'price': '150.00', 'image': 'img.jpg',
            'description': 'Nice', 'description_ar': 'جيد',
        }
        res = self.client.post(self.URL, data, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 4)

    def test_create_product_denied_for_user(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token.key)
        res = self.client.post(self.URL, {'title': 'X'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_single_product_public(self):
        res = self.client.get(f'{self.URL}{self.p1.id}/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['title'], 'Linen Dress')

    def test_delete_product_by_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        res = self.client.delete(f'{self.URL}{self.p1.id}/')
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_update_product_by_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        res = self.client.patch(f'{self.URL}{self.p1.id}/', {'price': '250.00'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.p1.refresh_from_db()
        self.assertEqual(float(self.p1.price), 250.0)

    def test_invalid_price_filter_ignored_gracefully(self):
        res = self.client.get(f'{self.URL}?min_price=notanumber')
        self.assertEqual(res.status_code, status.HTTP_200_OK)


# ─────────────────────────────────────────────────────────────────────────────
# Order API Tests
# ─────────────────────────────────────────────────────────────────────────────

class OrderAPITests(APITestCase):
    URL = '/api/orders/'

    def setUp(self):
        self.admin = User.objects.create_superuser(
            username='admin@test.com', email='admin@test.com', password='admin'
        )
        self.admin_token, _ = Token.objects.get_or_create(user=self.admin)

        self.user = User.objects.create_user(
            username='user@test.com', email='user@test.com', password='user'
        )
        self.user_token, _ = Token.objects.get_or_create(user=self.user)

    # ── Create ────────────────────────────────────────────────────────────

    def test_authenticated_user_can_create_order(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token.key)
        payload = make_order_payload('NS-U001')
        res = self.client.post(self.URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_guest_can_create_order(self):
        payload = make_order_payload('NS-G001')
        res = self.client.post(self.URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_order_default_status_is_pending(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token.key)
        payload = make_order_payload('NS-U002')
        res = self.client.post(self.URL, payload, format='json')
        self.assertEqual(res.data['status'], 'pending')

    def test_order_linked_to_authenticated_user(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token.key)
        payload = make_order_payload('NS-U003')
        self.client.post(self.URL, payload, format='json')
        order = Order.objects.get(id='NS-U003')
        self.assertEqual(order.user, self.user)

    def test_phone_saved_to_user_profile_on_order_create(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token.key)
        payload = make_order_payload('NS-P001', shipping_info={
            'name': 'Test', 'email': 'user@test.com', 'phone': '01012345678', 'address': 'Cairo'
        })
        self.client.post(self.URL, payload, format='json')
        self.user.refresh_from_db()
        self.assertEqual(self.user.profile.phone, '01012345678')

    def test_address_saved_to_user_profile_on_order_create(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token.key)
        payload = make_order_payload('NS-A001', shipping_info={
            'name': 'Test', 'email': 'user@test.com', 'phone': '010', 'address': 'Alexandria'
        })
        self.client.post(self.URL, payload, format='json')
        self.user.refresh_from_db()
        self.assertEqual(self.user.profile.address, 'Alexandria')

    def test_phone_replaced_on_subsequent_order(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token.key)
        self.client.post(self.URL, make_order_payload('NS-PR001', shipping_info={
            'name': 'T', 'email': 'user@test.com', 'phone': '01011111111', 'address': 'Cairo'
        }), format='json')
        self.client.post(self.URL, make_order_payload('NS-PR002', shipping_info={
            'name': 'T', 'email': 'user@test.com', 'phone': '01099999999', 'address': 'Giza'
        }), format='json')
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.phone, '01099999999')
        self.assertEqual(self.user.profile.address, 'Giza')

    def test_mobile_field_alias_also_saves_phone(self):
        """shippingInfo.mobile should also be picked up as phone."""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token.key)
        payload = make_order_payload('NS-MOB001', shipping_info={
            'name': 'T', 'email': 'user@test.com', 'mobile': '01055555555', 'address': 'Cairo'
        })
        self.client.post(self.URL, payload, format='json')
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.phone, '01055555555')

    def test_city_field_alias_also_saves_address(self):
        """shippingInfo.city should also be picked up as address."""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token.key)
        payload = make_order_payload('NS-CITY001', shipping_info={
            'name': 'T', 'email': 'user@test.com', 'phone': '010', 'city': 'Aswan'
        })
        self.client.post(self.URL, payload, format='json')
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.address, 'Aswan')

    # ── Read ──────────────────────────────────────────────────────────────

    def test_user_sees_only_own_orders(self):
        other = User.objects.create_user(username='other@test.com', email='other@test.com', password='p')
        Order.objects.create(id='NS-O1', date='2026-07-21', items=[], subtotal=10, tax=1, total=11, user=self.user)
        Order.objects.create(id='NS-O2', date='2026-07-21', items=[], subtotal=20, tax=2, total=22, user=other)

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token.key)
        res = self.client.get(self.URL)
        results = res.data.get('results', res.data)
        ids = [r['id'] for r in results]
        self.assertIn('NS-O1', ids)
        self.assertNotIn('NS-O2', ids)

    def test_admin_sees_all_orders(self):
        other = User.objects.create_user(username='other@test.com', email='other@test.com', password='p')
        Order.objects.create(id='NS-A1', date='2026-07-21', items=[], subtotal=10, tax=1, total=11, user=self.user)
        Order.objects.create(id='NS-A2', date='2026-07-21', items=[], subtotal=20, tax=2, total=22, user=other)

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        res = self.client.get(self.URL)
        results = res.data.get('results', res.data)
        ids = [r['id'] for r in results]
        self.assertIn('NS-A1', ids)
        self.assertIn('NS-A2', ids)

    def test_unauthenticated_cannot_list_orders(self):
        res = self.client.get(self.URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    # ── Update / Status ───────────────────────────────────────────────────

    def test_regular_user_cannot_patch_status(self):
        order = Order.objects.create(
            id='NS-SEC1', date='2026-07-21', items=[], subtotal=10, tax=1, total=11, user=self.user
        )
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token.key)
        res = self.client.patch(f'{self.URL}{order.id}/', {'status': 'delivered'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_patch_status(self):
        order = Order.objects.create(
            id='NS-SEC2', date='2026-07-21', items=[], subtotal=10, tax=1, total=11, user=self.user
        )
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        res = self.client.patch(f'{self.URL}{order.id}/', {'status': 'accepted'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        order.refresh_from_db()
        self.assertEqual(order.status, 'accepted')

    def test_regular_user_cannot_put_order(self):
        order = Order.objects.create(
            id='NS-SEC3', date='2026-07-21', items=[], subtotal=10, tax=1, total=11, user=self.user
        )
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token.key)
        res = self.client.put(f'{self.URL}{order.id}/', {'status': 'canceled'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    # ── Cancel Action ─────────────────────────────────────────────────────

    def test_user_can_cancel_pending_order(self):
        order = Order.objects.create(
            id='NS-CAN1', date='2026-07-21', items=[], subtotal=10, tax=1, total=11,
            status='pending', user=self.user
        )
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token.key)
        res = self.client.post(f'{self.URL}{order.id}/cancel/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        order.refresh_from_db()
        self.assertEqual(order.status, 'canceled')

    def test_cannot_cancel_delivered_order(self):
        order = Order.objects.create(
            id='NS-CAN2', date='2026-07-21', items=[], subtotal=10, tax=1, total=11,
            status='delivered', user=self.user
        )
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token.key)
        res = self.client.post(f'{self.URL}{order.id}/cancel/')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', res.data)

    def test_cannot_cancel_on_delivery_order(self):
        order = Order.objects.create(
            id='NS-CAN3', date='2026-07-21', items=[], subtotal=10, tax=1, total=11,
            status='on-delivery', user=self.user
        )
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token.key)
        res = self.client.post(f'{self.URL}{order.id}/cancel/')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_cancel_already_canceled_order(self):
        order = Order.objects.create(
            id='NS-CAN4', date='2026-07-21', items=[], subtotal=10, tax=1, total=11,
            status='canceled', user=self.user
        )
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token.key)
        res = self.client.post(f'{self.URL}{order.id}/cancel/')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_can_cancel_accepted_order(self):
        order = Order.objects.create(
            id='NS-CAN5', date='2026-07-21', items=[], subtotal=10, tax=1, total=11,
            status='accepted', user=self.user
        )
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token.key)
        res = self.client.post(f'{self.URL}{order.id}/cancel/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)


# ─────────────────────────────────────────────────────────────────────────────
# Analytics API Tests
# ─────────────────────────────────────────────────────────────────────────────

class AdminAnalyticsAPITests(APITestCase):
    URL = '/api/admin/analytics/'

    def setUp(self):
        self.admin = User.objects.create_superuser(
            username='admin@test.com', email='admin@test.com', password='admin'
        )
        self.admin_token, _ = Token.objects.get_or_create(user=self.admin)
        self.user = User.objects.create_user(
            username='user@test.com', email='user@test.com', password='user'
        )
        self.user_token, _ = Token.objects.get_or_create(user=self.user)

    def _make_order(self, oid, st='delivered', total=100, method='instapay'):
        return Order.objects.create(
            id=oid, date='2026-07-21', items=[], subtotal=total, tax=0, total=total,
            status=st, payment_method=method
        )

    def test_admin_access(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        res = self.client.get(self.URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_regular_user_forbidden(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token.key)
        res = self.client.get(self.URL)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_forbidden(self):
        # DRF returns 401 when no credentials provided (not 403)
        res = self.client.get(self.URL)
        self.assertIn(res.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_response_fields_present(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        res = self.client.get(self.URL)
        for field in ['total_revenue', 'total_orders', 'pending_orders', 'delivered_orders',
                      'aov', 'fulfillment_rate', 'total_products', 'status_counts', 'payment_counts']:
            self.assertIn(field, res.data)

    def test_total_revenue_correct(self):
        self._make_order('NS-AN1', total=200)
        self._make_order('NS-AN2', total=300)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        res = self.client.get(self.URL)
        self.assertEqual(res.data['total_revenue'], 500)

    def test_fulfillment_rate_zero_when_no_orders(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        res = self.client.get(self.URL)
        self.assertEqual(res.data['fulfillment_rate'], 0)

    def test_fulfillment_rate_calculation(self):
        self._make_order('NS-AN3', st='delivered', total=100)
        self._make_order('NS-AN4', st='pending', total=100)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        res = self.client.get(self.URL)
        self.assertEqual(res.data['fulfillment_rate'], 50.0)

    def test_status_counts(self):
        self._make_order('NS-SC1', st='pending')
        self._make_order('NS-SC2', st='delivered')
        self._make_order('NS-SC3', st='canceled')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        res = self.client.get(self.URL)
        self.assertEqual(res.data['status_counts']['pending'], 1)
        self.assertEqual(res.data['status_counts']['delivered'], 1)
        self.assertEqual(res.data['status_counts']['canceled'], 1)

    def test_payment_counts(self):
        self._make_order('NS-PAY1', method='instapay')
        self._make_order('NS-PAY2', method='instapay')
        self._make_order('NS-PAY3', method='vf_cash')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        res = self.client.get(self.URL)
        self.assertEqual(res.data['payment_counts']['instapay'], 2)
        self.assertEqual(res.data['payment_counts']['vf_cash'], 1)

    def test_aov_calculation(self):
        self._make_order('NS-AOV1', total=200)
        self._make_order('NS-AOV2', total=100)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        res = self.client.get(self.URL)
        self.assertEqual(res.data['aov'], 150.0)

    def test_product_count_included(self):
        make_product()
        make_product(title='Other', price=50)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        res = self.client.get(self.URL)
        self.assertEqual(res.data['total_products'], 2)


# ─────────────────────────────────────────────────────────────────────────────
# Newsletter API Tests
# ─────────────────────────────────────────────────────────────────────────────

class NewsletterAPITests(APITestCase):
    URL = '/api/newsletter/subscribe/'

    def test_first_subscription_returns_201(self):
        res = self.client.post(self.URL, {'email': 'sub@test.com'})
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['email'], 'sub@test.com')
        self.assertTrue(res.data['created'])

    def test_duplicate_subscription_returns_200(self):
        self.client.post(self.URL, {'email': 'dupe@test.com'})
        res = self.client.post(self.URL, {'email': 'dupe@test.com'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertFalse(res.data['created'])

    def test_missing_email_returns_400(self):
        res = self.client.post(self.URL, {})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_email_normalised_to_lowercase(self):
        res = self.client.post(self.URL, {'email': 'TEST@EXAMPLE.COM'})
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['email'], 'test@example.com')

    def test_subscription_persisted_in_db(self):
        self.client.post(self.URL, {'email': 'persist@test.com'})
        self.assertTrue(NewsletterSubscriber.objects.filter(email='persist@test.com').exists())


# ─────────────────────────────────────────────────────────────────────────────
# Cart API Tests
# ─────────────────────────────────────────────────────────────────────────────

class CartAPITests(APITestCase):
    URL = '/api/cart/'
    CLEAR_URL = '/api/cart/clear/'

    def setUp(self):
        self.user = User.objects.create_user(
            username='cart@test.com', email='cart@test.com', password='pass'
        )
        self.token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def _cart_item(self, title='Dress', price='50.00', qty=1, product_id=1):
        return {
            'product_id': product_id,
            'title': title,
            'title_ar': 'فستان',
            'price': price,
            'image': 'img.jpg',
            'color': 'red',
            'size': 'M',
            'quantity': qty,
            'weight': 0.4
        }

    def test_add_item_to_cart(self):
        res = self.client.post(self.URL, self._cart_item(), format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_list_cart_returns_user_items(self):
        self.client.post(self.URL, self._cart_item('Dress'), format='json')
        self.client.post(self.URL, self._cart_item('Scarf', product_id=2), format='json')
        res = self.client.get(self.URL)
        items = res.data.get('results', res.data)
        self.assertEqual(len(items), 2)

    def test_cart_isolated_between_users(self):
        other = User.objects.create_user(username='other@test.com', email='other@test.com', password='p')
        other_token, _ = Token.objects.get_or_create(user=other)

        # Add item for self.user
        self.client.post(self.URL, self._cart_item(), format='json')

        # Switch to other user
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + other_token.key)
        res = self.client.get(self.URL)
        items = res.data.get('results', res.data)
        self.assertEqual(len(items), 0)

    def test_clear_cart_removes_all_items(self):
        self.client.post(self.URL, self._cart_item('D1', product_id=1), format='json')
        self.client.post(self.URL, self._cart_item('D2', product_id=2), format='json')
        res = self.client.delete(self.CLEAR_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        res_empty = self.client.get(self.URL)
        items = res_empty.data.get('results', res_empty.data)
        self.assertEqual(len(items), 0)

    def test_delete_single_cart_item(self):
        res_add = self.client.post(self.URL, self._cart_item(), format='json')
        item_id = res_add.data['id']
        res_del = self.client.delete(f'{self.URL}{item_id}/')
        self.assertEqual(res_del.status_code, status.HTTP_204_NO_CONTENT)

    def test_anonymous_cart_returns_empty(self):
        self.client.credentials()  # clear auth
        res = self.client.get(self.URL)
        # Should be 200 but empty since anonymous
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        items = res.data.get('results', res.data)
        self.assertEqual(len(items), 0)

    def test_cart_item_fields_returned(self):
        res = self.client.post(self.URL, self._cart_item('Test Dress', '75.00'), format='json')
        self.assertIn('id', res.data)
        self.assertIn('product_id', res.data)
        self.assertIn('price', res.data)


# ─────────────────────────────────────────────────────────────────────────────
# UserProfile API Integration Tests
# ─────────────────────────────────────────────────────────────────────────────

class UserProfileIntegrationTests(APITestCase):
    """Test that phone/address exposed on /api/auth/me/ reflects profile correctly."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='prof@test.com', email='prof@test.com', password='pass'
        )
        self.token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_no_profile_returns_empty_strings(self):
        res = self.client.get('/api/auth/me/')
        self.assertEqual(res.data['phone'], '')
        self.assertEqual(res.data['address'], '')

    def test_profile_created_on_first_phone_update(self):
        self.assertFalse(UserProfile.objects.filter(user=self.user).exists())
        self.client.put('/api/auth/me/', {'phone': '01011'}, format='json')
        self.assertTrue(UserProfile.objects.filter(user=self.user).exists())

    def test_me_returns_saved_phone(self):
        UserProfile.objects.create(user=self.user, phone='01088888888')
        res = self.client.get('/api/auth/me/')
        self.assertEqual(res.data['phone'], '01088888888')

    def test_me_returns_saved_address(self):
        UserProfile.objects.create(user=self.user, address='Sharm El Sheikh')
        res = self.client.get('/api/auth/me/')
        self.assertEqual(res.data['address'], 'Sharm El Sheikh')
