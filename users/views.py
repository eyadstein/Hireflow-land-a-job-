import pyotp
import qrcode
import base64
from io import BytesIO
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import BlacklistedToken, SecurityAuditLog, TwoFactorCode
from .serializers import RegisterSerializer, UserSerializer
from .middleware import get_client_ip

User = get_user_model()


def log_event(user, event, request, details=None):
    SecurityAuditLog.objects.create(
        user       = user,
        event      = event,
        ip_address = get_client_ip(request),
        user_agent = request.META.get('HTTP_USER_AGENT', '')[:500],
        details    = details or {},
    )


class RegisterView(generics.CreateAPIView):
    serializer_class   = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user    = serializer.save()
        refresh = RefreshToken.for_user(user)

        log_event(user, 'login', request, {'method': 'register'})

        return Response({
            'user':    UserSerializer(user).data,
            'access':  str(refresh.access_token),
            'refresh': str(refresh),
        })


class SecureLoginView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        username = request.data.get('username', '')

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            SecurityAuditLog.objects.create(
                event      = 'login_failed',
                ip_address = get_client_ip(request),
                user_agent = request.META.get('HTTP_USER_AGENT', '')[:500],
                details    = {'username': username, 'reason': 'user not found'},
            )
            return Response({'error': 'Invalid credentials'}, status=401)

        if user.is_locked_out():
            log_event(user, 'locked_out', request)
            remaining = int((user.lockout_until - timezone.now()).total_seconds() / 60)
            return Response({
                'error':             f'Account locked. Try again in {remaining} minutes.',
                'lockout_until':     user.lockout_until.isoformat(),
                'remaining_minutes': remaining,
            }, status=429)

        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            user.reset_failed_login()
            log_event(user, 'login', request)
        else:
            user.record_failed_login()
            attempts_left = 5 - user.failed_login_attempts
            log_event(user, 'login_failed', request, {
                'attempts_left': max(0, attempts_left)
            })
            if attempts_left > 0:
                response.data['attempts_left'] = attempts_left

        return response


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class   = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        log_event(request.user, 'profile_update', request)
        return response


class AllUsersView(generics.ListAPIView):
    serializer_class   = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset           = User.objects.all()


class LogoutView(APIView):
    """
    POST /api/users/logout/
    Body: { "refresh": "<refresh_token>" }
    Blacklists the refresh token so it can't be reused.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')

        if not refresh_token:
            return Response({'error': 'refresh token is required'}, status=400)

        try:
            token = RefreshToken(refresh_token)
            BlacklistedToken.objects.get_or_create(
                token=refresh_token,
                defaults={'user': request.user}
            )
            token.blacklist() if hasattr(token, 'blacklist') else None
            log_event(request.user, 'logout', request)
            return Response({'detail': 'Logged out successfully'})

        except Exception as e:
            return Response({'error': str(e)}, status=400)


class SecurityAuditLogView(APIView):
    """
    GET /api/users/security-log/
    Returns the authenticated user's security event history.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        logs = SecurityAuditLog.objects.filter(
            user=request.user
        ).order_by('-created_at')[:50]

        return Response([
            {
                'event':      log.event,
                'ip_address': log.ip_address,
                'details':    log.details,
                'created_at': log.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            }
            for log in logs
        ])


class TwoFactorSetupView(APIView):
    """
    POST /api/users/2fa/setup/
    Generates a TOTP secret and QR code for Google Authenticator.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user   = request.user
        secret = pyotp.random_base32()

        user.two_factor_secret = secret
        user.save(update_fields=['two_factor_secret'])

        totp    = pyotp.TOTP(secret)
        otp_uri = totp.provisioning_uri(
            name=user.email,
            issuer_name='HireFlow'
        )

        # Generate QR code as base64
        qr  = qrcode.make(otp_uri)
        buf = BytesIO()
        qr.save(buf, format='PNG')
        qr_base64 = base64.b64encode(buf.getvalue()).decode()

        return Response({
            'secret':     secret,
            'otp_uri':    otp_uri,
            'qr_code':    f"data:image/png;base64,{qr_base64}",
            'message':    'Scan the QR code with Google Authenticator then verify with /2fa/verify/',
        })


class TwoFactorVerifyView(APIView):
    """
    POST /api/users/2fa/verify/
    Body: { "code": "123456" }
    Verifies the TOTP code and enables 2FA.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        code = request.data.get('code', '').strip()

        if not code:
            return Response({'error': 'code is required'}, status=400)

        if not user.two_factor_secret:
            return Response(
                {'error': 'Please setup 2FA first via /2fa/setup/'},
                status=400
            )

        totp = pyotp.TOTP(user.two_factor_secret)

        if totp.verify(code, valid_window=1):
            user.two_factor_enabled = True
            user.save(update_fields=['two_factor_enabled'])
            log_event(user, '2fa_enabled', request)
            return Response({
                'detail':  '2FA enabled successfully',
                'enabled': True,
            })

        return Response({'error': 'Invalid code. Try again.'}, status=400)


class TwoFactorDisableView(APIView):
    """
    POST /api/users/2fa/disable/
    Body: { "code": "123456" }
    Verifies code then disables 2FA.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        code = request.data.get('code', '').strip()

        if not code:
            return Response({'error': 'code is required'}, status=400)

        if not user.two_factor_enabled:
            return Response({'error': '2FA is not enabled'}, status=400)

        totp = pyotp.TOTP(user.two_factor_secret)

        if totp.verify(code, valid_window=1):
            user.two_factor_enabled = False
            user.two_factor_secret  = ''
            user.save(update_fields=['two_factor_enabled', 'two_factor_secret'])
            log_event(user, '2fa_disabled', request)
            return Response({
                'detail':  '2FA disabled successfully',
                'enabled': False,
            })

        return Response({'error': 'Invalid code. Try again.'}, status=400)