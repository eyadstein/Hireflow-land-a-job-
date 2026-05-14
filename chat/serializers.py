from rest_framework import serializers

from .models import Message


class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source="sender.username", read_only=True)
    recipient_name = serializers.CharField(source="recipient.username", read_only=True)

    class Meta:
        model = Message
        fields = [
            "id",
            "sender",
            "recipient",
            "sender_name",
            "recipient_name",
            "encrypted_text",
            "timestamp",
        ]
        read_only_fields = [
            "id",
            "sender",
            "recipient",
            "sender_name",
            "recipient_name",
            "timestamp",
        ]