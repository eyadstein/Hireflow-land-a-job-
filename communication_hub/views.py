from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count
from .models import (
    Message, MessageThread, ThreadMessage, Notification, NotificationPreference,
    MessageTemplate, CommunicationLog
)
from .serializers import (
    MessageSerializer, MessageCreateSerializer, MessageThreadSerializer,
    MessageThreadCreateSerializer, ThreadMessageSerializer, NotificationSerializer,
    NotificationCreateSerializer, NotificationPreferenceSerializer,
    MessageTemplateSerializer, CommunicationLogSerializer,
    BulkMessageSerializer, NotificationBulkCreateSerializer
)
from .services import CommunicationService, MessageSearchService


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Message.objects.filter(
            Q(sender=self.request.user) | Q(recipient=self.request.user)
        ).select_related('sender', 'recipient', 'job')
        
        # Filters
        message_type = self.request.query_params.get('message_type')
        if message_type:
            queryset = queryset.filter(message_type=message_type)
        
        is_read = self.request.query_params.get('is_read')
        if is_read is not None:
            queryset = queryset.filter(is_read=is_read.lower() == 'true')
        
        is_important = self.request.query_params.get('is_important')
        if is_important is not None:
            queryset = queryset.filter(is_important=is_important.lower() == 'true')
        
        return queryset.order_by('-created_at')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return MessageCreateSerializer
        return MessageSerializer
    
    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        message = self.get_object()
        service = CommunicationService()
        
        if service.mark_message_as_read(message, request.user):
            return Response({'status': 'marked as read'})
        
        return Response(
            {'error': 'Cannot mark message as read'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=False, methods=['get'])
    def inbox(self, request):
        messages = self.get_queryset().filter(recipient=request.user, is_read=False)
        
        page = self.paginate_queryset(messages)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def sent(self, request):
        messages = self.get_queryset().filter(sender=request.user)
        
        page = self.paginate_queryset(messages)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def bulk_send(self, request):
        serializer = BulkMessageSerializer(data=request.data)
        
        if serializer.is_valid():
            service = CommunicationService()
            messages = service.send_bulk_messages(
                sender=request.user,
                recipients=serializer.validated_data['recipients'],
                subject=serializer.validated_data['subject'],
                content=serializer.validated_data['content'],
                message_type=serializer.validated_data.get('message_type', 'text'),
                is_important=serializer.validated_data.get('is_important', False),
                job_id=serializer.validated_data.get('job_id')
            )
            
            return Response({
                'message': f'Sent {len(messages)} messages',
                'sent_count': len(messages)
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        query = request.query_params.get('q', '')
        if not query:
            return Response({'error': 'Search query is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        search_service = MessageSearchService()
        messages = search_service.search_messages(
            user=request.user,
            query=query,
            message_type=request.query_params.get('message_type'),
            is_read=request.query_params.get('is_read'),
            is_important=request.query_params.get('is_important'),
            start_date=request.query_params.get('start_date'),
            end_date=request.query_params.get('end_date'),
            page=int(request.query_params.get('page', 1)),
            page_size=int(request.query_params.get('page_size', 20))
        )
        
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)


class MessageThreadViewSet(viewsets.ModelViewSet):
    serializer_class = MessageThreadSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return MessageThread.objects.filter(
            participants=self.request.user
        ).select_related('job', 'created_by').prefetch_related('participants')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return MessageThreadCreateSerializer
        return MessageThreadSerializer
    
    def perform_create(self, serializer):
        thread = serializer.save(created_by=self.request.user)
        thread.participants.add(self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_message(self, request, pk=None):
        thread = self.get_object()
        service = CommunicationService()
        
        updated_thread = service.add_message_to_thread(
            thread=thread,
            sender=request.user,
            content=request.data.get('content', ''),
            message_type=request.data.get('message_type', 'text')
        )
        
        return Response(MessageThreadSerializer(updated_thread).data)
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        thread = self.get_object()
        thread_messages = ThreadMessage.objects.filter(
            thread=thread
        ).select_related('message__sender', 'message__recipient')
        
        serializer = ThreadMessageSerializer(thread_messages, many=True)
        return Response(serializer.data)


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Notification.objects.filter(user=self.request.user)
        
        notification_type = self.request.query_params.get('type')
        if notification_type:
            queryset = queryset.filter(notification_type=notification_type)
        
        is_read = self.request.query_params.get('is_read')
        if is_read is not None:
            queryset = queryset.filter(is_read=is_read.lower() == 'true')
        
        return queryset.order_by('-created_at')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return NotificationCreateSerializer
        return NotificationSerializer
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        service = CommunicationService()
        
        if service.mark_notification_as_read(notification, request.user):
            return Response({'status': 'marked as read'})
        
        return Response(
            {'error': 'Cannot mark notification as read'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        service = CommunicationService()
        unread_notifications = service.get_unread_notifications(request.user)
        
        count = 0
        for notification in unread_notifications:
            if service.mark_notification_as_read(notification, request.user):
                count += 1
        
        return Response({'marked_read_count': count})
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        service = CommunicationService()
        unread_count = service.get_unread_notifications(request.user).count()
        
        return Response({'unread_count': unread_count})
    
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        serializer = NotificationBulkCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            service = CommunicationService()
            
            # Get user objects
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            users = User.objects.filter(id__in=serializer.validated_data['users'])
            
            notifications = service.create_bulk_notifications(
                users=users,
                title=serializer.validated_data['title'],
                message=serializer.validated_data['message'],
                notification_type=serializer.validated_data['notification_type'],
                action_url=serializer.validated_data.get('action_url'),
                action_text=serializer.validated_data.get('action_text'),
                metadata=serializer.validated_data.get('metadata')
            )
            
            return Response({
                'message': f'Created {len(notifications)} notifications',
                'created_count': len(notifications)
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NotificationPreferenceViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return NotificationPreference.objects.filter(user=self.request.user)
    
    def get_object(self):
        preference, created = NotificationPreference.objects.get_or_create(
            user=self.request.user
        )
        return preference


class MessageTemplateViewSet(viewsets.ModelViewSet):
    queryset = MessageTemplate.objects.all()
    serializer_class = MessageTemplateSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['post'])
    def send(self, request, pk=None):
        template = self.get_object()
        recipient_id = request.data.get('recipient_id')
        variables = request.data.get('variables', {})
        
        if not recipient_id:
            return Response(
                {'error': 'recipient_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            recipient = User.objects.get(id=recipient_id)
            
            service = CommunicationService()
            message = service.apply_message_template(
                template_name=template.name,
                variables=variables,
                sender=request.user,
                recipient=recipient
            )
            
            if message:
                return Response(MessageSerializer(message).data)
            
            return Response(
                {'error': 'Failed to send message'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        except User.DoesNotExist:
            return Response(
                {'error': 'Recipient not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class CommunicationLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CommunicationLogSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = CommunicationLog.objects.filter(user=self.request.user)
        
        action_type = self.request.query_params.get('action_type')
        if action_type:
            queryset = queryset.filter(action_type=action_type)
        
        return queryset.order_by('-created_at')
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        service = CommunicationService()
        message_stats = service.get_user_message_stats(request.user)
        notification_stats = service.get_user_notification_stats(request.user)
        
        return Response({
            'messages': message_stats,
            'notifications': notification_stats
        })
