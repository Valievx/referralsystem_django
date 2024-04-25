from phonenumber_field.modelfields import PhoneNumberField
from uuid import uuid4

from django.db import models
from django.contrib.auth.models import AbstractUser

from .managers import CustomUserManager


class User(AbstractUser):
    """Модель пользователя."""
    username = None
    email = None
    phone_number = PhoneNumberField(
        'Номер телефона',
        max_length=12,
        unique=True)
    confirmation_code = models.CharField(
        'Код подтверждения',
        max_length=4,
        blank=True)
    my_invite_code = models.CharField(
        'Инвайт-код для приглашения',
        max_length=6,
        unique=True,
        editable=False
    )
    inviter_code = models.CharField(
        'Инвайт-код пригласившего',
        max_length=6,
        blank=True)

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def generate_invite_code(self):
        """Генерация инвайт-кода."""
        code = str(uuid4())[:6]
        self.my_invite_code = code

    def save(self, *args, **kwargs):
        """Переопределение метода save для генерации инвайт-кода."""
        if not self.my_invite_code:
            self.generate_invite_code()
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.phone_number)
