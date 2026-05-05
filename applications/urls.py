from django.urls import path
from .views import (
    ApplicationListCreateView,
    ApplicationDetailView,
    KanbanBoardView,
    MoveCardView,
    QuickApplyView,
    QuickApplyDashboardView,
)

urlpatterns = [
    path('',           ApplicationListCreateView.as_view()),
    path('<int:pk>/',  ApplicationDetailView.as_view()),

    path('board/',           KanbanBoardView.as_view()),
    path('<int:pk>/move/',   MoveCardView.as_view()),

    path('quick-apply/',          QuickApplyView.as_view()),
    path('quick-apply/history/',  QuickApplyDashboardView.as_view()),
]