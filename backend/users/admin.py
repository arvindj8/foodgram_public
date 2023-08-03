from django.contrib import admin

from .models import Subscription, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Админка для модели юзеров."""
    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
    )
    list_filter = ('username', 'email',)
    search_fields = ('username', 'email', 'first_name', 'last_name')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Админка для модели подписок."""
    list_display = ('id', 'user', 'author')
    list_filter = ('user', 'author')
    search_fields = ('user', 'author')
