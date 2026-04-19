from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
import json
from .models import Message, Signal, CallInvite
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

class SignalView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, call_id):
        signal_type = request.query_params.get('type')
        signals = Signal.objects.filter(call_id=call_id, type=signal_type)
        return Response([{"data": json.loads(s.data)} for s in signals])

    def post(self, request, call_id):
        Signal.objects.create(
            call_id=call_id,
            type=request.data.get('type'),
            data=json.dumps(request.data.get('data')),
        )
        return Response({"ok": True})

    def delete(self, request, call_id):
        Signal.objects.filter(call_id=call_id).delete()
        return Response({"ok": True})

class CallInviteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, user_id):
        invite = CallInvite.objects.filter(recipient_id=user_id).last()
        if not invite:
            return Response(None)
        return Response({
            "callId": invite.call_id,
            "callerId": invite.caller_id,
            "isVideo": invite.is_video,
        })

    def post(self, request, user_id):
        CallInvite.objects.filter(recipient_id=user_id).delete()
        CallInvite.objects.create(
            recipient_id=user_id,
            call_id=request.data.get('callId'),
            caller_id=request.data.get('callerId'),
            is_video=request.data.get('isVideo', True),
        )
        return Response({"ok": True})

    def delete(self, request, user_id):
        CallInvite.objects.filter(recipient_id=user_id).delete()
        return Response({"ok": True})