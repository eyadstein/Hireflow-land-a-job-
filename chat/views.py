from rest_framework import generics, permissions
from django.db.models import Q
from .models import Message
from .serializers import MessageSerializer

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
        serializer.save(sender=self.request.user)