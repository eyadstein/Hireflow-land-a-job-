from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, generics
from .models import ReferralCode, Referral
from .serializers import ReferralCodeSerializer, ReferralSerializer
from .services import (
    get_or_create_referral_code,
    process_referral,
    get_referral_stats
)


class MyReferralCodeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Get or create referral code for current user."""
        code = get_or_create_referral_code(request.user)
        return Response(ReferralCodeSerializer(code).data)


class ReferralStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Get full referral stats."""
        stats = get_referral_stats(request.user)
        return Response(stats)


class MyReferralsView(generics.ListAPIView):
    serializer_class = ReferralSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Referral.objects.filter(referrer=self.request.user)


class ValidateReferralCodeView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """Validate a referral code (called during registration)."""
        code = request.data.get('code', '').upper()
        if not code:
            return Response(
                {'error': 'code is required'},
                status=400
            )

        exists = ReferralCode.objects.filter(code=code).exists()
        if exists:
            referrer = ReferralCode.objects.get(code=code).user
            return Response({
                'valid': True,
                'referrer_name': referrer.username,
                'message': f"Valid code! You were referred by {referrer.username}"
            })
        return Response({
            'valid': False,
            'message': 'Invalid referral code'
        })


class ApplyReferralView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """Apply a referral code for current user."""
        code = request.data.get('code', '')
        if not code:
            return Response(
                {'error': 'code is required'},
                status=400
            )

        success = process_referral(request.user, code)
        if success:
            return Response({
                'success': True,
                'message': 'Referral applied successfully!'
            })
        return Response({
            'success': False,
            'message': 'Invalid code or already used'
        }, status=400)