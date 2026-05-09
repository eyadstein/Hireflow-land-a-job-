from django.urls import path
from .views import ApplicationListCreateView, ApplicationDetailView

urlpatterns = [
    path('', ApplicationListCreateView.as_view()),
    path('<int:pk>/', ApplicationDetailView.as_view()),
]
