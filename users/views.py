"""
Auth views: Request OTP, Verify OTP, Guest login.
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone

from .models import CustomUser, OTPCode
from .serializers import RequestOTPSerializer, VerifyOTPSerializer
from core.authentication import generate_otp, send_otp_email, get_otp_expiry


def _get_tokens_for_user(user):
    """Generate JWT token pair for a user."""
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


@api_view(['POST'])
@permission_classes([AllowAny])
def request_otp(request):
    """
    Send a 6-digit OTP to the provided email.
    Creates a new OTPCode record; invalidates previous unused ones.
    """
    serializer = RequestOTPSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.validated_data['email']

    # Invalidate previous unused OTPs for this email
    OTPCode.objects.filter(email=email, is_used=False).update(is_used=True)

    # Generate and save new OTP
    code = generate_otp()
    OTPCode.objects.create(
        email=email,
        code=code,
        expires_at=get_otp_expiry(),
    )

    # Send OTP via email (console in dev)
    send_otp_email(email, code)

    return Response(
        {'message': 'Código OTP enviado para o seu email.'},
        status=status.HTTP_200_OK,
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp(request):
    """
    Verify OTP code. If valid, creates user (if new) and returns JWT tokens.
    """
    serializer = VerifyOTPSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    email = serializer.validated_data['email']
    otp_code = serializer.validated_data['otp_code']

    # Find valid OTP
    try:
        otp = OTPCode.objects.get(
            email=email,
            code=otp_code,
            is_used=False,
        )
    except OTPCode.DoesNotExist:
        return Response(
            {'error': 'Código OTP inválido ou expirado.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not otp.is_valid:
        return Response(
            {'error': 'Código OTP expirado.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Mark OTP as used
    otp.is_used = True
    otp.save()

    # Get or create user
    user, created = CustomUser.objects.get_or_create(
        email=email,
        defaults={'username': email.split('@')[0]},
    )

    # Update last activity
    user.last_activity = timezone.now()
    user.save(update_fields=['last_activity'])

    tokens = _get_tokens_for_user(user)

    return Response({
        'tokens': tokens,
        'user': {
            'id': str(user.id),
            'email': user.email,
            'username': user.username,
            'is_new': created,
        },
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def guest_login(request):
    """
    Create an anonymous guest account and return JWT tokens.
    Guest accounts have limited functionality.
    """
    user = CustomUser.objects.create_guest()
    tokens = _get_tokens_for_user(user)

    return Response({
        'tokens': tokens,
        'user': {
            'id': str(user.id),
            'username': user.username,
            'is_guest': True,
        },
    }, status=status.HTTP_201_CREATED)
