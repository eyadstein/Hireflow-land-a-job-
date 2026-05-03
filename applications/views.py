from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Application
from .serializers import (
    ApplicationSerializer,
    MoveCardSerializer,
    KanbanColumnSerializer,
)


# ─────────────────────────────────────────────
#  Helper — always scope to the current user
# ─────────────────────────────────────────────
def user_applications(request):
    return Application.objects.filter(user=request.user)


# ─────────────────────────────────────────────
#  CRUD
# ─────────────────────────────────────────────
class ApplicationListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/applications/        → list all cards for current user
    POST /api/applications/        → create a new card
    """
    serializer_class   = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return user_applications(self.request)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ApplicationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/applications/<id>/  → retrieve
    PATCH  /api/applications/<id>/  → update (notes, applied_date, etc.)
    DELETE /api/applications/<id>/  → delete
    """
    serializer_class   = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return user_applications(self.request)


# ─────────────────────────────────────────────
#  Kanban Board
# ─────────────────────────────────────────────
class KanbanBoardView(APIView):
    """
    GET /api/applications/board/
    Returns all applications grouped by status column.

    Response shape:
    {
      "board": [
        { "status": "saved",     "label": "Saved",     "cards": [...] },
        { "status": "applied",   "label": "Applied",   "cards": [...] },
        { "status": "interview", "label": "Interview",  "cards": [...] },
        { "status": "offer",     "label": "Offer",     "cards": [...] },
        { "status": "rejected",  "label": "Rejected",  "cards": [...] }
      ],
      "total": 12
    }
    """
    permission_classes = [permissions.IsAuthenticated]

    COLUMNS = Application.KANBAN_STATUS_CHOICES  # ordered list of (value, label)

    def get(self, request):
        all_apps = user_applications(request).select_related('job')

        board = []
        for col_status, col_label in self.COLUMNS:
            cards = all_apps.filter(status=col_status)
            board.append({
                'status': col_status,
                'label':  col_label,
                'cards':  ApplicationSerializer(cards, many=True).data,
            })

        return Response({
            'board': board,
            'total': all_apps.count(),
        })


# ─────────────────────────────────────────────
#  Move Card
# ─────────────────────────────────────────────
class MoveCardView(APIView):
    """
    PATCH /api/applications/<id>/move/
    Body: { "status": "interview", "order": 0 }

    Moves a card to a new Kanban column.
    """
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        application = get_object_or_404(
            Application, pk=pk, user=request.user
        )

        serializer = MoveCardSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

        application.status = serializer.validated_data['status']
        if 'order' in serializer.validated_data:
            application.order = serializer.validated_data['order']
        application.save(update_fields=['status', 'order', 'updated_at'])

        return Response(
            ApplicationSerializer(application).data,
            status=status.HTTP_200_OK
        )