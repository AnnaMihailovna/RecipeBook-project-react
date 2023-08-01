from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import F, Q


class User(AbstractUser):
    """Модель пользователя."""
    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        max_length=254,
        unique=True,
        help_text=('Укажите свой email'),
    )
    username = models.CharField(
        verbose_name=('Логин'),
        max_length=150,
        unique=True,
        help_text=('Укажите свой никнейм'),
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150,
        help_text=('Укажите своё имя'),
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150,
        help_text=('Укажите свою фамилию'),
    )
    password = models.CharField(
        verbose_name=('Пароль'),
        max_length=150,
        help_text=('Введите пароль'),
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'password',)

    class Meta:
        ordering = ('username', )
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        constraints = [
            models.UniqueConstraint(
                fields=['username', 'email'],
                name='unique_user'
            )
        ]

    def __str__(self):
        return self.username


class Follow(models.Model):
    """Модель подписки."""
    user = models.ForeignKey(
        User,
        related_name='follower',
        verbose_name='Подписчик',
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        User,
        related_name='following',
        verbose_name='Автор',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'user'],
                name='unique_follow'),
            models.CheckConstraint(
                check=~Q(user=F('author')),
                name='no_self_follow')
        ]

    def __str__(self):
        return f'Пользователь {self.user} подписан(а) на {self.author}'
