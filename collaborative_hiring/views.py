from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta

from .models import (
    HiringTeam, HiringDecision, InterviewSchedule, CandidateFeedback,
    HiringWorkflow, JobWorkflow, TeamCollaboration, InterviewKit,
    JobInterviewKit, HiringAnalytics, TeamNotification
)
from .serializers import (
    HiringTeamSerializer, HiringDecisionSerializer, InterviewScheduleSerializer,
    CandidateFeedbackSerializer, HiringWorkflowSerializer, JobWorkflowSerializer,
    TeamCollaborationSerializer, InterviewKitSerializer, JobInterviewKitSerializer,
    HiringAnalyticsSerializer, TeamNotificationSerializer,
    HiringTeamCreateSerializer, HiringDecisionCreateSerializer, InterviewScheduleCreateSerializer,
    CandidateFeedbackCreateSerializer, HiringWorkflowCreateSerializer, JobWorkflowCreateSerializer,
    TeamCollaborationCreateSerializer, InterviewKitCreateSerializer, JobInterviewKitCreateSerializer,
    HiringAnalyticsCreateSerializer, TeamNotificationCreateSerializer,
    BulkInterviewScheduleSerializer, BulkFeedbackRequestSerializer, InterviewScheduleUpdateSerializer
)
from .services import CollaborativeHiringService, HiringAnalyticsService


class HiringTeamViewSet(viewsets.ModelViewSet):
    queryset = HiringTeam.objects.all()
    serializer_class = HiringTeamSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']
    filterset_fields = ['team_type', 'is_active', 'job']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return HiringTeamCreateSerializer
        return super().get_serializer_class()
    
    def perform_create(self, serializer):
        service = CollaborativeHiringService()
        team = service.create_hiring_team(
            name=serializer.validated_data['name'],
            team_type=serializer.validated_data['team_type'],
            job_id=serializer.validated_data['job'].id,
            member_ids=serializer.validated_data.get('members', []),
            description=serializer.validated_data.get('description', ''),
            user=self.request.user
        )
        
        if team:
            return Response(
                HiringTeamSerializer(team).data,
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {'error': 'Failed to create hiring team'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def add_members(self, request, pk=None):
        """Add members to hiring team"""
        team = self.get_object()
        member_ids = request.data.get('member_ids', [])
        
        try:
            team.members.add(*member_ids)
            return Response({'message': 'Members added successfully'})
        except Exception as e:
            return Response(
                {'error': f'Failed to add members: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def remove_members(self, request, pk=None):
        """Remove members from hiring team"""
        team = self.get_object()
        member_ids = request.data.get('member_ids', [])
        
        try:
            team.members.remove(*member_ids)
            return Response({'message': 'Members removed successfully'})
        except Exception as e:
            return Response(
                {'error': f'Failed to remove members: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )


class HiringDecisionViewSet(viewsets.ModelViewSet):
    queryset = HiringDecision.objects.all()
    serializer_class = HiringDecisionSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['comments', 'recommendation']
    filterset_fields = ['decision', 'is_final', 'application', 'reviewer']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return HiringDecisionCreateSerializer
        return super().get_serializer_class()
    
    def perform_create(self, serializer):
        service = CollaborativeHiringService()
        decision = service.add_decision(
            application_id=serializer.validated_data['application'].id,
            reviewer_id=serializer.validated_data['reviewer'].id,
            decision=serializer.validated_data['decision'],
            score=serializer.validated_data.get('score', 0),
            comments=serializer.validated_data.get('comments', ''),
            strengths=serializer.validated_data.get('strengths', []),
            concerns=serializer.validated_data.get('concerns', []),
            recommendation=serializer.validated_data.get('recommendation', ''),
            is_final=serializer.validated_data.get('is_final', False),
            user=self.request.user
        )
        
        if decision:
            return Response(
                HiringDecisionSerializer(decision).data,
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {'error': 'Failed to add hiring decision'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def make_final(self, request, pk=None):
        """Make decision final"""
        decision = self.get_object()
        
        try:
            decision.is_final = True
            decision.save()
            return Response({'message': 'Decision marked as final'})
        except Exception as e:
            return Response(
                {'error': f'Failed to mark decision as final: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )


class InterviewScheduleViewSet(viewsets.ModelViewSet):
    queryset = InterviewSchedule.objects.all()
    serializer_class = InterviewScheduleSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'description', 'location']
    filterset_fields = ['interview_type', 'status', 'application', 'candidate']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return InterviewScheduleCreateSerializer
        return super().get_serializer_class()
    
    def perform_create(self, serializer):
        service = CollaborativeHiringService()
        interview = service.schedule_interview(
            application_id=serializer.validated_data['application'].id,
            interview_type=serializer.validated_data['interview_type'],
            title=serializer.validated_data['title'],
            description=serializer.validated_data.get('description', ''),
            scheduled_date=serializer.validated_data['scheduled_date'],
            duration_minutes=serializer.validated_data.get('duration_minutes', 60),
            location=serializer.validated_data.get('location', ''),
            meeting_url=serializer.validated_data.get('meeting_url', ''),
            interviewer_ids=serializer.validated_data.get('interviewers', []),
            user=self.request.user
        )
        
        if interview:
            return Response(
                InterviewScheduleSerializer(interview).data,
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {'error': 'Failed to schedule interview'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update interview status"""
        interview = self.get_object()
        serializer = InterviewScheduleUpdateSerializer(data=request.data)
        
        if serializer.is_valid():
            service = CollaborativeHiringService()
            updated_interview = service.update_interview_status(
                interview_id=interview.id,
                status=serializer.validated_data['status'],
                feedback=serializer.validated_data.get('feedback'),
                rating=serializer.validated_data.get('rating'),
                would_hire=serializer.validated_data.get('would_hire'),
                internal_notes=serializer.validated_data.get('internal_notes'),
                candidate_notes=serializer.validated_data.get('candidate_notes'),
                user=self.request.user
            )
            
            if updated_interview:
                return Response(
                    InterviewScheduleSerializer(updated_interview).data,
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {'error': 'Failed to update interview status'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def bulk_schedule(self, request):
        """Bulk schedule interviews"""
        serializer = BulkInterviewScheduleSerializer(data=request.data)
        
        if serializer.is_valid():
            service = CollaborativeHiringService()
            scheduled_interviews = []
            
            for interview_data in serializer.validated_data['interviews']:
                interview = service.schedule_interview(
                    application_id=interview_data['application'].id,
                    interview_type=interview_data['interview_type'],
                    title=interview_data['title'],
                    description=interview_data.get('description', ''),
                    scheduled_date=interview_data['scheduled_date'],
                    duration_minutes=interview_data.get('duration_minutes', 60),
                    location=interview_data.get('location', ''),
                    meeting_url=interview_data.get('meeting_url', ''),
                    interviewer_ids=interview_data.get('interviewers', []),
                    user=self.request.user
                )
                
                if interview:
                    scheduled_interviews.append(interview)
            
            return Response(
                InterviewScheduleSerializer(scheduled_interviews, many=True).data,
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CandidateFeedbackViewSet(viewsets.ModelViewSet):
    queryset = CandidateFeedback.objects.all()
    serializer_class = CandidateFeedbackSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['observations', 'recommendations']
    filterset_fields = ['feedback_type', 'application', 'reviewer', 'is_shared_with_candidate', 'is_shared_with_team']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CandidateFeedbackCreateSerializer
        return super().get_serializer_class()
    
    def perform_create(self, serializer):
        service = CollaborativeHiringService()
        feedback = service.add_feedback(
            application_id=serializer.validated_data['application'].id,
            reviewer_id=serializer.validated_data['reviewer'].id,
            feedback_type=serializer.validated_data['feedback_type'],
            score=serializer.validated_data.get('score'),
            max_score=serializer.validated_data.get('max_score', 10),
            strengths=serializer.validated_data.get('strengths', []),
            weaknesses=serializer.validated_data.get('weaknesses', []),
            observations=serializer.validated_data.get('observations', ''),
            recommendations=serializer.validated_data.get('recommendations', ''),
            is_shared_with_candidate=serializer.validated_data.get('is_shared_with_candidate', False),
            is_shared_with_team=serializer.validated_data.get('is_shared_with_team', True),
            user=self.request.user
        )
        
        if feedback:
            return Response(
                CandidateFeedbackSerializer(feedback).data,
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {'error': 'Failed to add feedback'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def bulk_request(self, request):
        """Bulk request feedback"""
        serializer = BulkFeedbackRequestSerializer(data=request.data)
        
        if serializer.is_valid():
            service = CollaborativeHiringService()
            requested_feedback = []
            
            for feedback_data in serializer.validated_data['feedback_requests']:
                feedback = service.add_feedback(
                    application_id=serializer.validated_data['application_id'],
                    reviewer_id=feedback_data['reviewer'].id,
                    feedback_type=feedback_data['feedback_type'],
                    score=feedback_data.get('score'),
                    max_score=feedback_data.get('max_score', 10),
                    strengths=feedback_data.get('strengths', []),
                    weaknesses=feedback_data.get('weaknesses', []),
                    observations=feedback_data.get('observations', ''),
                    recommendations=feedback_data.get('recommendations', ''),
                    is_shared_with_candidate=feedback_data.get('is_shared_with_candidate', False),
                    is_shared_with_team=feedback_data.get('is_shared_with_team', True),
                    user=self.request.user
                )
                
                if feedback:
                    requested_feedback.append(feedback)
            
            return Response(
                CandidateFeedbackSerializer(requested_feedback, many=True).data,
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HiringWorkflowViewSet(viewsets.ModelViewSet):
    queryset = HiringWorkflow.objects.all()
    serializer_class = HiringWorkflowSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']
    filterset_fields = ['workflow_type', 'is_default', 'is_active']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return HiringWorkflowCreateSerializer
        return super().get_serializer_class()
    
    def perform_create(self, serializer):
        service = CollaborativeHiringService()
        workflow = service.create_workflow(
            name=serializer.validated_data['name'],
            workflow_type=serializer.validated_data['workflow_type'],
            stages=serializer.validated_data['stages'],
            job_id=serializer.validated_data.get('job_id'),
            is_default=serializer.validated_data.get('is_default', False),
            is_active=serializer.validated_data.get('is_active', True),
            description=serializer.validated_data.get('description', ''),
            user=self.request.user
        )
        
        if workflow:
            return Response(
                HiringWorkflowSerializer(workflow).data,
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {'error': 'Failed to create workflow'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """Set workflow as default"""
        workflow = self.get_object()
        
        try:
            # Remove default from other workflows
            HiringWorkflow.objects.filter(
                workflow_type=workflow.workflow_type,
                is_default=True
            ).update(is_default=False)
            
            # Set this as default
            workflow.is_default = True
            workflow.save()
            
            return Response({'message': 'Workflow set as default'})
        except Exception as e:
            return Response(
                {'error': f'Failed to set workflow as default: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )


class JobWorkflowViewSet(viewsets.ModelViewSet):
    queryset = JobWorkflow.objects.all()
    serializer_class = JobWorkflowSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['current_stage']
    filterset_fields = ['job', 'workflow', 'is_active']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return JobWorkflowCreateSerializer
        return super().get_serializer_class()
    
    def perform_create(self, serializer):
        service = CollaborativeHiringService()
        workflow = JobWorkflow.objects.create(
            job_id=serializer.validated_data['job'].id,
            workflow_id=serializer.validated_data['workflow'].id,
            current_stage=serializer.validated_data.get('current_stage', 'application_review'),
            is_active=True
        )
        
        return Response(
            JobWorkflowSerializer(workflow).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'])
    def advance_stage(self, request, pk=None):
        """Advance workflow stage"""
        job_workflow = self.get_object()
        new_stage = request.data.get('new_stage')
        
        if not new_stage:
            return Response(
                {'error': 'New stage is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Add to stage history
            stage_history = job_workflow.stage_history or []
            stage_history.append({
                'stage': job_workflow.current_stage,
                'timestamp': timezone.now().isoformat(),
                'advanced_by': self.request.user.get_full_name()
            })
            
            job_workflow.current_stage = new_stage
            job_workflow.stage_history = stage_history
            job_workflow.save()
            
            return Response({'message': 'Stage advanced successfully'})
        except Exception as e:
            return Response(
                {'error': f'Failed to advance stage: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )


class TeamCollaborationViewSet(viewsets.ModelViewSet):
    queryset = TeamCollaboration.objects.all()
    serializer_class = TeamCollaborationSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'message', 'resolution']
    filterset_fields = ['collaboration_type', 'status', 'priority', 'application', 'initiator']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TeamCollaborationCreateSerializer
        return super().get_serializer_class()
    
    def perform_create(self, serializer):
        service = CollaborativeHiringService()
        collaboration = service.create_collaboration(
            application_id=serializer.validated_data['application'].id,
            collaboration_type=serializer.validated_data['collaboration_type'],
            title=serializer.validated_data['title'],
            message=serializer.validated_data['message'],
            participant_ids=serializer.validated_data.get('participants', []),
            priority=serializer.validated_data.get('priority', 'medium'),
            user=self.request.user
        )
        
        if collaboration:
            return Response(
                TeamCollaborationSerializer(collaboration).data,
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {'error': 'Failed to create collaboration'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Resolve collaboration"""
        collaboration = self.get_object()
        resolution = request.data.get('resolution')
        
        if not resolution:
            return Response(
                {'error': 'Resolution is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = CollaborativeHiringService()
        resolved_collaboration = service.resolve_collaboration(
            collaboration_id=collaboration.id,
            resolution=resolution,
            resolved_by_id=self.request.user.id,
            user=self.request.user
        )
        
        if resolved_collaboration:
            return Response(
                TeamCollaborationSerializer(resolved_collaboration).data,
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {'error': 'Failed to resolve collaboration'},
                status=status.HTTP_400_BAD_REQUEST
            )


class InterviewKitViewSet(viewsets.ModelViewSet):
    queryset = InterviewKit.objects.all()
    serializer_class = InterviewKitSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description', 'job_category']
    filterset_fields = ['job_category', 'is_public', 'created_by']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return InterviewKitCreateSerializer
        return super().get_serializer_class()
    
    def perform_create(self, serializer):
        service = CollaborativeHiringService()
        kit = service.create_interview_kit(
            name=serializer.validated_data['name'],
            description=serializer.validated_data.get('description', ''),
            job_category=serializer.validated_data.get('job_category', ''),
            questions=serializer.validated_data.get('questions', []),
            evaluation_criteria=serializer.validated_data.get('evaluation_criteria', {}),
            scoring_rubric=serializer.validated_data.get('scoring_rubric', {}),
            time_allocations=serializer.validated_data.get('time_allocations', {}),
            resources=serializer.validated_data.get('resources', []),
            templates=serializer.validated_data.get('templates', []),
            is_public=serializer.validated_data.get('is_public', False),
            user=self.request.user
        )
        
        if kit:
            return Response(
                InterviewKitSerializer(kit).data,
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {'error': 'Failed to create interview kit'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Duplicate interview kit"""
        kit = self.get_object()
        
        try:
            new_kit = InterviewKit.objects.create(
                name=f"{kit.name} (Copy)",
                description=kit.description,
                job_category=kit.job_category,
                questions=kit.questions,
                evaluation_criteria=kit.evaluation_criteria,
                scoring_rubric=kit.scoring_rubric,
                time_allocations=kit.time_allocations,
                resources=kit.resources,
                templates=kit.templates,
                is_public=False,
                created_by=self.request.user
            )
            
            return Response(
                InterviewKitSerializer(new_kit).data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {'error': f'Failed to duplicate kit: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )


class JobInterviewKitViewSet(viewsets.ModelViewSet):
    queryset = JobInterviewKit.objects.all()
    serializer_class = JobInterviewKitSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = []
    filterset_fields = ['job', 'interview_kit', 'is_active']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return JobInterviewKitCreateSerializer
        return super().get_serializer_class()
    
    def perform_create(self, serializer):
        service = CollaborativeHiringService()
        assignment = service.assign_interview_kit(
            job_id=serializer.validated_data['job'].id,
            kit_id=serializer.validated_data['interview_kit'].id,
            is_active=serializer.validated_data.get('is_active', True),
            user=self.request.user
        )
        
        if assignment:
            return Response(
                JobInterviewKitSerializer(assignment).data,
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {'error': 'Failed to assign interview kit'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate interview kit assignment"""
        assignment = self.get_object()
        
        try:
            # Deactivate other assignments for this job
            JobInterviewKit.objects.filter(
                job=assignment.job,
                is_active=True
            ).exclude(id=assignment.id).update(is_active=False)
            
            # Activate this assignment
            assignment.is_active = True
            assignment.save()
            
            return Response({'message': 'Interview kit assignment activated'})
        except Exception as e:
            return Response(
                {'error': f'Failed to activate assignment: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )


class HiringAnalyticsViewSet(viewsets.ModelViewSet):
    queryset = HiringAnalytics.objects.all()
    serializer_class = HiringAnalyticsSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = []
    filterset_fields = ['metric_type', 'date', 'job', 'team', 'workflow']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return HiringAnalyticsCreateSerializer
        return super().get_serializer_class()
    
    def perform_create(self, serializer):
        service = CollaborativeHiringService()
        analytics = service.create_analytics(
            metric_type=serializer.validated_data['metric_type'],
            date=serializer.validated_data['date'],
            value=serializer.validated_data['value'],
            metadata=serializer.validated_data.get('metadata', {}),
            job_id=serializer.validated_data.get('job_id'),
            team_id=serializer.validated_data.get('team_id'),
            workflow_id=serializer.validated_data.get('workflow_id'),
            user=self.request.user
        )
        
        if analytics:
            return Response(
                HiringAnalyticsSerializer(analytics).data,
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {'error': 'Failed to create analytics'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def team_effectiveness(self, request):
        """Get team effectiveness metrics"""
        team_id = request.query_params.get('team_id')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not team_id:
            return Response(
                {'error': 'team_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Parse dates
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date() if start_date else None
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date() if end_date else None
        
        effectiveness = HiringAnalyticsService.calculate_team_effectiveness(
            team_id=team_id,
            start_date=start_date,
            end_date=end_date
        )
        
        if effectiveness:
            return Response(effectiveness)
        else:
            return Response(
                {'error': 'Failed to calculate team effectiveness'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def interview_to_offer_rate(self, request):
        """Get interview to offer rate"""
        job_id = request.query_params.get('job_id')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not job_id:
            return Response(
                {'error': 'job_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Parse dates
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date() if start_date else None
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date() if end_date else None
        
        rate = HiringAnalyticsService.calculate_interview_to_offer_rate(
            job_id=job_id,
            start_date=start_date,
            end_date=end_date
        )
        
        return Response({'interview_to_offer_rate': rate})


class TeamNotificationViewSet(viewsets.ModelViewSet):
    queryset = TeamNotification.objects.all()
    serializer_class = TeamNotificationSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'message']
    filterset_fields = ['team', 'notification_type', 'is_sent', 'is_read', 'delivery_method']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TeamNotificationCreateSerializer
        return super().get_serializer_class()
    
    def perform_create(self, serializer):
        service = CollaborativeHiringService()
        notification = service.send_notification(
            team_id=serializer.validated_data['team'].id,
            notification_type=serializer.validated_data['notification_type'],
            title=serializer.validated_data['title'],
            message=serializer.validated_data['message'],
            related_object_id=serializer.validated_data.get('related_object_id'),
            related_object_type=serializer.validated_data.get('related_object_type', ''),
            delivery_method=serializer.validated_data.get('delivery_method', 'in_app'),
            user=self.request.user
        )
        
        if notification:
            return Response(
                TeamNotificationSerializer(notification).data,
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {'error': 'Failed to send notification'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """Mark notification as read"""
        notification = self.get_object()
        
        try:
            notification.is_read = True
            notification.read_at = timezone.now()
            notification.save()
            
            return Response({'message': 'Notification marked as read'})
        except Exception as e:
            return Response(
                {'error': f'Failed to mark notification as read: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        """Mark all notifications as read for user"""
        team_id = request.data.get('team_id')
        
        if not team_id:
            return Response(
                {'error': 'team_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            TeamNotification.objects.filter(
                team_id=team_id,
                is_read=False
            ).update(is_read=True, read_at=timezone.now())
            
            return Response({'message': 'All notifications marked as read'})
        except Exception as e:
            return Response(
                {'error': f'Failed to mark notifications as read: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
