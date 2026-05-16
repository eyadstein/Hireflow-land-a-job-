from rest_framework import generics, permissions
from django.db.models import Q

from applications.views import User
from .models import Message
from .serializers import MessageSerializer
from rest_framework.exceptions import NotFound

class MessageListView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        other = self.kwargs['user_id']
        user = self.request.user
        return Message.objects.filter(
            Q(sender=user, recipient_id=other) |
            Q(sender_id=other, recipient=user)
        ).order_by('timestamp')

    def perform_create(self, serializer):
        from django.contrib.auth import get_user_model
        User = get_user_model()

        try:
            recipient = User.objects.get(id=self.kwargs['user_id'])
        except User.DoesNotExist:
            raise NotFound("Recipient not found.")

        serializer.save(sender=self.request.user, recipient=recipient)