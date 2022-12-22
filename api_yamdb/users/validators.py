import re

from django.core.exceptions import ValidationError


def validate_username(value):
    if value == 'me':
        raise ValidationError(
            ('Имя пользователя <me> зарезервировано системой. '
             'Пожалуйста используйте другое имя.'),
            params={'value': value},
        )
    if re.search(r'^[\w.@+-]+$', value) is None:
        raise ValidationError(
            (f'Недопустимые символы в имени пользователя -> {value}! '
             f'Letters, digits and @/./+/-/_ only'),
            params={'value': value},
        )
