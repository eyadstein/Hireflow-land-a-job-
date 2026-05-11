from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import timedelta

from .models import (
    CandidateProfile, CandidateInteraction, CandidateTask, CandidateDocument,
    CandidatePipeline, CandidatePipelineStage, CandidateTag, CandidateEmail,
    CandidateActivity, CandidateRelationship
)
from .serializers import (
    CandidateProfileSerializer, CandidateInteractionSerializer, CandidateTaskSerializer,
    CandidateDocumentSerializer, CandidatePipelineSerializer, CandidatePipelineStageSerializer,
    CandidateTagSerializer, CandidateEmailSerializer, CandidateActivitySerializer,
    CandidateRelationshipSerializer, CandidateInteractionCreateSerializer,
    CandidateTaskCreateSerializer, CandidateDocumentCreateSerializer,
    CandidatePipelineStageCreateSerializer, BulkCandidateTaskSerializer,
    CandidateStatusUpdateSerializer, CandidateAssignmentSerializer
)
from .services import CandidateCRMService, CandidateAnalyticsService


class CandidateProfileViewSet(viewsets.ModelViewSet):
    serializer_class = CandidateProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = CandidateProfile.objects.select_related('user', 'assigned_to')
        
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        assigned_to = self.request.query_params.get('assigned_to')
        if assigned_to:
            queryset = queryset.filter(assigned_to_id=assigned_to)
        
        source = self.request.query_params.get('source')
        if source:
            queryset = queryset.filter(source=source)
        
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset.order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        candidate = self.get_object()
        serializer = CandidateStatusUpdateSerializer(data=request.data)
        
        if serializer.is_valid():
            service = CandidateCRMService()
            updated_candidate = service.update_candidate_status(
                candidate_id=candidate.id,
                new_status=serializer.validated_data['status'],
                notes=serializer.validated_data.get('notes', ''),
                user=request.user
            )
            
            if updated_candidate:
                return Response(CandidateProfileSerializer(updated_candidate).data)
            
            return Response(
                {'error': 'Failed to update status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        candidate = self.get_object()
        serializer = CandidateAssignmentSerializer(data=request.data)
        
        if serializer.is_valid():
            service = CandidateCRMService()
            updated_candidate = service.assign_candidate(
                candidate_id=candidate.id,
                assigned_to_id=serializer.validated_data.get('assigned_to'),
                notes=serializer.validated_data.get('notes', ''),
                user=request.user
            )
            
            if updated_candidate:
                return Response(CandidateProfileSerializer(updated_candidate).data)
            
            return Response(
                {'error': 'Failed to assign candidate'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def summary(self, request, pk=None):
        candidate = self.get_object()
        service = CandidateCRMService()
        summary = service.get_candidate_summary(candidate.id)
        
        if summary:
            return Response(summary)
        
        return Response(
            {'error': 'Candidate not found'},
            status=status.HTTP_404_NOT_FOUND
        )


class CandidateInteractionViewSet(viewsets.ModelViewSet):
    serializer_class = CandidateInteractionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = CandidateInteraction.objects.select_related('candidate__user', 'created_by')
        
        candidate_id = self.request.query_params.get('candidate_id')
        if candidate_id:
            queryset = queryset.filter(candidate_id=candidate_id)
        
        interaction_type = self.request.query_params.get('interaction_type')
        if interaction_type:
            queryset = queryset.filter(interaction_type=interaction_type)
        
        created_by = self.request.query_params.get('created_by')
        if created_by:
            queryset = queryset.filter(created_by_id=created_by)
        
        return queryset.order_by('-date')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CandidateInteractionCreateSerializer
        return CandidateInteractionSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class CandidateTaskViewSet(viewsets.ModelViewSet):
    serializer_class = CandidateTaskSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = CandidateTask.objects.select_related('candidate__user', 'assigned_to', 'created_by')
        
        candidate_id = self.request.query_params.get('candidate_id')
        if candidate_id:
            queryset = queryset.filter(candidate_id=candidate_id)
        
        assigned_to = self.request.query_params.get('assigned_to')
        if assigned_to:
            queryset = queryset.filter(assigned_to_id=assigned_to)
        
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        priority = self.request.query_params.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)
        
        return queryset.order_by('due_date', '-created_at')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CandidateTaskCreateSerializer
        return CandidateTaskSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        task = self.get_object()
        service = CandidateCRMService()
        
        completed_task = service.complete_task(task.id, user=request.user)
        
        if completed_task:
            return Response(CandidateTaskSerializer(completed_task).data)
        
        return Response(
            {'error': 'Failed to complete task'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=False, methods=['get'])
    def due_soon(self, request):
        days_ahead = int(request.query_params.get('days', 7))
        service = CandidateCRMService()
        
        tasks = service.get_due_tasks(user=request.user, days_ahead=days_ahead)
        
        serializer = CandidateTaskSerializer(tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        serializer = BulkCandidateTaskSerializer(data=request.data)
        
        if serializer.is_valid():
            service = CandidateCRMService()
            
            tasks = []
            for candidate_id in serializer.validated_data['candidates']:
                task = service.create_task(
                    candidate_id=candidate_id,
                    title=serializer.validated_data['title'],
                    description=serializer.validated_data['description'],
                    priority=serializer.validated_data['priority'],
                    due_date=serializer.validated_data.get('due_date'),
                    assigned_to=serializer.validated_data.get('assigned_to'),
                    user=request.user
                )
                
                if task:
                    tasks.append(task)
            
            return Response({
                'message': f'Created {len(tasks)} tasks',
                'created_count': len(tasks)
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CandidateDocumentViewSet(viewsets.ModelViewSet):
    serializer_class = CandidateDocumentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = CandidateDocument.objects.select_related('candidate__user', 'uploaded_by')
        
        candidate_id = self.request.query_params.get('candidate_id')
        if candidate_id:
            queryset = queryset.filter(candidate_id=candidate_id)
        
        document_type = self.request.query_params.get('document_type')
        if document_type:
            queryset = queryset.filter(document_type=document_type)
        
        is_public = self.request.query_params.get('is_public')
        if is_public is not None:
            queryset = queryset.filter(is_public=is_public.lower() == 'true')
        
        return queryset.order_by('-uploaded_at')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CandidateDocumentCreateSerializer
        return CandidateDocumentSerializer
    
    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)


class CandidatePipelineViewSet(viewsets.ModelViewSet):
    serializer_class = CandidatePipelineSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = CandidatePipeline.objects.select_related('created_by')
        
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset.order_by('name')
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        pipeline = self.get_object()
        service = CandidateCRMService()
        
        stats = service.get_pipeline_statistics(pipeline.id)
        
        if stats:
            return Response(stats)
        
        return Response(
            {'error': 'Pipeline not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    @action(detail=True, methods=['post'])
    def add_candidate(self, request, pk=None):
        pipeline = self.get_object()
        serializer = CandidatePipelineStageCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            service = CandidateCRMService()
            stage = service.add_candidate_to_pipeline(
                candidate_id=serializer.validated_data['candidate'],
                pipeline_id=pipeline.id,
                stage=serializer.validated_data.get('stage', 'sourcing'),
                notes=serializer.validated_data.get('notes', ''),
                user=request.user
            )
            
            if stage:
                return Response(CandidatePipelineStageSerializer(stage).data)
            
            return Response(
                {'error': 'Failed to add candidate to pipeline'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CandidatePipelineStageViewSet(viewsets.ModelViewSet):
    serializer_class = CandidatePipelineStageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = CandidatePipelineStage.objects.select_related(
            'candidate__user', 'pipeline', 'moved_by'
        )
        
        pipeline_id = self.request.query_params.get('pipeline_id')
        if pipeline_id:
            queryset = queryset.filter(pipeline_id=pipeline_id)
        
        candidate_id = self.request.query_params.get('candidate_id')
        if candidate_id:
            queryset = queryset.filter(candidate_id=candidate_id)
        
        return queryset.order_by('pipeline', 'stage_order', 'entered_at')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CandidatePipelineStageCreateSerializer
        return CandidatePipelineStageSerializer
    
    @action(detail=True, methods=['post'])
    def move_candidate(self, request, pk=None):
        current_stage = self.get_object()
        pipeline_id = current_stage.pipeline.id
        new_stage = request.data.get('new_stage')
        notes = request.data.get('notes', '')
        
        if not new_stage:
            return Response(
                {'error': 'new_stage is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = CandidateCRMService()
        moved_stage = service.move_candidate_in_pipeline(
            candidate_id=current_stage.candidate.id,
            pipeline_id=pipeline_id,
            new_stage=new_stage,
            notes=notes,
            user=request.user
        )
        
        if moved_stage:
            return Response(CandidatePipelineStageSerializer(moved_stage).data)
        
        return Response(
            {'error': 'Failed to move candidate in pipeline'},
            status=status.HTTP_400_BAD_REQUEST
        )


class CandidateTagViewSet(viewsets.ModelViewSet):
    serializer_class = CandidateTagSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = CandidateTag.objects.select_related('created_by')
        
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset.order_by('name')
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class CandidateEmailViewSet(viewsets.ModelViewSet):
    serializer_class = CandidateEmailSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = CandidateEmail.objects.select_related('candidate__user')
        
        candidate_id = self.request.query_params.get('candidate_id')
        if candidate_id:
            queryset = queryset.filter(candidate_id=candidate_id)
        
        direction = self.request.query_params.get('direction')
        if direction:
            queryset = queryset.filter(direction=direction)
        
        return queryset.order_by('-sent_at')


class CandidateActivityViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CandidateActivitySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = CandidateActivity.objects.select_related('candidate__user', 'user')
        
        candidate_id = self.request.query_params.get('candidate_id')
        if candidate_id:
            queryset = queryset.filter(candidate_id=candidate_id)
        
        activity_type = self.request.query_params.get('activity_type')
        if activity_type:
            queryset = queryset.filter(activity_type=activity_type)
        
        return queryset.order_by('-created_at')


class CandidateRelationshipViewSet(viewsets.ModelViewSet):
    serializer_class = CandidateRelationshipSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = CandidateRelationship.objects.select_related(
            'candidate__user', 'related_user', 'created_by'
        )
        
        candidate_id = self.request.query_params.get('candidate_id')
        if candidate_id:
            queryset = queryset.filter(candidate_id=candidate_id)
        
        relationship_type = self.request.query_params.get('relationship_type')
        if relationship_type:
            queryset = queryset.filter(relationship_type=relationship_type)
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class CandidateSearchViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def candidates(self, request):
        service = CandidateCRMService()
        
        candidates = service.search_candidates(
            query=request.query_params.get('q'),
            status=request.query_params.get('status'),
            assigned_to=request.query_params.get('assigned_to'),
            tags=request.query_params.getlist('tags'),
            source=request.query_params.get('source'),
            rating_min=request.query_params.get('rating_min'),
            rating_max=request.query_params.get('rating_max'),
            created_after=request.query_params.get('created_after'),
            created_before=request.query_params.get('created_before')
        )
        
        serializer = CandidateProfileSerializer(candidates, many=True)
        return Response(serializer.data)


class CandidateAnalyticsViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def metrics(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        # Parse dates
        if start_date:
            start_date = timezone.datetime.strptime(start_date, '%Y-%m-%d').date()
        if end_date:
            end_date = timezone.datetime.strptime(end_date, '%Y-%m-%d').date()
        
        # Get metrics
        candidate_metrics = CandidateAnalyticsService.get_candidate_metrics(
            start_date=start_date, end_date=end_date
        )
        
        interaction_metrics = CandidateAnalyticsService.get_interaction_metrics(
            start_date=start_date, end_date=end_date
        )
        
        return Response({
            'candidates': candidate_metrics,
            'interactions': interaction_metrics
        })
    
    @action(detail=False, methods=['get'])
    def pipeline_metrics(self, request):
        pipeline_id = request.query_params.get('pipeline_id')
        
        if pipeline_id:
            metrics = CandidateAnalyticsService.get_pipeline_metrics(
                pipeline_id=int(pipeline_id)
            )
            return Response(metrics)
        
        # Get metrics for all pipelines
        pipelines = CandidatePipeline.objects.all()
        all_metrics = {}
        
        for pipeline in pipelines:
            all_metrics[pipeline.id] = CandidateAnalyticsService.get_pipeline_metrics(
                pipeline.id
            )
        
        return Response(all_metrics)
