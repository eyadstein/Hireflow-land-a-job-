from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import datetime, timedelta

from .models import (
    TalentPool, TalentPoolCandidate, TalentVisualization, TalentAnalytics,
    TalentDashboard, UserDashboard, TalentReport, ReportSchedule, TalentInsight
)
from .serializers import (
    TalentPoolSerializer, TalentPoolCandidateSerializer, TalentVisualizationSerializer,
    TalentAnalyticsSerializer, TalentDashboardSerializer, UserDashboardSerializer,
    TalentReportSerializer, ReportScheduleSerializer, TalentInsightSerializer,
    TalentPoolCreateSerializer, TalentPoolCandidateCreateSerializer, TalentVisualizationCreateSerializer,
    TalentAnalyticsCreateSerializer, TalentDashboardCreateSerializer, UserDashboardCreateSerializer,
    TalentReportCreateSerializer, ReportScheduleCreateSerializer, TalentInsightCreateSerializer,
    BulkAddCandidatesSerializer, BulkAnalyticsSerializer, DashboardLayoutSerializer
)
from .services import TalentVisualizationService, TalentAnalyticsService


class TalentPoolViewSet(viewsets.ModelViewSet):
    queryset = TalentPool.objects.all()
    serializer_class = TalentPoolSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description', 'job_category']
    filterset_fields = ['pool_type', 'is_active', 'created_by']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TalentPoolCreateSerializer
        return super().get_serializer_class()
    
    def perform_create(self, serializer):
        service = TalentVisualizationService()
        pool = service.create_talent_pool(
            name=serializer.validated_data['name'],
            pool_type=serializer.validated_data['pool_type'],
            job_category=serializer.validated_data.get('job_category', ''),
            skills=serializer.validated_data.get('skills', []),
            experience_levels=serializer.validated_data.get('experience_levels', []),
            locations=serializer.validated_data.get('locations', []),
            description=serializer.validated_data.get('description', ''),
            user=self.request.user
        )
        
        if pool:
            return Response(
                TalentPoolSerializer(pool).data,
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {'error': 'Failed to create talent pool'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def add_candidates(self, request, pk=None):
        """Add candidates to talent pool"""
        pool = self.get_object()
        serializer = BulkAddCandidatesSerializer(data=request.data)
        
        if serializer.is_valid():
            service = TalentVisualizationService()
            added_candidates = []
            
            for candidate_data in serializer.validated_data['candidates']:
                candidate = service.add_candidate_to_pool(
                    pool_id=pool.id,
                    candidate_id=candidate_data['candidate'].id,
                    skills=candidate_data.get('skills', []),
                    experience_years=candidate_data.get('experience_years'),
                    education_level=candidate_data.get('education_level', ''),
                    location=candidate_data.get('location', ''),
                    salary_expectation=candidate_data.get('salary_expectation'),
                    availability=candidate_data.get('availability', ''),
                    notes=candidate_data.get('notes', ''),
                    user=self.request.user
                )
                
                if candidate:
                    added_candidates.append(candidate)
            
            return Response(
                TalentPoolCandidateSerializer(added_candidates, many=True).data,
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def metrics(self, request, pk=None):
        """Get pool metrics"""
        pool = self.get_object()
        service = TalentVisualizationService()
        metrics = service.calculate_pool_metrics(pool.id)
        
        if metrics:
            return Response(metrics)
        else:
            return Response(
                {'error': 'Failed to calculate pool metrics'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['get'])
    def skill_gap_analysis(self, request, pk=None):
        """Get skill gap analysis"""
        pool = self.get_object()
        required_skills = request.query_params.getlist('required_skills', [])
        
        service = TalentVisualizationService()
        analysis = service.generate_skill_gap_analysis(pool.id, required_skills)
        
        if analysis:
            return Response(analysis)
        else:
            return Response(
                {'error': 'Failed to generate skill gap analysis'},
                status=status.HTTP_400_BAD_REQUEST
            )


class TalentPoolCandidateViewSet(viewsets.ModelViewSet):
    queryset = TalentPoolCandidate.objects.all()
    serializer_class = TalentPoolCandidateSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['notes', 'education_level', 'location']
    filterset_fields = ['talent_pool', 'candidate', 'status', 'experience_years']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TalentPoolCandidateCreateSerializer
        return super().get_serializer_class()
    
    def perform_create(self, serializer):
        service = TalentVisualizationService()
        candidate = service.add_candidate_to_pool(
            pool_id=serializer.validated_data['talent_pool'].id,
            candidate_id=serializer.validated_data['candidate'].id,
            skills=serializer.validated_data.get('skills', []),
            experience_years=serializer.validated_data.get('experience_years'),
            education_level=serializer.validated_data.get('education_level', ''),
            location=serializer.validated_data.get('location', ''),
            salary_expectation=serializer.validated_data.get('salary_expectation'),
            availability=serializer.validated_data.get('availability', ''),
            notes=serializer.validated_data.get('notes', ''),
            user=self.request.user
        )
        
        if candidate:
            return Response(
                TalentPoolCandidateSerializer(candidate).data,
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {'error': 'Failed to add candidate to pool'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update candidate status"""
        candidate = self.get_object()
        new_status = request.data.get('status')
        notes = request.data.get('notes', '')
        
        if not new_status:
            return Response(
                {'error': 'Status is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = TalentVisualizationService()
        updated_candidate = service.update_candidate_status(
            candidate_id=candidate.candidate.id,
            pool_id=candidate.talent_pool.id,
            status=new_status,
            notes=notes
        )
        
        if updated_candidate:
            return Response(
                TalentPoolCandidateSerializer(updated_candidate).data,
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {'error': 'Failed to update candidate status'},
                status=status.HTTP_400_BAD_REQUEST
            )


class TalentVisualizationViewSet(viewsets.ModelViewSet):
    queryset = TalentVisualization.objects.all()
    serializer_class = TalentVisualizationSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']
    filterset_fields = ['chart_type', 'is_public', 'is_active', 'created_by']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TalentVisualizationCreateSerializer
        return super().get_serializer_class()
    
    def perform_create(self, serializer):
        service = TalentVisualizationService()
        visualization = service.create_visualization(
            name=serializer.validated_data['name'],
            chart_type=serializer.validated_data['chart_type'],
            description=serializer.validated_data.get('description', ''),
            configuration=serializer.validated_data.get('configuration', {}),
            data=serializer.validated_data.get('data', {}),
            filters=serializer.validated_data.get('filters', {}),
            is_public=serializer.validated_data.get('is_public', False),
            user=self.request.user
        )
        
        if visualization:
            return Response(
                TalentVisualizationSerializer(visualization).data,
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {'error': 'Failed to create visualization'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def refresh_data(self, request, pk=None):
        """Refresh visualization data"""
        visualization = self.get_object()
        
        try:
            # In real implementation, this would recalculate data based on current filters
            visualization.data = visualization.data  # Placeholder
            visualization.save()
            
            return Response({'message': 'Data refreshed successfully'})
        except Exception as e:
            return Response(
                {'error': f'Failed to refresh data: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )


class TalentAnalyticsViewSet(viewsets.ModelViewSet):
    queryset = TalentAnalytics.objects.all()
    serializer_class = TalentAnalyticsSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = []
    filterset_fields = ['metric_type', 'date', 'talent_pool', 'job', 'visualization']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TalentAnalyticsCreateSerializer
        return super().get_serializer_class()
    
    def perform_create(self, serializer):
        service = TalentVisualizationService()
        analytics = service.create_analytics(
            metric_type=serializer.validated_data['metric_type'],
            value=serializer.validated_data['value'],
            metadata=serializer.validated_data.get('metadata', {}),
            date=serializer.validated_data['date'],
            talent_pool_id=serializer.validated_data.get('talent_pool_id'),
            job_id=serializer.validated_data.get('job_id'),
            visualization_id=serializer.validated_data.get('visualization_id'),
            user=self.request.user
        )
        
        if analytics:
            return Response(
                TalentAnalyticsSerializer(analytics).data,
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {'error': 'Failed to create analytics'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """Bulk create analytics"""
        serializer = BulkAnalyticsSerializer(data=request.data)
        
        if serializer.is_valid():
            service = TalentVisualizationService()
            created_analytics = []
            
            for analytics_data in serializer.validated_data['analytics_data']:
                analytics = service.create_analytics(
                    metric_type=analytics_data['metric_type'],
                    value=analytics_data['value'],
                    metadata=analytics_data.get('metadata', {}),
                    date=analytics_data['date'],
                    talent_pool_id=analytics_data.get('talent_pool_id'),
                    job_id=analytics_data.get('job_id'),
                    visualization_id=analytics_data.get('visualization_id'),
                    user=self.request.user
                )
                
                if analytics:
                    created_analytics.append(analytics)
            
            return Response(
                TalentAnalyticsSerializer(created_analytics, many=True).data,
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TalentDashboardViewSet(viewsets.ModelViewSet):
    queryset = TalentDashboard.objects.all()
    serializer_class = TalentDashboardSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']
    filterset_fields = ['dashboard_type', 'is_public', 'is_active', 'created_by']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TalentDashboardCreateSerializer
        return super().get_serializer_class()
    
    def perform_create(self, serializer):
        service = TalentVisualizationService()
        dashboard = service.create_dashboard(
            name=serializer.validated_data['name'],
            dashboard_type=serializer.validated_data['dashboard_type'],
            description=serializer.validated_data.get('description', ''),
            layout=serializer.validated_data.get('layout', {}),
            widgets=serializer.validated_data.get('widgets', []),
            filters=serializer.validated_data.get('filters', {}),
            refresh_interval=serializer.validated_data.get('refresh_interval', 300),
            is_public=serializer.validated_data.get('is_public', False),
            user=self.request.user
        )
        
        if dashboard:
            return Response(
                TalentDashboardSerializer(dashboard).data,
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {'error': 'Failed to create dashboard'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def update_layout(self, request, pk=None):
        """Update dashboard layout"""
        dashboard = self.get_object()
        serializer = DashboardLayoutSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                dashboard.layout = serializer.validated_data.get('layout', {})
                dashboard.widgets = serializer.validated_data.get('widgets', [])
                dashboard.filters = serializer.validated_data.get('filters', {})
                dashboard.save()
                
                return Response({'message': 'Layout updated successfully'})
            except Exception as e:
                return Response(
                    {'error': f'Failed to update layout: {str(e)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDashboardViewSet(viewsets.ModelViewSet):
    queryset = UserDashboard.objects.all()
    serializer_class = UserDashboardSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = []
    filterset_fields = ['user', 'dashboard', 'is_favorite']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserDashboardCreateSerializer
        return super().get_serializer_class()
    
    def perform_create(self, serializer):
        service = TalentVisualizationService()
        user_dashboard = service.assign_dashboard_to_user(
            user_id=serializer.validated_data['user'].id,
            dashboard_id=serializer.validated_data['dashboard'].id,
            is_favorite=serializer.validated_data.get('is_favorite', False),
            custom_filters=serializer.validated_data.get('custom_filters', {}),
            custom_layout=serializer.validated_data.get('custom_layout', {})
        )
        
        if user_dashboard:
            return Response(
                UserDashboardSerializer(user_dashboard).data,
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {'error': 'Failed to assign dashboard to user'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def mark_favorite(self, request, pk=None):
        """Mark dashboard as favorite"""
        user_dashboard = self.get_object()
        
        try:
            user_dashboard.is_favorite = True
            user_dashboard.save()
            
            return Response({'message': 'Dashboard marked as favorite'})
        except Exception as e:
            return Response(
                {'error': f'Failed to mark as favorite: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )


class TalentReportViewSet(viewsets.ModelViewSet):
    queryset = TalentReport.objects.all()
    serializer_class = TalentReportSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']
    filterset_fields = ['report_type', 'format', 'is_scheduled', 'created_by']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TalentReportCreateSerializer
        return super().get_serializer_class()
    
    def perform_create(self, serializer):
        service = TalentVisualizationService()
        report = service.create_report(
            name=serializer.validated_data['name'],
            report_type=serializer.validated_data['report_type'],
            description=serializer.validated_data.get('description', ''),
            template=serializer.validated_data.get('template', {}),
            data=serializer.validated_data.get('data', {}),
            filters=serializer.validated_data.get('filters', {}),
            format=serializer.validated_data.get('format', 'pdf'),
            is_scheduled=serializer.validated_data.get('is_scheduled', False),
            schedule_frequency=serializer.validated_data.get('schedule_frequency', ''),
            user=self.request.user
        )
        
        if report:
            return Response(
                TalentReportSerializer(report).data,
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {'error': 'Failed to create report'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def generate(self, request, pk=None):
        """Generate report"""
        report = self.get_object()
        
        try:
            # In real implementation, this would generate the actual report file
            report.last_generated = timezone.now()
            report.save()
            
            return Response({
                'message': 'Report generated successfully',
                'generated_at': report.last_generated
            })
        except Exception as e:
            return Response(
                {'error': f'Failed to generate report: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )


class ReportScheduleViewSet(viewsets.ModelViewSet):
    queryset = ReportSchedule.objects.all()
    serializer_class = ReportScheduleSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['frequency']
    filterset_fields = ['report', 'frequency', 'is_active', 'created_by']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ReportScheduleCreateSerializer
        return super().get_serializer_class()
    
    def perform_create(self, serializer):
        service = TalentVisualizationService()
        schedule = service.schedule_report(
            report_id=serializer.validated_data['report'].id,
            recipient_ids=serializer.validated_data.get('recipients', []),
            frequency=serializer.validated_data['frequency'],
            next_run=serializer.validated_data.get('next_run'),
            user=self.request.user
        )
        
        if schedule:
            return Response(
                ReportScheduleSerializer(schedule).data,
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {'error': 'Failed to schedule report'},
                status=status.HTTP_400_BAD_REQUEST
            )


class TalentInsightViewSet(viewsets.ModelViewSet):
    queryset = TalentInsight.objects.all()
    serializer_class = TalentInsightSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'description']
    filterset_fields = ['insight_type', 'impact_level', 'is_active', 'created_by']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TalentInsightCreateSerializer
        return super().get_serializer_class()
    
    def perform_create(self, serializer):
        service = TalentVisualizationService()
        insight = service.create_insight(
            title=serializer.validated_data['title'],
            insight_type=serializer.validated_data['insight_type'],
            description=serializer.validated_data['description'],
            data_points=serializer.validated_data.get('data_points', []),
            confidence_score=serializer.validated_data.get('confidence_score', 0.0),
            impact_level=serializer.validated_data.get('impact_level', 'medium'),
            action_items=serializer.validated_data.get('action_items', []),
            expires_at=serializer.validated_data.get('expires_at'),
            user=self.request.user
        )
        
        if insight:
            return Response(
                TalentInsightSerializer(insight).data,
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {'error': 'Failed to create insight'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        """Archive insight"""
        insight = self.get_object()
        
        try:
            insight.is_active = False
            insight.save()
            
            return Response({'message': 'Insight archived successfully'})
        except Exception as e:
            return Response(
                {'error': f'Failed to archive insight: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )


# Analytics endpoints
class AnalyticsViewSet(viewsets.ViewSet):
    
    @action(detail=False, methods=['get'])
    def funnel_data(self, request):
        """Get hiring funnel data"""
        pool_id = request.query_params.get('pool_id')
        job_id = request.query_params.get('job_id')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        # Parse dates
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date() if start_date else None
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date() if end_date else None
        
        service = TalentVisualizationService()
        funnel_data = service.generate_funnel_data(
            pool_id=pool_id,
            job_id=job_id,
            start_date=start_date,
            end_date=end_date
        )
        
        if funnel_data:
            return Response(funnel_data)
        else:
            return Response(
                {'error': 'Failed to generate funnel data'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def pipeline_velocity(self, request):
        """Get pipeline velocity metrics"""
        pool_id = request.query_params.get('pool_id')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        # Parse dates
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date() if start_date else None
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date() if end_date else None
        
        velocity = TalentAnalyticsService.calculate_pipeline_velocity(
            pool_id=pool_id,
            start_date=start_date,
            end_date=end_date
        )
        
        if velocity:
            return Response(velocity)
        else:
            return Response(
                {'error': 'Failed to calculate pipeline velocity'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def source_effectiveness(self, request):
        """Get source effectiveness metrics"""
        pool_id = request.query_params.get('pool_id')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        # Parse dates
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date() if start_date else None
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date() if end_date else None
        
        effectiveness = TalentAnalyticsService.calculate_source_effectiveness(
            pool_id=pool_id,
            start_date=start_date,
            end_date=end_date
        )
        
        if effectiveness:
            return Response(effectiveness)
        else:
            return Response(
                {'error': 'Failed to calculate source effectiveness'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def diversity_metrics(self, request):
        """Get diversity metrics"""
        pool_id = request.query_params.get('pool_id')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        # Parse dates
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date() if start_date else None
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date() if end_date else None
        
        diversity = TalentAnalyticsService.generate_diversity_metrics(
            pool_id=pool_id,
            start_date=start_date,
            end_date=end_date
        )
        
        if diversity:
            return Response(diversity)
        else:
            return Response(
                {'error': 'Failed to generate diversity metrics'},
                status=status.HTTP_400_BAD_REQUEST
            )
