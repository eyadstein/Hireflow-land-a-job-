from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import generics, permissions
from rest_framework.exceptions import NotFound, PermissionDenied

from .models import Message
from .serializers import MessageSerializer

User = get_user_model()


class MessageListView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_other_user(self):
        user_id = self.kwargs.get("user_id")

        try:
            other_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise NotFound("User not found.")

        if other_user.id == self.request.user.id:
            raise PermissionDenied("You cannot message yourself.")

        return other_user

    def get_queryset(self):
        other_user = self.get_other_user()
        user = self.request.user

        return Message.objects.filter(
            Q(sender=user, recipient=other_user)
            | Q(sender=other_user, recipient=user)
        ).order_by("timestamp")

    def perform_create(self, serializer):
        other_user = self.get_other_user()

        serializer.save(
            sender=self.request.user,
            recipient=other_user,
        )