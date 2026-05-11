from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Count, Avg, Max, Min
from django.utils import timezone
from datetime import datetime, timedelta

from .models import (
    MarketData, SalaryInsight, DemandAnalysis, SkillsAnalysis,
    MarketTrend, CompensationBenchmark, MarketReport, ReportSubscription, MarketAlert
)
from .serializers import (
    MarketDataSerializer, SalaryInsightSerializer, DemandAnalysisSerializer,
    SkillsAnalysisSerializer, MarketTrendSerializer, CompensationBenchmarkSerializer,
    MarketReportSerializer, ReportSubscriptionSerializer, MarketAlertSerializer,
    MarketDataCreateSerializer, SalaryInsightCreateSerializer, DemandAnalysisCreateSerializer,
    SkillsAnalysisCreateSerializer, MarketTrendCreateSerializer, CompensationBenchmarkCreateSerializer,
    MarketReportCreateSerializer, ReportSubscriptionCreateSerializer, MarketAlertCreateSerializer,
    BulkMarketDataSerializer, BulkSalaryInsightSerializer, SalaryComparisonSerializer,
    DemandAnalysisSerializer, SkillsGapAnalysisSerializer, MarketTrendAnalysisSerializer,
    CompensationAnalysisSerializer
)
from .services import MarketInsightsService, MarketAnalyticsService


class MarketDataViewSet(viewsets.ModelViewSet):
    queryset = MarketData.objects.all()
    serializer_class = MarketDataSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['job_title', 'job_category', 'location', 'industry']
    filterset_fields = ['data_type', 'job_category', 'location', 'is_active']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return MarketDataCreateSerializer
        return super().get_serializer_class()
    
    def perform_create(self, serializer):
        service = MarketInsightsService()
        market_data = service.create_market_data(
            data_type=serializer.validated_data['data_type'],
            job_category=serializer.validated_data['job_category'],
            job_title=serializer.validated_data['job_title'],
            location=serializer.validated_data['location'],
            data_value=serializer.validated_data['data_value'],
            industry=serializer.validated_data.get('industry', ''),
            experience_level=serializer.validated_data.get('experience_level', ''),
            source=serializer.validated_data.get('source', ''),
            collection_date=serializer.validated_data.get('collection_date'),
            user=self.request.user
        )
        
        if market_data:
            return Response(
                MarketDataSerializer(market_data).data,
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {'error': 'Failed to create market data'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """Bulk create market data"""
        serializer = BulkMarketDataSerializer(data=request.data)
        
        if serializer.is_valid():
            service = MarketInsightsService()
            created_data = []
            
            for data_item in serializer.validated_data['market_data']:
                market_data = service.create_market_data(
                    data_type=data_item['data_type'],
                    job_category=data_item['job_category'],
                    job_title=data_item['job_title'],
                    location=data_item['location'],
                    data_value=data_item['data_value'],
                    industry=data_item.get('industry', ''),
                    experience_level=data_item.get('experience_level', ''),
                    source=data_item.get('source', ''),
                    collection_date=data_item.get('collection_date'),
                    user=self.request.user
                )
                
                if market_data:
                    created_data.append(market_data)
            
            return Response(
                MarketDataSerializer(created_data, many=True).data,
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SalaryInsightViewSet(viewsets.ModelViewSet):
    queryset = SalaryInsight.objects.all()
    serializer_class = SalaryInsightSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['job_title', 'job_category', 'location']
    filterset_fields = ['insight_type', 'job_category', 'location', 'currency']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return SalaryInsightCreateSerializer
        return super().get_serializer_class()
    
    def perform_create(self, serializer):
        service = MarketInsightsService()
        insight = service.create_salary_insight(
            job_title=serializer.validated_data['job_title'],
            job_category=serializer.validated_data['job_category'],
            experience_level=serializer.validated_data.get('experience_level', ''),
            location=serializer.validated_data['location'],
            insight_type=serializer.validated_data['insight_type'],
            salary_data=serializer.validated_data['salary_data'],
            min_salary=serializer.validated_data['min_salary'],
            max_salary=serializer.validated_data['max_salary'],
            median_salary=serializer.validated_data['median_salary'],
            mean_salary=serializer.validated_data['mean_salary'],
            percentile_25=serializer.validated_data.get('percentile_25'),
            percentile_75=serializer.validated_data.get('percentile_75'),
            currency=serializer.validated_data.get('currency', 'USD'),
            data_points=serializer.validated_data.get('data_points', 0),
            confidence_level=serializer.validated_data.get('confidence_level', 0.95),
            last_updated=serializer.validated_data.get('last_updated'),
            user=self.request.user
        )
        
        if insight:
            return Response(
                SalaryInsightSerializer(insight).data,
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {'error': 'Failed to create salary insight'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def compare_salaries(self, request):
        """Compare salaries across roles and locations"""
        serializer = SalaryComparisonSerializer(data=request.data)
        
        if serializer.is_valid():
            service = MarketInsightsService()
            percentiles = service.calculate_salary_percentiles(
                job_title=serializer.validated_data['job_title'],
                location=serializer.validated_data['location'],
                experience_level=serializer.validated_data.get('experience_level'),
                currency=serializer.validated_data.get('currency', 'USD')
            )
            
            if percentiles:
                return Response(percentiles)
            else:
                return Response(
                    {'error': 'Failed to calculate salary percentiles'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DemandAnalysisViewSet(viewsets.ModelViewSet):
    queryset = DemandAnalysis.objects.all()
    serializer_class = DemandAnalysisSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['job_title', 'job_category', 'location']
    filterset_fields = ['demand_level', 'job_category', 'location', 'competition_level']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return DemandAnalysisCreateSerializer
        return super().get_serializer_class()
    
    def perform_create(self, serializer):
        service = MarketInsightsService()
        analysis = service.create_demand_analysis(
            job_category=serializer.validated_data['job_category'],
            job_title=serializer.validated_data['job_title'],
            location=serializer.validated_data['location'],
            demand_level=serializer.validated_data['demand_level'],
            demand_score=serializer.validated_data.get('demand_score', 0.0),
            job_postings=serializer.validated_data.get('job_postings', 0),
            active_candidates=serializer.validated_data.get('active_candidates', 0),
            hiring_velocity=serializer.validated_data.get('hiring_velocity', 0.0),
            time_to_fill=serializer.validated_data.get('time_to_fill', 0),
            growth_rate=serializer.validated_data.get('growth_rate', 0.0),
            competition_level=serializer.validated_data.get('competition_level', 'medium'),
            analysis_date=serializer.validated_data.get('analysis_date'),
            user=self.request.user
        )
        
        if analysis:
            return Response(
                DemandAnalysisSerializer(analysis).data,
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {'error': 'Failed to create demand analysis'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def analyze_trends(self, request):
        """Analyze demand trends"""
        serializer = DemandAnalysisSerializer(data=request.data)
        
        if serializer.is_valid():
            service = MarketInsightsService()
            trends = service.analyze_demand_trends(
                job_category=serializer.validated_data['job_category'],
                location=serializer.validated_data['location'],
                days=serializer.validated_data.get('time_period', 30)
            )
            
            if trends:
                return Response(trends)
            else:
                return Response(
                    {'error': 'Failed to analyze demand trends'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SkillsAnalysisViewSet(viewsets.ModelViewSet):
    queryset = SkillsAnalysis.objects.all()
    serializer_class = SkillsAnalysisSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['skill_name', 'job_categories']
    filterset_fields = ['skill_type', 'demand_level', 'growth_trend']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return SkillsAnalysisCreateSerializer
        return super().get_serializer_class()
    
    def perform_create(self, serializer):
        service = MarketInsightsService()
        analysis = service.create_skills_analysis(
            skill_name=serializer.validated_data['skill_name'],
            skill_type=serializer.validated_data['skill_type'],
            job_categories=serializer.validated_data['job_categories'],
            demand_level=serializer.validated_data.get('demand_level', 'medium'),
            growth_trend=serializer.validated_data.get('growth_trend', 'stable'),
            salary_impact=serializer.validated_data.get('salary_impact', 0.0),
            market_saturation=serializer.validated_data.get('market_saturation', 0.0),
            learning_time=serializer.validated_data.get('learning_time', 0),
            analysis_date=serializer.validated_data.get('analysis_date'),
            user=self.request.user
        )
        
        if analysis:
            return Response(
                SkillsAnalysisSerializer(analysis).data,
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {'error': 'Failed to create skills analysis'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def analyze_gap(self, request):
        """Analyze skills gap"""
        serializer = SkillsGapAnalysisSerializer(data=request.data)
        
        if serializer.is_valid():
            service = MarketInsightsService()
            gap_analysis = service.analyze_skills_demand(
                skill_names=serializer.validated_data['required_skills'],
                job_category=serializer.validated_data.get('job_category'),
                location=serializer.validated_data.get('location')
            )
            
            if gap_analysis:
                return Response(gap_analysis)
            else:
                return Response(
                    {'error': 'Failed to analyze skills gap'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MarketTrendViewSet(viewsets.ModelViewSet):
    queryset = MarketTrend.objects.all()
    serializer_class = MarketTrendSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'category']
    filterset_fields = ['trend_type', 'category', 'trend_direction']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return MarketTrendCreateSerializer
        return super().get_serializer_class()
    
    def perform_create(self, serializer):
        service = MarketInsightsService()
        trend = service.create_market_trend(
            trend_type=serializer.validated_data['trend_type'],
            category=serializer.validated_data['category'],
            title=serializer.validated_data['title'],
            trend_data=serializer.validated_data['trend_data'],
            trend_direction=serializer.validated_data.get('trend_direction', 'stable'),
            change_percentage=serializer.validated_data.get('change_percentage', 0.0),
            confidence_interval=serializer.validated_data.get('confidence_interval'),
            prediction_period=serializer.validated_data.get('prediction_period', 12),
            user=self.request.user
        )
        
        if trend:
            return Response(
                MarketTrendSerializer(trend).data,
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {'error': 'Failed to create market trend'},
                status=status.HTTP_400_BAD_REQUEST
            )


class CompensationBenchmarkViewSet(viewsets.ModelViewSet):
    queryset = CompensationBenchmark.objects.all()
    serializer_class = CompensationBenchmarkSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['job__title', 'benchmark_category']
    filterset_fields = ['benchmark_type', 'job', 'currency']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CompensationBenchmarkCreateSerializer
        return super().get_serializer_class()
    
    def perform_create(self, serializer):
        service = MarketInsightsService()
        benchmark = service.create_compensation_benchmark(
            job_id=serializer.validated_data['job'].id,
            benchmark_type=serializer.validated_data['benchmark_type'],
            benchmark_category=serializer.validated_data['benchmark_category'],
            base_salary_min=serializer.validated_data['base_salary_min'],
            base_salary_max=serializer.validated_data['base_salary_max'],
            base_salary_median=serializer.validated_data['base_salary_median'],
            total_comp_min=serializer.validated_data['total_comp_min'],
            total_comp_max=serializer.validated_data['total_comp_max'],
            total_comp_median=serializer.validated_data['total_comp_median'],
            bonus_percentage=serializer.validated_data.get('bonus_percentage', 0.0),
            equity_range=serializer.validated_data.get('equity_range'),
            benefits_value=serializer.validated_data.get('benefits_value', 0.0),
            currency=serializer.validated_data.get('currency', 'USD'),
            sample_size=serializer.validated_data.get('sample_size', 0),
            data_quality_score=serializer.validated_data.get('data_quality_score', 0.0),
            last_updated=serializer.validated_data.get('last_updated'),
            user=self.request.user
        )
        
        if benchmark:
            return Response(
                CompensationBenchmarkSerializer(benchmark).data,
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {'error': 'Failed to create compensation benchmark'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def analyze_compensation(self, request):
        """Analyze compensation data"""
        serializer = CompensationAnalysisSerializer(data=request.data)
        
        if serializer.is_valid():
            # Get benchmarks for the job
            benchmarks = CompensationBenchmark.objects.filter(
                job_id=serializer.validated_data['job_id'],
                benchmark_type__in=serializer.validated_data['benchmark_types']
            )
            
            if serializer.validated_data.get('locations'):
                # In real implementation, would filter by location
                pass
            
            if serializer.validated_data.get('experience_levels'):
                # In real implementation, would filter by experience level
                pass
            
            return Response(
                CompensationBenchmarkSerializer(benchmarks, many=True).data
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MarketReportViewSet(viewsets.ModelViewSet):
    queryset = MarketReport.objects.all()
    serializer_class = MarketReportSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']
    filterset_fields = ['report_type', 'format', 'is_public', 'is_scheduled']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return MarketReportCreateSerializer
        return super().get_serializer_class()
    
    def perform_create(self, serializer):
        service = MarketInsightsService()
        report = service.create_market_report(
            name=serializer.validated_data['name'],
            report_type=serializer.validated_data['report_type'],
            description=serializer.validated_data.get('description', ''),
            parameters=serializer.validated_data.get('parameters'),
            data=serializer.validated_data.get('data'),
            insights=serializer.validated_data.get('insights'),
            recommendations=serializer.validated_data.get('recommendations'),
            format=serializer.validated_data.get('format', 'pdf'),
            is_public=serializer.validated_data.get('is_public', False),
            is_scheduled=serializer.validated_data.get('is_scheduled', False),
            schedule_frequency=serializer.validated_data.get('schedule_frequency', ''),
            user=self.request.user
        )
        
        if report:
            return Response(
                MarketReportSerializer(report).data,
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {'error': 'Failed to create market report'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def generate(self, request, pk=None):
        """Generate market report"""
        report = self.get_object()
        
        try:
            # In real implementation, this would generate actual report file
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


class ReportSubscriptionViewSet(viewsets.ModelViewSet):
    queryset = ReportSubscription.objects.all()
    serializer_class = ReportSubscriptionSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = []
    filterset_fields = ['report', 'frequency', 'is_active']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ReportSubscriptionCreateSerializer
        return super().get_serializer_class()
    
    def perform_create(self, serializer):
        service = MarketInsightsService()
        subscription = service.create_report_subscription(
            report_id=serializer.validated_data['report'].id,
            subscriber_ids=serializer.validated_data.get('subscribers', []),
            frequency=serializer.validated_data.get('frequency', 'monthly'),
            next_delivery=serializer.validated_data.get('next_delivery'),
            user=self.request.user
        )
        
        if subscription:
            return Response(
                ReportSubscriptionSerializer(subscription).data,
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {'error': 'Failed to create report subscription'},
                status=status.HTTP_400_BAD_REQUEST
            )


class MarketAlertViewSet(viewsets.ModelViewSet):
    queryset = MarketAlert.objects.all()
    serializer_class = MarketAlertSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'description']
    filterset_fields = ['alert_type', 'severity', 'is_active']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return MarketAlertCreateSerializer
        return super().get_serializer_class()
    
    def perform_create(self, serializer):
        service = MarketInsightsService()
        alert = service.create_market_alert(
            title=serializer.validated_data['title'],
            alert_type=serializer.validated_data['alert_type'],
            description=serializer.validated_data['description'],
            severity=serializer.validated_data.get('severity', 'medium'),
            affected_roles=serializer.validated_data.get('affected_roles'),
            affected_locations=serializer.validated_data.get('affected_locations'),
            trigger_conditions=serializer.validated_data.get('trigger_conditions'),
            action_required=serializer.validated_data.get('action_required', False),
            action_items=serializer.validated_data.get('action_items'),
            expires_at=serializer.validated_data.get('expires_at'),
            user=self.request.user
        )
        
        if alert:
            return Response(
                MarketAlertSerializer(alert).data,
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {'error': 'Failed to create market alert'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        """Archive market alert"""
        alert = self.get_object()
        
        try:
            alert.is_active = False
            alert.save()
            
            return Response({'message': 'Alert archived successfully'})
        except Exception as e:
            return Response(
                {'error': f'Failed to archive alert: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )


# Analytics endpoints
class MarketAnalyticsViewSet(viewsets.ViewSet):
    
    @action(detail=False, methods=['get'])
    def salary_variance(self, request):
        """Get salary variance analysis"""
        job_title = request.query_params.get('job_title')
        location = request.query_params.get('location')
        experience_level = request.query_params.get('experience_level')
        
        if not job_title or not location:
            return Response(
                {'error': 'job_title and location are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        variance = MarketAnalyticsService.calculate_salary_variance(
            job_title=job_title,
            location=location,
            experience_level=experience_level
        )
        
        if variance:
            return Response(variance)
        else:
            return Response(
                {'error': 'Failed to calculate salary variance'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def salary_outliers(self, request):
        """Get salary outliers analysis"""
        job_title = request.query_params.get('job_title')
        location = request.query_params.get('location')
        threshold = float(request.query_params.get('threshold', 2.0))
        
        if not job_title or not location:
            return Response(
                {'error': 'job_title and location are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        outliers = MarketAnalyticsService.identify_salary_outliers(
            job_title=job_title,
            location=location,
            threshold=threshold
        )
        
        if outliers:
            return Response(outliers)
        else:
            return Response(
                {'error': 'Failed to identify salary outliers'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def market_efficiency(self, request):
        """Get market efficiency metrics"""
        job_category = request.query_params.get('job_category')
        location = request.query_params.get('location')
        
        if not job_category or not location:
            return Response(
                {'error': 'job_category and location are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        efficiency = MarketAnalyticsService.calculate_market_efficiency(
            job_category=job_category,
            location=location
        )
        
        if efficiency:
            return Response(efficiency)
        else:
            return Response(
                {'error': 'Failed to calculate market efficiency'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def market_summary(self, request):
        """Generate comprehensive market summary"""
        job_category = request.data.get('job_category')
        location = request.data.get('location')
        
        if not job_category or not location:
            return Response(
                {'error': 'job_category and location are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = MarketInsightsService()
        summary = service.generate_market_summary(
            job_category=job_category,
            location=location
        )
        
        if summary:
            return Response(summary)
        else:
            return Response(
                {'error': 'Failed to generate market summary'},
                status=status.HTTP_400_BAD_REQUEST
            )
