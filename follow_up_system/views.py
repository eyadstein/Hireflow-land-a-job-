from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import timedelta

from .models import (
    FollowUpTemplate, FollowUpRule, FollowUpSchedule, FollowUpHistory,
    FollowUpTrigger, FollowUpAnalytics, FollowUpBlacklist
)
from .serializers import (
    FollowUpTemplateSerializer, FollowUpRuleSerializer, FollowUpScheduleSerializer,
    FollowUpHistorySerializer, FollowUpTriggerSerializer, FollowUpAnalyticsSerializer,
    FollowUpBlacklistSerializer, FollowUpScheduleCreateSerializer,
    FollowUpTriggerCreateSerializer, BulkFollowUpScheduleSerializer,
    FollowUpTestSerializer
)
from .services import FollowUpService, FollowUpAutomationService


class FollowUpTemplateViewSet(viewsets.ModelViewSet):
    serializer_class = FollowUpTemplateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = FollowUpTemplate.objects.all()
        
        trigger_type = self.request.query_params.get('trigger_type')
        if trigger_type:
            queryset = queryset.filter(trigger_type=trigger_type)
        
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset.order_by('priority', 'name')
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def test(self, request, pk=None):
        template = self.get_object()
        serializer = FollowUpTestSerializer(data=request.data)
        
        if serializer.is_valid():
            service = FollowUpService()
            result = service.test_template(
                template_id=template.id,
                candidate_id=serializer.validated_data['candidate_id'],
                variables=serializer.validated_data.get('variables', {})
            )
            
            if result['success']:
                return Response(result)
            
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def send_now(self, request, pk=None):
        template = self.get_object()
        candidate_id = request.data.get('candidate_id')
        variables = request.data.get('variables', {})
        
        if not candidate_id:
            return Response(
                {'error': 'candidate_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            candidate = User.objects.get(id=candidate_id)
            
            service = FollowUpService()
            
            # Create trigger
            trigger = service.create_trigger(
                event_type='custom',
                candidate=candidate,
                event_data=variables
            )
            
            return Response({
                'message': 'Follow-up triggered successfully',
                'trigger_id': trigger.id
            })
            
        except User.DoesNotExist:
            return Response(
                {'error': 'Candidate not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class FollowUpRuleViewSet(viewsets.ModelViewSet):
    serializer_class = FollowUpRuleSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = FollowUpRule.objects.prefetch_related('templates')
        
        condition_type = self.request.query_params.get('condition_type')
        if condition_type:
            queryset = queryset.filter(condition_type=condition_type)
        
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset.order_by('name')
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def test_rules(self, request, pk=None):
        rule = self.get_object()
        candidate_id = request.data.get('candidate_id')
        
        if not candidate_id:
            return Response(
                {'error': 'candidate_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            candidate = User.objects.get(id=candidate_id)
            
            service = FollowUpService()
            
            # Create test trigger
            trigger = FollowUpTrigger.objects.create(
                event_type='custom',
                candidate=candidate
            )
            
            # Test rule matching
            matches = service._rule_matches_trigger(rule, trigger)
            
            trigger.delete()
            
            return Response({
                'rule_matches': matches,
                'rule_name': rule.name
            })
            
        except User.DoesNotExist:
            return Response(
                {'error': 'Candidate not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class FollowUpScheduleViewSet(viewsets.ModelViewSet):
    serializer_class = FollowUpScheduleSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = FollowUpSchedule.objects.select_related(
            'candidate', 'template', 'rule', 'job'
        )
        
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        candidate_id = self.request.query_params.get('candidate_id')
        if candidate_id:
            queryset = queryset.filter(candidate_id=candidate_id)
        
        template_id = self.request.query_params.get('template_id')
        if template_id:
            queryset = queryset.filter(template_id=template_id)
        
        return queryset.order_by('-scheduled_at')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return FollowUpScheduleCreateSerializer
        return FollowUpScheduleSerializer
    
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        serializer = BulkFollowUpScheduleSerializer(data=request.data)
        
        if serializer.is_valid():
            service = FollowUpService()
            
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            schedules = []
            for candidate_id in serializer.validated_data['candidates']:
                try:
                    candidate = User.objects.get(id=candidate_id)
                    template = FollowUpTemplate.objects.get(
                        id=serializer.validated_data['template_id']
                    )
                    
                    schedule = FollowUpSchedule.objects.create(
                        candidate=candidate,
                        template=template,
                        scheduled_at=serializer.validated_data['scheduled_at'],
                        recipient_email=candidate.email,
                        subject=serializer.validated_data.get('subject_override', template.subject),
                        content=serializer.validated_data.get('content_override', template.content),
                        variables_used={}
                    )
                    
                    schedules.append(schedule)
                    
                except (User.DoesNotExist, FollowUpTemplate.DoesNotExist):
                    continue
            
            return Response({
                'message': f'Created {len(schedules)} schedules',
                'created_count': len(schedules)
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def send_pending(self, request):
        service = FollowUpService()
        results = service.send_scheduled_follow_ups()
        
        return Response(results)
    
    @action(detail=True, methods=['post'])
    def mark_opened(self, request, pk=None):
        schedule = self.get_object()
        service = FollowUpService()
        
        if service.track_email_open(schedule.id):
            return Response({'status': 'marked as opened'})
        
        return Response(
            {'error': 'Failed to track email open'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=True, methods=['post'])
    def mark_clicked(self, request, pk=None):
        schedule = self.get_object()
        service = FollowUpService()
        
        if service.track_email_click(schedule.id):
            return Response({'status': 'marked as clicked'})
        
        return Response(
            {'error': 'Failed to track email click'},
            status=status.HTTP_400_BAD_REQUEST
        )


class FollowUpHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = FollowUpHistorySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = FollowUpHistory.objects.select_related(
            'schedule', 'schedule__candidate', 'schedule__template'
        )
        
        schedule_id = self.request.query_params.get('schedule_id')
        if schedule_id:
            queryset = queryset.filter(schedule_id=schedule_id)
        
        action_type = self.request.query_params.get('action_type')
        if action_type:
            queryset = queryset.filter(action_type=action_type)
        
        return queryset.order_by('-action_date')


class FollowUpTriggerViewSet(viewsets.ModelViewSet):
    serializer_class = FollowUpTriggerSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = FollowUpTrigger.objects.select_related(
            'candidate', 'job', 'application'
        )
        
        event_type = self.request.query_params.get('event_type')
        if event_type:
            queryset = queryset.filter(event_type=event_type)
        
        processed = self.request.query_params.get('processed')
        if processed is not None:
            queryset = queryset.filter(processed=processed.lower() == 'true')
        
        return queryset.order_by('-created_at')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return FollowUpTriggerCreateSerializer
        return FollowUpTriggerSerializer
    
    @action(detail=True, methods=['post'])
    def reprocess(self, request, pk=None):
        trigger = self.get_object()
        
        if trigger.processed:
            trigger.processed = False
            trigger.processed_at = None
            trigger.save()
            
            service = FollowUpService()
            schedules_created, errors = service.process_trigger(trigger)
            
            return Response({
                'message': 'Trigger reprocessed',
                'schedules_created': schedules_created,
                'errors': errors
            })
        
        return Response(
            {'error': 'Trigger has not been processed yet'},
            status=status.HTTP_400_BAD_REQUEST
        )


class FollowUpAnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = FollowUpAnalyticsSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = FollowUpAnalytics.objects.select_related('template', 'rule')
        
        start_date = self.request.query_params.get('start_date')
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        
        end_date = self.request.query_params.get('end_date')
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        template_id = self.request.query_params.get('template_id')
        if template_id:
            queryset = queryset.filter(template_id=template_id)
        
        return queryset.order_by('-date')
    
    @action(detail=False, methods=['post'])
    def update_analytics(self, request):
        date_str = request.data.get('date')
        
        if date_str:
            try:
                date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {'error': 'Invalid date format. Use YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            date = timezone.now().date()
        
        service = FollowUpService()
        service.update_analytics(date)
        
        return Response({
            'message': f'Analytics updated for {date}',
            'date': date
        })
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        queryset = self.get_queryset()
        
        # Calculate summary statistics
        total_scheduled = queryset.aggregate(
            total=Count('total_scheduled')
        )['total'] or 0
        
        total_sent = queryset.aggregate(
            total=Count('total_sent')
        )['total'] or 0
        
        avg_open_rate = queryset.aggregate(
            avg=Avg('open_rate')
        )['avg'] or 0
        
        avg_click_rate = queryset.aggregate(
            avg=Avg('click_rate')
        )['avg'] or 0
        
        avg_reply_rate = queryset.aggregate(
            avg=Avg('reply_rate')
        )['avg'] or 0
        
        return Response({
            'total_scheduled': total_scheduled,
            'total_sent': total_sent,
            'average_open_rate': round(avg_open_rate, 2),
            'average_click_rate': round(avg_click_rate, 2),
            'average_reply_rate': round(avg_reply_rate, 2),
        })


class FollowUpBlacklistViewSet(viewsets.ModelViewSet):
    serializer_class = FollowUpBlacklistSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = FollowUpBlacklist.objects.select_related(
            'candidate', 'template', 'rule', 'created_by'
        )
        
        candidate_id = self.request.query_params.get('candidate_id')
        if candidate_id:
            queryset = queryset.filter(candidate_id=candidate_id)
        
        is_permanent = self.request.query_params.get('is_permanent')
        if is_permanent is not None:
            queryset = queryset.filter(is_permanent=is_permanent.lower() == 'true')
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
