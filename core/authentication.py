"""
OTP generation and email sending utilities.
"""

import random
import string
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


def generate_otp(length=None):
    """Generate a numeric OTP code."""
    length = length or getattr(settings, 'OTP_LENGTH', 6)
    return ''.join(random.choices(string.digits, k=length))


def send_otp_email(email, otp_code):
    """Send OTP code via email."""
    send_mail(
        subject='Kwijiya — Código de Verificação',
        message=(
            f'O seu código de verificação é: {otp_code}\n\n'
            f'Este código expira em {getattr(settings, "OTP_EXPIRY_MINUTES", 10)} minutos.\n\n'
            f'Se não solicitou este código, ignore esta mensagem.'
        ),
        from_email='noreply@kwijiya.ao',
        recipient_list=[email],
        fail_silently=False,
    )


def get_otp_expiry():
    """Return the expiry datetime for a new OTP."""
    minutes = getattr(settings, 'OTP_EXPIRY_MINUTES', 10)
    return timezone.now() + timedelta(minutes=minutes)
