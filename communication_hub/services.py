from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.db.models import Q, Count
from django.contrib.auth import get_user_model
from .models import (
    Message, MessageThread, ThreadMessage, Notification, NotificationPreference,
    MessageTemplate, CommunicationLog
)
import logging

User = get_user_model()

logger = logging.getLogger(__name__)


class CommunicationService:
    
    def __init__(self):
        self.default_from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@hireflow.com')
    
    def send_message(self, sender, recipient, subject, content, message_type='text', 
                    attachment_url=None, attachment_name=None, is_important=False, 
                    parent_message=None, job=None):
        message = Message.objects.create(
            sender=sender,
            recipient=recipient,
            subject=subject,
            content=content,
            message_type=message_type,
            attachment_url=attachment_url or '',
            attachment_name=attachment_name or '',
            is_important=is_important,
            parent_message=parent_message,
            job=job
        )
        
        # Log the action
        self._log_communication_action(sender, 'sent', message=message)
        self._log_communication_action(recipient, 'received', message=message)
        
        # Send notification to recipient
        self._send_message_notification(message)
        
        return message
    
    def send_bulk_messages(self, sender, recipients, subject, content, message_type='text',
                          is_important=False, job=None):
        messages = []
        for recipient_id in recipients:
            try:
                recipient = User.objects.get(id=recipient_id)
                message = self.send_message(
                    sender=sender,
                    recipient=recipient,
                    subject=subject,
                    content=content,
                    message_type=message_type,
                    is_important=is_important,
                    job=job
                )
                messages.append(message)
            except User.DoesNotExist:
                continue
        
        return messages
    
    def create_message_thread(self, creator, participants, subject, job=None, initial_message=None):
        thread = MessageThread.objects.create(
            subject=subject,
            job=job,
            created_by=creator
        )
        
        thread.participants.set(participants)
        
        if initial_message:
            message = self.send_message(
                sender=creator,
                recipient=participants[0] if participants else creator,
                subject=subject,
                content=initial_message,
                job=job
            )
            
            ThreadMessage.objects.create(
                thread=thread,
                message=message
            )
        
        return thread
    
    def add_message_to_thread(self, thread, sender, content, message_type='text'):
        # Create message for each participant (except sender)
        participants = thread.participants.exclude(id=sender.id)
        
        for recipient in participants:
            message = self.send_message(
                sender=sender,
                recipient=recipient,
                subject=thread.subject,
                content=content,
                message_type=message_type,
                job=thread.job
            )
            
            ThreadMessage.objects.create(
                thread=thread,
                message=message
            )
        
        return thread
    
    def mark_message_as_read(self, message, user):
        if message.recipient == user and not message.is_read:
            message.is_read = True
            message.read_at = timezone.now()
            message.save()
            
            self._log_communication_action(user, 'read', message=message)
            return True
        return False
    
    def create_notification(self, user, title, message, notification_type, 
                          action_url=None, action_text=None, metadata=None, expires_at=None):
        notification = Notification.objects.create(
            user=user,
            title=title,
            message=message,
            notification_type=notification_type,
            action_url=action_url or '',
            action_text=action_text or '',
            metadata=metadata or {},
            expires_at=expires_at
        )
        
        # Send email/push notifications based on user preferences
        self._send_notification_channels(notification)
        
        return notification
    
    def create_bulk_notifications(self, users, title, message, notification_type,
                                 action_url=None, action_text=None, metadata=None):
        notifications = []
        for user in users:
            notification = self.create_notification(
                user=user,
                title=title,
                message=message,
                notification_type=notification_type,
                action_url=action_url,
                action_text=action_text,
                metadata=metadata
            )
            notifications.append(notification)
        
        return notifications
    
    def mark_notification_as_read(self, notification, user):
        if notification.user == user and not notification.is_read:
            notification.is_read = True
            notification.read_at = timezone.now()
            notification.save()
            
            self._log_communication_action(user, 'read', notification=notification)
            return True
        return False
    
    def get_unread_notifications(self, user, notification_type=None):
        queryset = Notification.objects.filter(user=user, is_read=False)
        
        if notification_type:
            queryset = queryset.filter(notification_type=notification_type)
        
        return queryset.order_by('-created_at')
    
    def get_user_message_stats(self, user):
        return {
            'total_sent': Message.objects.filter(sender=user).count(),
            'total_received': Message.objects.filter(recipient=user).count(),
            'unread_count': Message.objects.filter(recipient=user, is_read=False).count(),
            'important_count': Message.objects.filter(recipient=user, is_important=True, is_read=False).count(),
            'archived_count': Message.objects.filter(recipient=user, is_archived=True).count(),
        }
    
    def get_user_notification_stats(self, user):
        return {
            'total_notifications': Notification.objects.filter(user=user).count(),
            'unread_count': Notification.objects.filter(user=user, is_read=False).count(),
            'unread_by_type': dict(
                Notification.objects.filter(user=user, is_read=False)
                .values('notification_type')
                .annotate(count=Count('id'))
                .values_list('notification_type', 'count')
            )
        }
    
    def apply_message_template(self, template_name, variables, sender, recipient, job=None):
        try:
            template = MessageTemplate.objects.get(name=template_name, is_active=True)
            
            # Replace variables in subject and content
            subject = template.subject
            content = template.content
            
            for key, value in variables.items():
                subject = subject.replace(f'{{{key}}}', str(value))
                content = content.replace(f'{{{key}}}', str(value))
            
            return self.send_message(
                sender=sender,
                recipient=recipient,
                subject=subject,
                content=content,
                job=job
            )
        
        except MessageTemplate.DoesNotExist:
            logger.error(f"Message template '{template_name}' not found")
            return None
    
    def _send_message_notification(self, message):
        try:
            preferences = NotificationPreference.objects.get(user=message.recipient)
            
            if preferences.message_notifications:
                self.create_notification(
                    user=message.recipient,
                    title=f"New message from {message.sender.get_full_name()}",
                    content=message.content[:200] + "..." if len(message.content) > 200 else message.content,
                    notification_type='message_received',
                    action_url=f"/messages/{message.id}",
                    action_text="View Message"
                )
        except NotificationPreference.DoesNotExist:
            # Create default preferences and retry
            NotificationPreference.objects.create(user=message.recipient)
            self._send_message_notification(message)
    
    def _send_notification_channels(self, notification):
        try:
            preferences = NotificationPreference.objects.get(user=notification.user)
            
            # Send email notification
            if (preferences.email_notifications and 
                not notification.is_email_sent and
                self._is_within_quiet_hours(preferences)):
                
                self._send_email_notification(notification)
                notification.is_email_sent = True
                notification.save()
            
            # Send push notification (implementation depends on your push service)
            if (preferences.push_notifications and 
                not notification.is_push_sent and
                self._is_within_quiet_hours(preferences)):
                
                self._send_push_notification(notification)
                notification.is_push_sent = True
                notification.save()
                
        except NotificationPreference.DoesNotExist:
            # Create default preferences and retry
            NotificationPreference.objects.create(user=notification.user)
            self._send_notification_channels(notification)
    
    def _send_email_notification(self, notification):
        try:
            send_mail(
                subject=notification.title,
                message=notification.message,
                from_email=self.default_from_email,
                recipient_list=[notification.user.email],
                html_message=render_to_string('emails/notification.html', {
                    'notification': notification,
                    'user': notification.user
                })
            )
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")
    
    def _send_push_notification(self, notification):
        # Implement push notification logic here
        # This would integrate with services like Firebase Cloud Messaging
        pass
    
    def _is_within_quiet_hours(self, preferences):
        if not preferences.quiet_hours_start or not preferences.quiet_hours_end:
            return True
        
        current_time = timezone.now().time()
        start_time = preferences.quiet_hours_start
        end_time = preferences.quiet_hours_end
        
        if start_time <= end_time:
            return not (start_time <= current_time <= end_time)
        else:
            # Handle overnight quiet hours
            return not (current_time >= start_time or current_time <= end_time)
    
    def _log_communication_action(self, user, action_type, message=None, notification=None, 
                                 ip_address=None, user_agent=None, metadata=None):
        CommunicationLog.objects.create(
            user=user,
            action_type=action_type,
            message=message,
            notification=notification,
            ip_address=ip_address,
            user_agent=user_agent or '',
            metadata=metadata or {}
        )


class MessageSearchService:
    
    @staticmethod
    def search_messages(user, query, message_type=None, is_read=None, is_important=None,
                      start_date=None, end_date=None, page=1, page_size=20):
        queryset = Message.objects.filter(
            Q(sender=user) | Q(recipient=user)
        ).select_related('sender', 'recipient', 'job')
        
        if query:
            queryset = queryset.filter(
                Q(subject__icontains=query) |
                Q(content__icontains=query)
            )
        
        if message_type:
            queryset = queryset.filter(message_type=message_type)
        
        if is_read is not None:
            queryset = queryset.filter(is_read=is_read)
        
        if is_important is not None:
            queryset = queryset.filter(is_important=is_important)
        
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)
        
        # Pagination
        offset = (page - 1) * page_size
        return queryset[offset:offset + page_size]
    
    @staticmethod
    def search_threads(user, query, job_id=None, is_active=None, page=1, page_size=20):
        queryset = MessageThread.objects.filter(
            participants=user
        ).select_related('job', 'created_by').prefetch_related('participants')
        
        if query:
            queryset = queryset.filter(subject__icontains=query)
        
        if job_id:
            queryset = queryset.filter(job_id=job_id)
        
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        
        # Pagination
        offset = (page - 1) * page_size
        return queryset[offset:offset + page_size]
