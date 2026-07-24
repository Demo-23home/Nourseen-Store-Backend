"""Newsletter subscription view."""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status

from api.models import NewsletterSubscriber


class NewsletterSubscribeView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email', '').lower().strip()
        if not email:
            return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        subscriber, created = NewsletterSubscriber.objects.get_or_create(email=email)
        return Response({
            "message": "Subscribed successfully!",
            "email": subscriber.email,
            "created": created,
        }, status=status.HTTP_200_OK if not created else status.HTTP_201_CREATED)
