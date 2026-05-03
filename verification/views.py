from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from .services import (
    calculate_profile_completion,
    get_missing_fields,
    can_apply_to_job,
    assign_badge,
)
from .models import ProfileVerification


class ProfileCompletionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Get profile completion status."""
        verification = calculate_profile_completion(request.user)
        missing = get_missing_fields(request.user)

        return Response({
            'completion_percentage': verification.completion_percentage,
            'status': verification.status,
            'is_verified': request.user.is_profile_verified,
            'badge': request.user.badge,
            'badge_color': get_badge_color(request.user.badge),
            'missing_fields': missing,
            'checklist': {
                'has_name': verification.has_name,
                'has_email': verification.has_email,
                'has_phone': verification.has_phone,
                'has_location': verification.has_location,
                'has_bio': verification.has_bio,
                'has_skills': verification.has_skills,
                'has_experience_level': verification.has_experience_level,
                'has_education': verification.has_education,
                'has_desired_roles': verification.has_desired_roles,
                'has_gender': verification.has_gender,
                'has_profile_photo': verification.has_profile_photo,
                'has_linkedin': verification.has_linkedin,
                'has_resume': verification.has_resume,
                'has_portfolio': verification.has_portfolio,
            }
        })


class VerifyProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """Trigger profile verification check."""
        verification = calculate_profile_completion(request.user)
        missing = get_missing_fields(request.user)

        if request.user.is_profile_verified:
            return Response({
                'verified': True,
                'badge': request.user.badge,
                'badge_color': get_badge_color(request.user.badge),
                'message': f'Profile verified! You have a {request.user.badge} badge.',
                'completion': verification.completion_percentage,
            })

        return Response({
            'verified': False,
            'completion': verification.completion_percentage,
            'message': 'Complete your profile to get verified',
            'missing_fields': missing,
        }, status=400)


class BadgeInfoView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        """Get info about all badges."""
        return Response({
            'badges': [
                {
                    'type': 'blue',
                    'emoji': '🔵',
                    'name': 'Verified Professional',
                    'description': 'Awarded to verified male job seekers',
                    'requirements': 'Complete profile + verified',
                },
                {
                    'type': 'pink',
                    'emoji': '🌸',
                    'name': 'Verified Professional',
                    'description': 'Awarded to verified female job seekers',
                    'requirements': 'Complete profile + verified',
                },
                {
                    'type': 'gold',
                    'emoji': '👑',
                    'name': 'Pro Member',
                    'description': 'Awarded to Pro plan verified users',
                    'requirements': 'Pro plan + complete profile',
                },
            ]
        })


class CanApplyView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Check if current user can apply to jobs."""
        allowed, reason = can_apply_to_job(request.user)
        if allowed:
            return Response({
                'can_apply': True,
                'badge': request.user.badge,
            })
        return Response({
            'can_apply': False,
            **reason,
        }, status=403)


def get_badge_color(badge):
    colors = {
        'blue': '#3182ce',
        'pink': '#d53f8c',
        'gold': '#d69e2e',
        'none': None,
    }
    return colors.get(badge)