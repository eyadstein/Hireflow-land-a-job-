from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Avg, Count
from .models import Job, CompanyReview, ReviewHelpful
from .serializers import JobSerializer
from .analytics import get_seeker_stats, get_recruiter_stats


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
        data = get_seeker_stats(request.user)
        return Response(data)


class RecruiterStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if request.user.role != 'recruiter':
            return Response(
                {'detail': 'Only recruiters can access this endpoint.'},
                status=status.HTTP_403_FORBIDDEN
            )
        data = get_recruiter_stats(request.user)
        return Response(data)


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
    """
    POST /api/jobs/reviews/   → create a review
    """
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
            user            = request.user,
            company         = company,
            rating          = rating,
            title           = title,
            review          = review,
            pros            = pros,
            cons            = cons,
            position        = position,
            employment_type = employment_type,
            is_anonymous    = is_anonymous,
        )

        return Response(
            serialize_review(r, request.user),
            status=201
        )


class CompanyReviewsByCompanyView(APIView):
    """
    GET /api/jobs/reviews/company/<name>/
    Returns aggregated rating + all reviews for a company.
    """
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

        agg = reviews.aggregate(
            average_rating=Avg('rating'),
            total_reviews=Count('id')
        )

        breakdown = {}
        for i in range(1, 6):
            breakdown[str(i)] = reviews.filter(rating=i).count()

        return Response({
            'company':          company_name,
            'average_rating':   round(agg['average_rating'], 1),
            'total_reviews':    agg['total_reviews'],
            'rating_breakdown': breakdown,
            'reviews': [
                serialize_review(r, request.user) for r in reviews
            ],
        })


class MyReviewsView(APIView):
    """
    GET /api/jobs/reviews/my/  → list current user's reviews
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        reviews = CompanyReview.objects.filter(user=request.user)
        return Response([
            serialize_review(r, request.user) for r in reviews
        ])


class CompanyReviewDetailView(APIView):
    """
    PATCH  /api/jobs/reviews/<id>/  → edit own review
    DELETE /api/jobs/reviews/<id>/  → delete own review
    """
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        try:
            review = CompanyReview.objects.get(pk=pk, user=request.user)
        except CompanyReview.DoesNotExist:
            return Response({'error': 'Review not found'}, status=404)

        updatable = ['rating', 'title', 'review', 'pros', 'cons',
                     'position', 'employment_type', 'is_anonymous']

        for field in updatable:
            if field in request.data:
                setattr(review, field, request.data[field])

        if 'rating' in request.data:
            rating = request.data['rating']
            if not isinstance(rating, int) or not (1 <= rating <= 5):
                return Response(
                    {'error': 'rating must be between 1 and 5'},
                    status=400
                )

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
    """
    POST /api/jobs/reviews/<id>/helpful/
    Toggle helpful vote on a review.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            review = CompanyReview.objects.get(pk=pk)
        except CompanyReview.DoesNotExist:
            return Response({'error': 'Review not found'}, status=404)

        if review.user == request.user:
            return Response(
                {'error': 'You cannot vote on your own review'},
                status=400
            )

        vote, created = ReviewHelpful.objects.get_or_create(
            user=request.user, review=review
        )

        if not created:
            vote.delete()
            review.helpful_count = max(0, review.helpful_count - 1)
            review.save(update_fields=['helpful_count'])
            return Response({
                'helpful_count': review.helpful_count,
                'voted':         False,
            })

        review.helpful_count += 1
        review.save(update_fields=['helpful_count'])
        return Response({
            'helpful_count': review.helpful_count,
            'voted':         True,
        })