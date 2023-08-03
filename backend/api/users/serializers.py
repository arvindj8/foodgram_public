from django.contrib.auth import get_user_model
from djoser.serializers import (
    UserCreateSerializer as DjoserUserCreateSerializer
)
from djoser.serializers import UserSerializer as DjoserUserSerialiser
from rest_framework import serializers

from users.models import Subscription

User = get_user_model()


class UserSerializer(DjoserUserSerialiser):
    """Сериализация для User. Проверка полей username и email."""
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email',
                  'first_name', 'last_name', 'is_subscribed')

    def validate_email(self, value):
        """Функция для проверки существующего Email."""
        norm_email = value.lower()
        if User.objects.filter(email=norm_email).exists():
            raise serializers.ValidationError('Email уже зарегистрирован')
        return norm_email

    def get_is_subscribed(self, obj):
        """Функция для проверки наличия подписки на автора."""
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Subscription.objects.filter(
            user=request.user, author=obj
        ).exists()


class UserCreateSerializer(DjoserUserCreateSerializer):
    """Сериализатор для создания объекта пользователя."""

    class Meta:
        fields = ('username', 'password', 'email',
                  'first_name', 'last_name',)
        model = User
