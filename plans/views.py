from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.utils import timezone
from .models import PlanUpgradeRequest
from .services import get_user_plan_status, get_plan_limits


class PlanStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Get current user's plan status and usage."""
        status = get_user_plan_status(request.user)
        return Response(status)


class PlanCompareView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        """Compare free vs pro plans."""
        return Response({
            'plans': {
                'free': {
                    'price': 0,
                    'currency': 'USD',
                    'limits': get_plan_limits('free'),
                    'features': [
                        '5 AI uses per day',
                        'Save up to 10 jobs',
                        '2 job alerts',
                        'Basic job search',
                        'Apply to jobs',
                    ]
                },
                'pro': {
                    'price': 9.99,
                    'currency': 'USD',
                    'limits': get_plan_limits('pro'),
                    'features': [
                        'Unlimited AI uses',
                        'Save unlimited jobs',
                        '20 job alerts',
                        'Salary insights',
                        'Interview coach',
                        'CV builder',
                        'Priority support',
                        'Advanced job matching',
                    ]
                }
            }
        })


class RequestUpgradeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """Request plan upgrade."""
        if request.user.plan == 'pro':
            return Response({
                'message': 'You are already on Pro plan!'
            })

        payment_ref = request.data.get('payment_reference', '')

        upgrade_request, created = PlanUpgradeRequest.objects.get_or_create(
            user=request.user,
            status='pending',
            defaults={'payment_reference': payment_ref}
        )

        if not created:
            return Response({
                'message': 'Upgrade request already pending',
                'request_id': upgrade_request.id,
            })

        return Response({
            'message': 'Upgrade request submitted successfully',
            'request_id': upgrade_request.id,
            'status': 'pending',
        }, status=201)


class AdminApproveUpgradeView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, request_id):
        """Admin approves upgrade request."""
        try:
            upgrade_request = PlanUpgradeRequest.objects.get(id=request_id)
        except PlanUpgradeRequest.DoesNotExist:
            return Response({'error': 'Request not found'}, status=404)

        upgrade_request.status = 'approved'
        upgrade_request.processed_at = timezone.now()
        upgrade_request.save()

        # Upgrade user
        user = upgrade_request.user
        user.plan = 'pro'
        user.save()

        return Response({
            'message': f"{user.username} upgraded to Pro successfully",
            'user': user.username,
            'plan': 'pro',
        })