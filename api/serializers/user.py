"""User serializer — handles registration, profile update, phone/address via UserProfile."""
from rest_framework import serializers
from django.contrib.auth.models import User
from api.models import UserProfile


class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    name = serializers.CharField(source='first_name', required=False, allow_blank=True)
    phone = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'name', 'phone', 'address', 'role', 'password')
        extra_kwargs = {
            'password': {'write_only': True, 'required': False},
            'username': {'required': False},
        }

    def get_role(self, obj):
        return 'admin' if obj.is_superuser else 'user'

    def get_phone(self, obj):
        if hasattr(obj, 'profile') and obj.profile.phone:
            return obj.profile.phone
        return ""

    def get_address(self, obj):
        if hasattr(obj, 'profile') and obj.profile.address:
            return obj.profile.address
        return ""

    def create(self, validated_data):
        email = validated_data.get('email', '').lower().strip()
        username = email
        password = validated_data.get('password')
        name = validated_data.get('first_name', '')

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": "A user with this email already exists."})

        return User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=name,
        )

    def update(self, instance, validated_data):
        if 'first_name' in validated_data:
            instance.first_name = validated_data['first_name']
        if 'email' in validated_data:
            new_email = validated_data['email'].lower().strip()
            if new_email != instance.email and User.objects.filter(email=new_email).exclude(pk=instance.pk).exists():
                raise serializers.ValidationError({"email": "This email is already in use."})
            instance.email = new_email
            instance.username = new_email
        if 'password' in validated_data and validated_data['password']:
            instance.set_password(validated_data['password'])
        instance.save()
        return instance
