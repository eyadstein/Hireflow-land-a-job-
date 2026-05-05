from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Avg, Count
from django.utils import timezone
from datetime import timedelta

from .models import Job, CompanyReview, ReviewHelpful, JobSwipe
from .serializers import JobSerializer
from .analytics import get_seeker_stats, get_recruiter_stats
from applications.models import Application

FREE_PLAN_DAILY_SWIPE_LIMIT = 20


class IsRecruiter(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_authenticated and request.user.role == 'recruiter'


class JobListCreateView(generics.ListCreateAPIView):
    serializer_class   = JobSerializer
    permission_classes = [IsRecruiter]

    def get_queryset(self):
        return Job.objects.all().order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(posted_by=self.request.user)


class JobDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class   = JobSerializer
    permission_classes = [IsRecruiter]
    queryset           = Job.objects.all()


class SeekerStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if request.user.role != 'jobseeker':
            return Response(
                {'detail': 'Only job seekers can access this endpoint.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return Response(get_seeker_stats(request.user))


class RecruiterStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if request.user.role != 'recruiter':
            return Response(
                {'detail': 'Only recruiters can access this endpoint.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return Response(get_recruiter_stats(request.user))


def serialize_review(review, requesting_user=None):
    return {
        'id':              review.id,
        'company':         review.company,
        'rating':          review.rating,
        'title':           review.title,
        'review':          review.review,
        'pros':            review.pros,
        'cons':            review.cons,
        'position':        review.position,
        'employment_type': review.employment_type,
        'is_anonymous':    review.is_anonymous,
        'reviewer':        'Anonymous' if review.is_anonymous else review.user.username,
        'helpful_count':   review.helpful_count,
        'is_mine':         review.user == requesting_user if requesting_user else False,
        'created_at':      review.created_at.strftime('%Y-%m-%d'),
        'updated_at':      review.updated_at.strftime('%Y-%m-%d'),
    }


class CompanyReviewListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        company         = request.data.get('company', '').strip()
        rating          = request.data.get('rating')
        title           = request.data.get('title', '').strip()
        review          = request.data.get('review', '').strip()
        pros            = request.data.get('pros', '')
        cons            = request.data.get('cons', '')
        position        = request.data.get('position', '')
        employment_type = request.data.get('employment_type', 'full_time')
        is_anonymous    = request.data.get('is_anonymous', False)

        if not all([company, rating, title, review]):
            return Response(
                {'error': 'company, rating, title and review are required'},
                status=400
            )

        if not isinstance(rating, int) or not (1 <= rating <= 5):
            return Response(
                {'error': 'rating must be an integer between 1 and 5'},
                status=400
            )

        if CompanyReview.objects.filter(
            user=request.user, company__iexact=company
        ).exists():
            return Response(
                {'error': 'You have already reviewed this company'},
                status=400
            )

        r = CompanyReview.objects.create(
            user=request.user, company=company, rating=rating,
            title=title, review=review, pros=pros, cons=cons,
            position=position, employment_type=employment_type,
            is_anonymous=is_anonymous,
        )
        return Response(serialize_review(r, request.user), status=201)


class CompanyReviewsByCompanyView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, company_name):
        reviews = CompanyReview.objects.filter(
            company__iexact=company_name
        ).select_related('user')

        if not reviews.exists():
            return Response(
                {'error': 'No reviews found for this company'},
                status=404
            )

        agg       = reviews.aggregate(
            average_rating=Avg('rating'),
            total_reviews=Count('id')
        )
        breakdown = {str(i): reviews.filter(rating=i).count() for i in range(1, 6)}

        return Response({
            'company':          company_name,
            'average_rating':   round(agg['average_rating'], 1),
            'total_reviews':    agg['total_reviews'],
            'rating_breakdown': breakdown,
            'reviews':          [serialize_review(r, request.user) for r in reviews],
        })


class MyReviewsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        reviews = CompanyReview.objects.filter(user=request.user)
        return Response([serialize_review(r, request.user) for r in reviews])


class CompanyReviewDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        try:
            review = CompanyReview.objects.get(pk=pk, user=request.user)
        except CompanyReview.DoesNotExist:
            return Response({'error': 'Review not found'}, status=404)

        for field in ['rating', 'title', 'review', 'pros', 'cons',
                      'position', 'employment_type', 'is_anonymous']:
            if field in request.data:
                setattr(review, field, request.data[field])

        if 'rating' in request.data:
            rating = request.data['rating']
            if not isinstance(rating, int) or not (1 <= rating <= 5):
                return Response({'error': 'rating must be between 1 and 5'}, status=400)

        review.save()
        return Response(serialize_review(review, request.user))

    def delete(self, request, pk):
        try:
            review = CompanyReview.objects.get(pk=pk, user=request.user)
            review.delete()
            return Response({'detail': 'Review deleted'}, status=204)
        except CompanyReview.DoesNotExist:
            return Response({'error': 'Review not found'}, status=404)


class MarkHelpfulView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            review = CompanyReview.objects.get(pk=pk)
        except CompanyReview.DoesNotExist:
            return Response({'error': 'Review not found'}, status=404)

        if review.user == request.user:
            return Response(
                {'error': 'You cannot vote on your own review'}, status=400
            )

        vote, created = ReviewHelpful.objects.get_or_create(
            user=request.user, review=review
        )

        if not created:
            vote.delete()
            review.helpful_count = max(0, review.helpful_count - 1)
            review.save(update_fields=['helpful_count'])
            return Response({'helpful_count': review.helpful_count, 'voted': False})

        review.helpful_count += 1
        review.save(update_fields=['helpful_count'])
        return Response({'helpful_count': review.helpful_count, 'voted': True})


def serialize_job_card(job):
    return {
        'id':          job.id,
        'title':       job.title,
        'company':     job.company,
        'location':    job.location,
        'salary':      job.salary,
        'description': job.description[:300] + '...' if len(job.description) > 300 else job.description,
        'posted_at':   job.created_at.strftime('%Y-%m-%d'),
    }


def get_swipes_today(user):
    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    return JobSwipe.objects.filter(
        user=user,
        created_at__gte=today_start
    ).count()


class SwipeFeedView(APIView):
    """
    GET /api/jobs/swipe/feed/
    Returns unseen jobs as swipe cards.
    Free plan: shows remaining swipes count.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        seen_job_ids = JobSwipe.objects.filter(
            user=request.user
        ).values_list('job_id', flat=True)

        feed = Job.objects.exclude(
            id__in=seen_job_ids
        ).exclude(
            posted_by=request.user
        ).order_by('-created_at')[:20]

        swipes_today     = get_swipes_today(request.user)
        is_pro           = request.user.plan == 'pro'
        remaining_swipes = None if is_pro else max(
            0, FREE_PLAN_DAILY_SWIPE_LIMIT - swipes_today
        )

        return Response({
            'cards':            [serialize_job_card(j) for j in feed],
            'remaining_swipes': remaining_swipes,
            'is_pro':           is_pro,
            'total_unseen':     Job.objects.exclude(id__in=seen_job_ids).count(),
        })


class SwipeActionView(APIView):
    """
    POST /api/jobs/swipe/action/
    Body: { "job_id": 1, "direction": "right|left|up" }

    right → instant apply
    left  → skip forever
    up    → save for later
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        job_id    = request.data.get('job_id')
        direction = request.data.get('direction', '').lower()

        if not job_id:
            return Response({'error': 'job_id is required'}, status=400)
        if direction not in ['right', 'left', 'up']:
            return Response(
                {'error': 'direction must be right, left, or up'},
                status=400
            )

        try:
            job = Job.objects.get(pk=job_id)
        except Job.DoesNotExist:
            return Response({'error': 'Job not found'}, status=404)

        is_pro       = request.user.plan == 'pro'
        swipes_today = get_swipes_today(request.user)

        if not is_pro and swipes_today >= FREE_PLAN_DAILY_SWIPE_LIMIT:
            return Response({
                'error':      'Daily swipe limit reached. Upgrade to Pro for unlimited swipes.',
                'limit':      FREE_PLAN_DAILY_SWIPE_LIMIT,
                'used_today': swipes_today,
                'upgrade_url': '/api/users/upgrade/',
            }, status=429)

        swipe, created = JobSwipe.objects.get_or_create(
            user=request.user,
            job=job,
            defaults={'direction': direction}
        )

        if not created:
            return Response(
                {'error': 'You have already swiped on this job'},
                status=400
            )

        result = {
            'job_id':    job.id,
            'direction': direction,
            'job_title': job.title,
            'company':   job.company,
        }

        if direction == 'right':
            if not Application.objects.filter(
                user=request.user, job=job
            ).exists():
                Application.objects.create(
                    user=request.user,
                    job=job,
                    job_title=job.title,
                    company_name=job.company,
                    status='applied',
                )
            result['message'] = 'Applied successfully!'
            result['applied']  = True

        elif direction == 'up':
            result['message'] = 'Job saved for later!'
            result['saved']   = True

        elif direction == 'left':
            result['message'] = 'Job skipped.'
            result['skipped'] = True

        remaining = None if is_pro else max(
            0, FREE_PLAN_DAILY_SWIPE_LIMIT - (swipes_today + 1)
        )
        result['remaining_swipes'] = remaining

        return Response(result, status=201)


class SwipeSavedView(APIView):
    """
    GET /api/jobs/swipe/saved/
    Returns all jobs swiped up (saved).
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        saved_swipes = JobSwipe.objects.filter(
            user=request.user, direction='up'
        ).select_related('job')

        return Response([
            serialize_job_card(s.job) for s in saved_swipes
        ])


class SwipeAppliedView(APIView):
    """
    GET /api/jobs/swipe/applied/
    Returns all jobs applied via swipe right.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        applied_swipes = JobSwipe.objects.filter(
            user=request.user, direction='right'
        ).select_related('job')

        return Response([
            serialize_job_card(s.job) for s in applied_swipes
        ])


class SwipeLimitView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        is_pro       = request.user.plan == 'pro'
        swipes_today = get_swipes_today(request.user)

        return Response({
            'is_pro':           is_pro,
            'swipes_today':     swipes_today,
            'daily_limit':      None if is_pro else FREE_PLAN_DAILY_SWIPE_LIMIT,
            'remaining_swipes': None if is_pro else max(
                0, FREE_PLAN_DAILY_SWIPE_LIMIT - swipes_today
            ),
            'reset_at': (
                timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
                + timedelta(days=1)
            ).strftime('%Y-%m-%d %H:%M:%S'),
        })