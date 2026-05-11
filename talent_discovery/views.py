from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import timedelta

from .models import (
    TalentPool, TalentCandidate, TalentSearch, TalentEngagement,
    TalentCampaign, TalentCampaignExecution, TalentInsight,
    TalentSource, TalentSourcingRule, TalentAnalytics
)
from .serializers import (
    TalentPoolSerializer, TalentCandidateSerializer, TalentSearchSerializer,
    TalentEngagementSerializer, TalentCampaignSerializer,
    TalentCampaignExecutionSerializer, TalentInsightSerializer,
    TalentSourceSerializer, TalentSourcingRuleSerializer,
    TalentAnalyticsSerializer, TalentPoolCreateSerializer,
    TalentCandidateCreateSerializer, TalentEngagementCreateSerializer,
    TalentCampaignCreateSerializer, TalentSearchCreateSerializer,
    BulkCandidateAddSerializer, TalentCampaignLaunchSerializer,
    CandidateSearchRequestSerializer, TalentInsightGenerateSerializer
)
from .services import TalentDiscoveryService, TalentAnalyticsService


class TalentPoolViewSet(viewsets.ModelViewSet):
    serializer_class = TalentPoolSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = TalentPool.objects.select_related('created_by')
        
        pool_type = self.request.query_params.get('pool_type')
        if pool_type:
            queryset = queryset.filter(pool_type=pool_type)
        
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset.order_by('name')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TalentPoolCreateSerializer
        return TalentPoolSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_candidates(self, request, pk=None):
        pool = self.get_object()
        serializer = BulkCandidateAddSerializer(data=request.data)
        
        if serializer.is_valid():
            service = TalentDiscoveryService()
            
            candidates_added = 0
            for candidate_data in serializer.validated_data['candidates']:
                candidate = service.add_candidate_to_pool(
                    pool_id=pool.id,
                    candidate_data=candidate_data,
                    source=serializer.validated_data.get('source', 'other'),
                    source_details=serializer.validated_data.get('source_details', '')
                )
                
                if candidate:
                    candidates_added += 1
            
            return Response({
                'message': f'Added {candidates_added} candidates to pool',
                'candidates_added': candidates_added
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def candidates(self, request, pk=None):
        pool = self.get_object()
        
        status_filter = request.query_params.get('status')
        skill_filter = request.query_params.get('skill')
        location_filter = request.query_params.get('location')
        
        candidates = TalentCandidate.objects.filter(pool=pool)
        
        if status_filter:
            candidates = candidates.filter(status=status_filter)
        if skill_filter:
            candidates = candidates.filter(skills__overlap=[skill_filter])
        if location_filter:
            candidates = candidates.filter(location__icontains=location_filter)
        
        serializer = TalentCandidateSerializer(candidates, many=True)
        return Response(serializer.data)


class TalentCandidateViewSet(viewsets.ModelViewSet):
    serializer_class = TalentCandidateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = TalentCandidate.objects.select_related('pool', 'user')
        
        pool_id = self.request.query_params.get('pool_id')
        if pool_id:
            queryset = queryset.filter(pool_id=pool_id)
        
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        source = self.request.query_params.get('source')
        if source:
            queryset = queryset.filter(source=source)
        
        return queryset.order_by('-discovered_at')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TalentCandidateCreateSerializer
        return TalentCandidateSerializer
    
    @action(detail=True, methods=['post'])
    def engage(self, request, pk=None):
        candidate = self.get_object()
        serializer = TalentEngagementCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            service = TalentDiscoveryService()
            engagement = service.engage_candidate(
                candidate_id=candidate.id,
                engagement_type=serializer.validated_data['engagement_type'],
                subject=serializer.validated_data.get('subject', ''),
                message=serializer.validated_data['message'],
                template_used=serializer.validated_data.get('template_used'),
                user=request.user
            )
            
            if engagement:
                return Response(TalentEngagementSerializer(engagement).data)
            
            return Response(
                {'error': 'Failed to engage candidate'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TalentSearchViewSet(viewsets.ModelViewSet):
    serializer_class = TalentSearchSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = TalentSearch.objects.select_related('created_by')
        
        search_type = self.request.query_params.get('search_type')
        if search_type:
            queryset = queryset.filter(search_type=search_type)
        
        return queryset.order_by('-created_at')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TalentSearchCreateSerializer
        return TalentSearchSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['post'])
    def search_candidates(self, request):
        serializer = CandidateSearchRequestSerializer(data=request.data)
        
        if serializer.is_valid():
            service = TalentDiscoveryService()
            
            candidates = service.search_candidates(
                query=serializer.validated_data['query'],
                search_type=serializer.validated_data.get('search_type', 'keyword'),
                filters=serializer.validated_data.get('filters', {}),
                limit=serializer.validated_data.get('limit', 50),
                offset=serializer.validated_data.get('offset', 0)
            )
            
            candidate_serializer = TalentCandidateSerializer(candidates, many=True)
            return Response(candidate_serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def search_external(self, request):
        query = request.data.get('query')
        sources = request.data.get('sources', ['linkedin'])
        filters = request.data.get('filters', {})
        
        if not query:
            return Response(
                {'error': 'query is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = TalentDiscoveryService()
        candidates = service.search_external_sources(query, sources, filters)
        
        return Response({
            'query': query,
            'sources': sources,
            'candidates_found': len(candidates),
            'candidates': candidates
        })


class TalentEngagementViewSet(viewsets.ModelViewSet):
    serializer_class = TalentEngagementSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = TalentEngagement.objects.select_related('candidate', 'created_by')
        
        candidate_id = self.request.query_params.get('candidate_id')
        if candidate_id:
            queryset = queryset.filter(candidate_id=candidate_id)
        
        engagement_type = self.request.query_params.get('engagement_type')
        if engagement_type:
            queryset = queryset.filter(engagement_type=engagement_type)
        
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset.order_by('-sent_at')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TalentEngagementCreateSerializer
        return TalentEngagementSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class TalentCampaignViewSet(viewsets.ModelViewSet):
    serializer_class = TalentCampaignSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = TalentCampaign.objects.select_related('created_by').prefetch_related('target_pools')
        
        campaign_type = self.request.query_params.get('campaign_type')
        if campaign_type:
            queryset = queryset.filter(campaign_type=campaign_type)
        
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset.order_by('-created_at')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TalentCampaignCreateSerializer
        return TalentCampaignSerializer
    
    def perform_create(self, serializer):
        campaign = serializer.save(created_by=self.request.user)
        
        # Set target pools if provided
        if 'target_pools' in self.request.data:
            campaign.target_pools.set(self.request.data['target_pools'])
    
    @action(detail=True, methods=['post'])
    def launch(self, request, pk=None):
        campaign = self.get_object()
        serializer = TalentCampaignLaunchSerializer(data=request.data)
        
        if serializer.is_valid():
            service = TalentDiscoveryService()
            result = service.launch_campaign(
                campaign_id=campaign.id,
                send_immediately=serializer.validated_data.get('send_immediately', False),
                user=request.user
            )
            
            if result:
                return Response(result)
            
            return Response(
                {'error': 'Failed to launch campaign'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def executions(self, request, pk=None):
        campaign = self.get_object()
        
        executions = TalentCampaignExecution.objects.filter(campaign=campaign).select_related('candidate')
        
        status_filter = request.query_params.get('status')
        if status_filter:
            executions = executions.filter(status=status_filter)
        
        serializer = TalentCampaignExecutionSerializer(executions, many=True)
        return Response(serializer.data)


class TalentInsightViewSet(viewsets.ModelViewSet):
    serializer_class = TalentInsightSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = TalentInsight.objects.all()
        
        insight_type = self.request.query_params.get('insight_type')
        if insight_type:
            queryset = queryset.filter(insight_type=insight_type)
        
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset.order_by('-generated_at')
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        serializer = TalentInsightGenerateSerializer(data=request.data)
        
        if serializer.is_valid():
            service = TalentDiscoveryService()
            insight = service.generate_insight(
                insight_type=serializer.validated_data['insight_type'],
                parameters=serializer.validated_data.get('parameters', {})
            )
            
            if insight:
                return Response(TalentInsightSerializer(insight).data)
            
            return Response(
                {'error': 'Failed to generate insight'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TalentSourceViewSet(viewsets.ModelViewSet):
    serializer_class = TalentSourceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = TalentSource.objects.all()
        
        source_type = self.request.query_params.get('source_type')
        if source_type:
            queryset = queryset.filter(source_type=source_type)
        
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset.order_by('name')


class TalentSourcingRuleViewSet(viewsets.ModelViewSet):
    serializer_class = TalentSourcingRuleSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = TalentSourcingRule.objects.select_related('created_by')
        
        rule_type = self.request.query_params.get('rule_type')
        if rule_type:
            queryset = queryset.filter(rule_type=rule_type)
        
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset.order_by('name')
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['post'])
    def run_rules(self, request):
        service = TalentDiscoveryService()
        service.run_sourcing_rules()
        
        return Response({'message': 'Sourcing rules executed'})


class TalentAnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TalentAnalyticsSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = TalentAnalytics.objects.select_related('pool', 'campaign', 'source')
        
        metric_type = self.request.query_params.get('metric_type')
        if metric_type:
            queryset = queryset.filter(metric_type=metric_type)
        
        pool_id = self.request.query_params.get('pool_id')
        if pool_id:
            queryset = queryset.filter(pool_id=pool_id)
        
        campaign_id = self.request.query_params.get('campaign_id')
        if campaign_id:
            queryset = queryset.filter(campaign_id=campaign_id)
        
        source_id = self.request.query_params.get('source_id')
        if source_id:
            queryset = queryset.filter(source_id=source_id)
        
        start_date = self.request.query_params.get('start_date')
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        
        end_date = self.request.query_params.get('end_date')
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        return queryset.order_by('-date')
    
    @action(detail=False, methods=['get'])
    def pool_metrics(self, request):
        pool_id = request.query_params.get('pool_id')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        service = TalentAnalyticsService()
        metrics = service.get_pool_analytics(pool_id, start_date, end_date)
        
        serializer = TalentAnalyticsSerializer(metrics, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def engagement_metrics(self, request):
        pool_id = request.query_params.get('pool_id')
        campaign_id = request.query_params.get('campaign_id')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        service = TalentAnalyticsService()
        metrics = service.get_engagement_analytics(pool_id, campaign_id, start_date, end_date)
        
        serializer = TalentAnalyticsSerializer(metrics, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        # Get overall talent discovery summary
        total_pools = TalentPool.objects.count()
        total_candidates = TalentCandidate.objects.count()
        active_campaigns = TalentCampaign.objects.filter(status='active').count()
        total_engagements = TalentEngagement.objects.count()
        
        # Recent activity
        recent_engagements = TalentEngagement.objects.filter(
            sent_at__gte=timezone.now() - timedelta(days=7)
        ).count()
        
        return Response({
            'total_pools': total_pools,
            'total_candidates': total_candidates,
            'active_campaigns': active_campaigns,
            'total_engagements': total_engagements,
            'recent_engagements': recent_engagements
        })
