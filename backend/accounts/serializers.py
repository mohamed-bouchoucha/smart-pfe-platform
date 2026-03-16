from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'password', 'password_confirm',
            'first_name', 'last_name', 'university', 'field_of_study',
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password_confirm'):
            raise serializers.ValidationError(
                {"password_confirm": "Les mots de passe ne correspondent pas."}
            )
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user profile display and updates."""

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name',
            'role', 'university', 'field_of_study', 'bio', 'avatar',
            'date_joined', 'is_active',
        ]
        read_only_fields = ['id', 'email', 'role', 'date_joined', 'is_active']


class UserAdminSerializer(serializers.ModelSerializer):
    """Serializer for admin to manage users."""

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name',
            'role', 'university', 'field_of_study', 'bio',
            'date_joined', 'is_active', 'last_login',
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']


class LoginSerializer(serializers.Serializer):
    """Serializer for user login."""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
