import re

from django.core.exceptions import ValidationError


def validate_username(value):
    """
    Функция для валидации, что /me зарезервировано системой.
    Проверяет соответствие только буквам, цифрам и определенным символам.
    """
    if value.lower() == 'me':
        raise ValidationError(
            f'{value} зарезервированною системой.'
        )
    if not re.match(r'^[\w.@+-]+$', value):
        raise ValidationError(
            f'{value} содержит неизвестные символы.'
        )
