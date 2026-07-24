"""
OrderService — business logic for order creation and user profile sync.
Keeps OrderViewSet thin and testable independently.
"""
from api.models import UserProfile


class OrderService:
    @staticmethod
    def extract_contact_from_order(order, request_data):
        """
        Extract phone and address from order.shippingInfo or request root data.
        Supports both 'phone'/'address' and 'mobile'/'city' field aliases.
        """
        phone = None
        address = None

        if isinstance(order.shippingInfo, dict):
            phone = order.shippingInfo.get('phone') or order.shippingInfo.get('mobile')
            address = order.shippingInfo.get('address') or order.shippingInfo.get('city')

        if not phone:
            phone = request_data.get('phone')
        if not address:
            address = request_data.get('address')

        return phone, address

    @staticmethod
    def sync_user_profile(user, phone, address):
        """
        Save or update the user's profile phone and address.
        If profile doesn't exist, creates one. Always replaces the previous value.
        """
        if not (phone or address):
            return

        profile, _ = UserProfile.objects.get_or_create(user=user)
        if phone:
            profile.phone = str(phone).strip()
        if address:
            profile.address = str(address).strip()
        profile.save()
