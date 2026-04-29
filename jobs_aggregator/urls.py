from django.urls import path
from .views import JobAggregatorView, CountriesView

urlpatterns = [
    path('search/', JobAggregatorView.as_view()),
    path('countries/', CountriesView.as_view()),
]