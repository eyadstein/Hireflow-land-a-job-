from django.urls import path
from .views import (
    ApplicationListCreateView,
    ApplicationDetailView,
    KanbanBoardView,
    MoveCardView,
)

urlpatterns = [
    # ── CRUD ──────────────────────────────────────────────────────
    path('',           ApplicationListCreateView.as_view()),   # GET list / POST create
    path('<int:pk>/',  ApplicationDetailView.as_view()),       # GET / PATCH / DELETE
    # ── Kanban ────────────────────────────────────────────────────
    path('board/',            KanbanBoardView.as_view()),      # GET full board
    path('<int:pk>/move/',    MoveCardView.as_view()),         # PATCH move card
]