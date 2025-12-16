import re

from django.core.exceptions import ValidationError


def validate_password(password):
    regex = r"^(?=.*[A-Z])(?=.*\d)(?=.*[,.\-_]).*$"
    if not re.match(regex, password):
        raise ValidationError(
            "La contraseña debe tener al menos una letra mayúscula, un número y un caracter especial.")
    return True


def get_request_login_data(request):
    return {
        'ip': request.META.get('REMOTE_ADDR') if request.META.get('REMOTE_ADDR') else request.META.get('HTTP_X_FORWARDED_FOR'),
        'os': request.META.get('HTTP_USER_AGENT') if request.META.get('HTTP_USER_AGENT') else None
    }
