from django.db import models
from django.conf import settings

class Message(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_messages')
    encrypted_text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

class Signal(models.Model):
    call_id = models.CharField(max_length=200)
    type = models.CharField(max_length=50)
    data = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class CallInvite(models.Model):
    recipient_id = models.IntegerField()
    call_id = models.CharField(max_length=200)
    caller_id = models.IntegerField()
    is_video = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)