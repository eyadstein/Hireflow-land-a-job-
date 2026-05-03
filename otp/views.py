from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from .services import send_email_otp, send_sms_otp, verify_otp


class SendEmailOTPView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """Send OTP to user's email."""
        purpose = request.data.get('purpose', 'verify')
        success, result = send_email_otp(request.user, purpose)

        if success:
            return Response({
                'message': f'OTP sent to {request.user.email}',
                'email': mask_email(request.user.email),
                'expires_in': '10 minutes',
            })
        return Response({
            'error': 'Failed to send OTP',
            'detail': str(result)
        }, status=500)


class SendPhoneOTPView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """Send OTP to user's phone."""
        if not request.user.phone:
            return Response({
                'error': 'No phone number on file. Please update your profile first.'
            }, status=400)

        purpose = request.data.get('purpose', 'verify')
        success, result = send_sms_otp(request.user, purpose)

        if success:
            return Response({
                'message': f'OTP sent to {mask_phone(request.user.phone)}',
                'expires_in': '10 minutes',
            })
        return Response({
            'error': 'Failed to send SMS',
            'detail': str(result)
        }, status=500)


class VerifyEmailOTPView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """Verify email OTP."""
        code = request.data.get('code', '')
        purpose = request.data.get('purpose', 'verify')

        if not code:
            return Response({'error': 'code is required'}, status=400)

        success, message = verify_otp(
            request.user, code, 'email', purpose
        )

        if success:
            return Response({
                'verified': True,
                'message': message,
                'badge': request.user.badge,
                'is_profile_verified': request.user.is_profile_verified,
            })
        return Response({
            'verified': False,
            'message': message,
        }, status=400)


class VerifyPhoneOTPView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """Verify phone OTP."""
        code = request.data.get('code', '')
        purpose = request.data.get('purpose', 'verify')

        if not code:
            return Response({'error': 'code is required'}, status=400)

        success, message = verify_otp(
            request.user, code, 'phone', purpose
        )

        if success:
            return Response({
                'verified': True,
                'message': message,
                'badge': request.user.badge,
                'is_profile_verified': request.user.is_profile_verified,
            })
        return Response({
            'verified': False,
            'message': message,
        }, status=400)


class OTPStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Get verification status for current user."""
        from .models import OTP
        from django.utils import timezone

        # Check latest email OTP
        email_verified = OTP.objects.filter(
            user=request.user,
            otp_type='email',
            is_verified=True
        ).exists()

        phone_verified = OTP.objects.filter(
            user=request.user,
            otp_type='phone',
            is_verified=True
        ).exists()

        return Response({
            'email_verified': email_verified,
            'phone_verified': phone_verified,
            'is_profile_verified': request.user.is_profile_verified,
            'badge': request.user.badge,
        })


# Helper functions
def mask_email(email):
    parts = email.split('@')
    name = parts[0]
    masked = name[:2] + '*' * (len(name) - 2)
    return f"{masked}@{parts[1]}"


def mask_phone(phone):
    return phone[:4] + '*' * (len(phone) - 6) + phone[-2:]