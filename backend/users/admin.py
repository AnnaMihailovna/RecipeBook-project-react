from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import Follow

User = get_user_model()


class UserAdmin(admin.ModelAdmin):
    """Отображение модели пользователя в админке."""
    list_display = ('pk', 'username', 'email', 'first_name', 'last_name')
    list_filter = ('email', 'first_name')
    search_fields = ('email', 'first_name')
    ordering = ('username',)
    empty_value_display = '-пусто-'


class FollowAdmin(admin.ModelAdmin):
    """Отображение модели подписок в админке."""
    list_display = ('pk', 'user', 'author')
    list_filter = ('user', 'author')
    empty_value_display = '-пусто-'


admin.site.register(User, UserAdmin)
admin.site.register(Follow, FollowAdmin)
