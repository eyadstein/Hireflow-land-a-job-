from django.urls import path
from .views import (
    JobListCreateView,
    JobDetailView,
    SeekerStatsView,
    RecruiterStatsView,
    CompanyReviewListCreateView,
    CompanyReviewsByCompanyView,
    MyReviewsView,
    CompanyReviewDetailView,
    MarkHelpfulView,
    SwipeFeedView,
    SwipeActionView,
    SwipeSavedView,
    SwipeAppliedView,
    SwipeLimitView,
)

urlpatterns = [
    path('',          JobListCreateView.as_view()),
    path('<int:pk>/', JobDetailView.as_view()),

    path('analytics/my-stats/',        SeekerStatsView.as_view()),
    path('analytics/recruiter-stats/', RecruiterStatsView.as_view()),

    path('reviews/',                            CompanyReviewListCreateView.as_view()),
    path('reviews/my/',                         MyReviewsView.as_view()),
    path('reviews/company/<str:company_name>/', CompanyReviewsByCompanyView.as_view()),
    path('reviews/<int:pk>/',                   CompanyReviewDetailView.as_view()),
    path('reviews/<int:pk>/helpful/',           MarkHelpfulView.as_view()),

    path('swipe/feed/',    SwipeFeedView.as_view()),
    path('swipe/action/',  SwipeActionView.as_view()),
    path('swipe/saved/',   SwipeSavedView.as_view()),
    path('swipe/applied/', SwipeAppliedView.as_view()),
    path('swipe/limit/',   SwipeLimitView.as_view()),
]