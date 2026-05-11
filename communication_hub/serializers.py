from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Message, MessageThread, ThreadMessage, Notification, NotificationPreference,
    MessageTemplate, CommunicationLog
)

User = get_user_model()


class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.get_full_name', read_only=True)
    sender_email = serializers.EmailField(source='sender.email', read_only=True)
    recipient_name = serializers.CharField(source='recipient.get_full_name', read_only=True)
    recipient_email = serializers.EmailField(source='recipient.email', read_only=True)
    job_title = serializers.CharField(source='job.title', read_only=True)

    class Meta:
        model = Message
        fields = [
            'id', 'sender', 'sender_name', 'sender_email', 'recipient', 
            'recipient_name', 'recipient_email', 'subject', 'content', 
            'message_type', 'attachment_url', 'attachment_name', 'is_read', 
            'is_important', 'is_archived', 'parent_message', 'job', 'job_title',
            'created_at', 'updated_at', 'read_at'
        ]
        read_only_fields = ['id', 'sender', 'created_at', 'updated_at', 'read_at']


class MessageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = [
            'recipient', 'subject', 'content', 'message_type', 
            'attachment_url', 'attachment_name', 'is_important', 'parent_message', 'job'
        ]


class MessageThreadSerializer(serializers.ModelSerializer):
    participants_info = serializers.SerializerMethodField()
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    job_title = serializers.CharField(source='job.title', read_only=True)
    message_count = serializers.SerializerMethodField()

    class Meta:
        model = MessageThread
        fields = [
            'id', 'participants', 'participants_info', 'subject', 'job', 
            'job_title', 'is_active', 'created_by', 'created_by_name', 
            'last_message_at', 'created_at', 'message_count'
        ]
        read_only_fields = ['id', 'created_by', 'last_message_at', 'created_at']

    def get_participants_info(self, obj):
        return [
            {
                'id': user.id,
                'name': user.get_full_name(),
                'email': user.email
            }
            for user in obj.participants.all()
        ]
    
    def get_message_count(self, obj):
        return obj.thread_messages.count()


class ThreadMessageSerializer(serializers.ModelSerializer):
    message_details = MessageSerializer(source='message', read_only=True)

    class Meta:
        model = ThreadMessage
        fields = [
            'id', 'thread', 'message', 'message_details', 'is_deleted', 
            'deleted_by', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class NotificationSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'user_name', 'user_email', 'title', 'message', 
            'notification_type', 'is_read', 'is_email_sent', 'is_push_sent', 
            'action_url', 'action_text', 'metadata', 'expires_at', 
            'created_at', 'read_at'
        ]
        read_only_fields = [
            'id', 'user', 'is_email_sent', 'is_push_sent', 'created_at', 'read_at'
        ]


class NotificationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            'user', 'title', 'message', 'notification_type', 'action_url', 
            'action_text', 'metadata', 'expires_at'
        ]


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = NotificationPreference
        fields = [
            'id', 'user', 'user_email', 'email_notifications', 'push_notifications', 
            'message_notifications', 'job_match_notifications', 'application_notifications', 
            'interview_notifications', 'profile_view_notifications', 'system_notifications', 
            'daily_digest', 'weekly_digest', 'quiet_hours_start', 'quiet_hours_end', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class MessageTemplateSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = MessageTemplate
        fields = [
            'id', 'name', 'subject', 'content', 'variables', 'is_active', 
            'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']


class CommunicationLogSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = CommunicationLog
        fields = [
            'id', 'user', 'user_name', 'user_email', 'action_type', 'message', 
            'notification', 'ip_address', 'user_agent', 'metadata', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']


class MessageThreadCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageThread
        fields = ['participants', 'subject', 'job', 'is_active']


class BulkMessageSerializer(serializers.Serializer):
    recipients = serializers.ListField(child=serializers.IntegerField())
    subject = serializers.CharField(max_length=255)
    content = serializers.CharField()
    message_type = serializers.ChoiceField(choices=Message.MESSAGE_TYPES, default='text')
    is_important = serializers.BooleanField(default=False)
    job_id = serializers.IntegerField(required=False)


class NotificationBulkCreateSerializer(serializers.Serializer):
    users = serializers.ListField(child=serializers.IntegerField())
    title = serializers.CharField(max_length=255)
    message = serializers.CharField()
    notification_type = serializers.ChoiceField(choices=Notification.NOTIFICATION_TYPES)
    action_url = serializers.URLField(required=False)
    action_text = serializers.CharField(max_length=100, required=False)
    metadata = serializers.JSONField(default=dict)
