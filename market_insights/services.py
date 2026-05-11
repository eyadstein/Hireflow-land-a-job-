from django.utils import timezone
from django.db.models import Q, Count, Avg, Sum, F
from datetime import datetime, timedelta
import logging

from .models import (
    MarketData, SalaryInsight, DemandAnalysis, SkillsAnalysis,
    MarketTrend, CompensationBenchmark, MarketReport, ReportSubscription, MarketAlert
)

logger = logging.getLogger(__name__)


class MarketInsightsService:
    
    def __init__(self):
        pass
    
    def create_market_data(self, data_type, job_category, job_title, location, data_value, industry='', experience_level='', source='', collection_date=None, user=None):
        """Create market data entry"""
        try:
            if not collection_date:
                collection_date = timezone.now().date()
            
            market_data = MarketData.objects.create(
                data_type=data_type,
                job_category=job_category,
                job_title=job_title,
                location=location,
                industry=industry,
                experience_level=experience_level,
                data_value=data_value,
                source=source,
                collection_date=collection_date,
                created_by=user
            )
            
            return market_data
            
        except Exception as e:
            logger.error(f"Error creating market data: {e}")
            return None
    
    def create_salary_insight(self, job_title, job_category, experience_level, location, insight_type, salary_data, min_salary, max_salary, median_salary, mean_salary, percentile_25=None, percentile_75=None, currency='USD', data_points=0, confidence_level=0.95, last_updated=None, user=None):
        """Create salary insight"""
        try:
            if not last_updated:
                last_updated = timezone.now().date()
            
            insight = SalaryInsight.objects.create(
                job_title=job_title,
                job_category=job_category,
                experience_level=experience_level,
                location=location,
                insight_type=insight_type,
                salary_data=salary_data,
                min_salary=min_salary,
                max_salary=max_salary,
                median_salary=median_salary,
                mean_salary=mean_salary,
                percentile_25=percentile_25,
                percentile_75=percentile_75,
                currency=currency,
                data_points=data_points,
                confidence_level=confidence_level,
                last_updated=last_updated,
                created_by=user
            )
            
            return insight
            
        except Exception as e:
            logger.error(f"Error creating salary insight: {e}")
            return None
    
    def create_demand_analysis(self, job_category, job_title, location, demand_level, demand_score=0.0, job_postings=0, active_candidates=0, hiring_velocity=0.0, time_to_fill=0, growth_rate=0.0, competition_level='medium', analysis_date=None, user=None):
        """Create demand analysis"""
        try:
            if not analysis_date:
                analysis_date = timezone.now().date()
            
            analysis = DemandAnalysis.objects.create(
                job_category=job_category,
                job_title=job_title,
                location=location,
                demand_level=demand_level,
                demand_score=demand_score,
                job_postings=job_postings,
                active_candidates=active_candidates,
                hiring_velocity=hiring_velocity,
                time_to_fill=time_to_fill,
                growth_rate=growth_rate,
                competition_level=competition_level,
                analysis_date=analysis_date,
                created_by=user
            )
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error creating demand analysis: {e}")
            return None
    
    def create_skills_analysis(self, skill_name, skill_type, job_categories, demand_level='medium', growth_trend='stable', salary_impact=0.0, market_saturation=0.0, learning_time=0, analysis_date=None, user=None):
        """Create skills analysis"""
        try:
            if not analysis_date:
                analysis_date = timezone.now().date()
            
            analysis = SkillsAnalysis.objects.create(
                skill_name=skill_name,
                skill_type=skill_type,
                job_categories=job_categories,
                demand_level=demand_level,
                growth_trend=growth_trend,
                salary_impact=salary_impact,
                market_saturation=market_saturation,
                learning_time=learning_time,
                analysis_date=analysis_date,
                created_by=user
            )
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error creating skills analysis: {e}")
            return None
    
    def create_market_trend(self, trend_type, category, title, trend_data, trend_direction='stable', change_percentage=0.0, confidence_interval=None, prediction_period=12, user=None):
        """Create market trend"""
        try:
            trend = MarketTrend.objects.create(
                trend_type=trend_type,
                category=category,
                title=title,
                trend_data=trend_data,
                trend_direction=trend_direction,
                change_percentage=change_percentage,
                confidence_interval=confidence_interval or {},
                prediction_period=prediction_period,
                created_by=user
            )
            
            return trend
            
        except Exception as e:
            logger.error(f"Error creating market trend: {e}")
            return None
    
    def create_compensation_benchmark(self, job_id, benchmark_type, benchmark_category, base_salary_min, base_salary_max, base_salary_median, total_comp_min, total_comp_max, total_comp_median, bonus_percentage=0.0, equity_range=None, benefits_value=0.0, currency='USD', sample_size=0, data_quality_score=0.0, last_updated=None, user=None):
        """Create compensation benchmark"""
        try:
            if not last_updated:
                last_updated = timezone.now().date()
            
            benchmark = CompensationBenchmark.objects.create(
                job_id=job_id,
                benchmark_type=benchmark_type,
                benchmark_category=benchmark_category,
                base_salary_min=base_salary_min,
                base_salary_max=base_salary_max,
                base_salary_median=base_salary_median,
                total_comp_min=total_comp_min,
                total_comp_max=total_comp_max,
                total_comp_median=total_comp_median,
                bonus_percentage=bonus_percentage,
                equity_range=equity_range or {},
                benefits_value=benefits_value,
                currency=currency,
                sample_size=sample_size,
                data_quality_score=data_quality_score,
                last_updated=last_updated,
                created_by=user
            )
            
            return benchmark
            
        except Exception as e:
            logger.error(f"Error creating compensation benchmark: {e}")
            return None
    
    def create_market_report(self, name, report_type, description='', parameters=None, data=None, insights=None, recommendations=None, format='pdf', is_public=False, is_scheduled=False, schedule_frequency='', user=None):
        """Create market report"""
        try:
            report = MarketReport.objects.create(
                name=name,
                report_type=report_type,
                description=description,
                parameters=parameters or {},
                data=data or {},
                insights=insights or [],
                recommendations=recommendations or [],
                format=format,
                is_public=is_public,
                is_scheduled=is_scheduled,
                schedule_frequency=schedule_frequency,
                created_by=user
            )
            
            return report
            
        except Exception as e:
            logger.error(f"Error creating market report: {e}")
            return None
    
    def create_report_subscription(self, report_id, subscriber_ids, frequency='monthly', next_delivery=None, user=None):
        """Create report subscription"""
        try:
            if not next_delivery:
                next_delivery = self._calculate_next_delivery(frequency)
            
            subscription = ReportSubscription.objects.create(
                report_id=report_id,
                frequency=frequency,
                next_delivery=next_delivery,
                created_by=user
            )
            
            subscription.subscribers.set(subscriber_ids)
            
            return subscription
            
        except Exception as e:
            logger.error(f"Error creating report subscription: {e}")
            return None
    
    def create_market_alert(self, title, alert_type, description, severity='medium', affected_roles=None, affected_locations=None, trigger_conditions=None, action_required=False, action_items=None, expires_at=None, user=None):
        """Create market alert"""
        try:
            alert = MarketAlert.objects.create(
                title=title,
                alert_type=alert_type,
                description=description,
                severity=severity,
                affected_roles=affected_roles or [],
                affected_locations=affected_locations or [],
                trigger_conditions=trigger_conditions or {},
                action_required=action_required,
                action_items=action_items or [],
                expires_at=expires_at,
                created_by=user
            )
            
            return alert
            
        except Exception as e:
            logger.error(f"Error creating market alert: {e}")
            return None
    
    def calculate_salary_percentiles(self, job_title, location, experience_level=None, currency='USD'):
        """Calculate salary percentiles for a role"""
        try:
            insights = SalaryInsight.objects.filter(
                job_title=job_title,
                location=location,
                currency=currency
            )
            
            if experience_level:
                insights = insights.filter(experience_level=experience_level)
            
            if not insights.exists():
                return None
            
            # Aggregate data
            salary_data = []
            for insight in insights:
                salary_data.extend(insight.salary_data.get('salaries', []))
            
            if not salary_data:
                return None
            
            # Calculate percentiles
            sorted_salaries = sorted(salary_data)
            n = len(sorted_salaries)
            
            if n == 0:
                return None
            
            percentiles = {
                'min': sorted_salaries[0],
                'max': sorted_salaries[-1],
                'median': sorted_salaries[n // 2] if n % 2 == 1 else (sorted_salaries[n // 2 - 1] + sorted_salaries[n // 2]) / 2,
                'percentile_25': sorted_salaries[int(n * 0.25)],
                'percentile_75': sorted_salaries[int(n * 0.75)],
                'mean': sum(sorted_salaries) / n,
                'count': n
            }
            
            return {
                'job_title': job_title,
                'location': location,
                'experience_level': experience_level,
                'currency': currency,
                'percentiles': percentiles,
                'calculated_at': timezone.now()
            }
            
        except Exception as e:
            logger.error(f"Error calculating salary percentiles: {e}")
            return None
    
    def analyze_demand_trends(self, job_category, location, days=30):
        """Analyze demand trends for a job category and location"""
        try:
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=days)
            
            analyses = DemandAnalysis.objects.filter(
                job_category=job_category,
                location=location,
                analysis_date__gte=start_date,
                analysis_date__lte=end_date
            ).order_by('analysis_date')
            
            if not analyses.exists():
                return None
            
            # Calculate trend metrics
            demand_scores = [analysis.demand_score for analysis in analyses]
            job_postings = [analysis.job_postings for analysis in analyses]
            active_candidates = [analysis.active_candidates for analysis in analyses]
            
            # Calculate growth rates
            if len(analyses) >= 2:
                first_analysis = analyses.first()
                last_analysis = analyses.last()
                
                demand_growth = ((last_analysis.demand_score - first_analysis.demand_score) / first_analysis.demand_score * 100) if first_analysis.demand_score > 0 else 0
                postings_growth = ((last_analysis.job_postings - first_analysis.job_postings) / first_analysis.job_postings * 100) if first_analysis.job_postings > 0 else 0
                candidates_growth = ((last_analysis.active_candidates - first_analysis.active_candidates) / first_analysis.active_candidates * 100) if first_analysis.active_candidates > 0 else 0
            else:
                demand_growth = 0
                postings_growth = 0
                candidates_growth = 0
            
            return {
                'job_category': job_category,
                'location': location,
                'time_period': days,
                'data_points': analyses.count(),
                'current_demand_score': analyses.last().demand_score,
                'current_job_postings': analyses.last().job_postings,
                'current_active_candidates': analyses.last().active_candidates,
                'growth_rates': {
                    'demand': demand_growth,
                    'postings': postings_growth,
                    'candidates': candidates_growth
                },
                'trend_data': {
                    'demand_scores': demand_scores,
                    'job_postings': job_postings,
                    'active_candidates': active_candidates
                },
                'analyzed_at': timezone.now()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing demand trends: {e}")
            return None
    
    def analyze_skills_demand(self, skill_names, job_category=None, location=None):
        """Analyze demand for specific skills"""
        try:
            analyses = SkillsAnalysis.objects.filter(
                skill_name__in=skill_names
            )
            
            if job_category:
                analyses = analyses.filter(job_categories__contains=job_category)
            
            if location:
                # In real implementation, would filter by location
                pass
            
            skill_demand = {}
            for skill_name in skill_names:
                skill_analyses = analyses.filter(skill_name=skill_name)
                if skill_analyses.exists():
                    latest_analysis = skill_analyses.latest('analysis_date')
                    skill_demand[skill_name] = {
                        'demand_level': latest_analysis.demand_level,
                        'growth_trend': latest_analysis.growth_trend,
                        'salary_impact': latest_analysis.salary_impact,
                        'market_saturation': latest_analysis.market_saturation,
                        'learning_time': latest_analysis.learning_time,
                        'job_categories': latest_analysis.job_categories
                    }
            
            return {
                'skills': skill_demand,
                'analyzed_at': timezone.now()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing skills demand: {e}")
            return None
    
    def generate_market_summary(self, job_category, location):
        """Generate comprehensive market summary"""
        try:
            # Get latest salary insights
            salary_insights = SalaryInsight.objects.filter(
                job_category=job_category,
                location=location
            ).order_by('-last_updated')
            
            # Get latest demand analysis
            demand_analysis = DemandAnalysis.objects.filter(
                job_category=job_category,
                location=location
            ).order_by('-analysis_date').first()
            
            # Get top skills
            skills_analysis = SkillsAnalysis.objects.filter(
                job_categories__contains=job_category
            ).order_by('-salary_impact')[:10]
            
            # Get market trends
            market_trends = MarketTrend.objects.filter(
                category=job_category
            ).order_by('-created_at')[:5]
            
            summary = {
                'job_category': job_category,
                'location': location,
                'salary_insights': {
                    'average_median': salary_insights.aggregate(Avg('median_salary'))['median_salary__avg'] or 0,
                    'salary_range': {
                        'min': salary_insights.aggregate(Min('min_salary'))['min_salary__min'] or 0,
                        'max': salary_insights.aggregate(Max('max_salary'))['max_salary__max'] or 0
                    },
                    'insight_count': salary_insights.count()
                },
                'demand_analysis': {
                    'current_level': demand_analysis.demand_level if demand_analysis else 'unknown',
                    'demand_score': demand_analysis.demand_score if demand_analysis else 0,
                    'job_postings': demand_analysis.job_postings if demand_analysis else 0,
                    'competition_level': demand_analysis.competition_level if demand_analysis else 'unknown'
                } if demand_analysis else None,
                'top_skills': [
                    {
                        'name': skill.skill_name,
                        'demand_level': skill.demand_level,
                        'salary_impact': skill.salary_impact
                    }
                    for skill in skills_analysis
                ],
                'market_trends': [
                    {
                        'title': trend.title,
                        'trend_type': trend.trend_type,
                        'direction': trend.trend_direction,
                        'change_percentage': trend.change_percentage
                    }
                    for trend in market_trends
                ],
                'generated_at': timezone.now()
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating market summary: {e}")
            return None
    
    def _calculate_next_delivery(self, frequency):
        """Calculate next delivery date based on frequency"""
        now = timezone.now()
        
        if frequency == 'daily':
            return now + timedelta(days=1)
        elif frequency == 'weekly':
            return now + timedelta(weeks=1)
        elif frequency == 'monthly':
            return now + timedelta(days=30)
        elif frequency == 'quarterly':
            return now + timedelta(days=90)
        else:
            return now + timedelta(days=30)  # Default to monthly


class MarketAnalyticsService:
    
    @staticmethod
    def calculate_salary_variance(job_title, location, experience_level=None):
        """Calculate salary variance for a role"""
        try:
            insights = SalaryInsight.objects.filter(
                job_title=job_title,
                location=location
            )
            
            if experience_level:
                insights = insights.filter(experience_level=experience_level)
            
            if not insights.exists():
                return None
            
            # Calculate variance metrics
            salaries = []
            for insight in insights:
                salaries.extend(insight.salary_data.get('salaries', []))
            
            if not salaries:
                return None
            
            import statistics
            variance = statistics.variance(salaries) if len(salaries) > 1 else 0
            std_dev = statistics.stdev(salaries) if len(salaries) > 1 else 0
            
            return {
                'job_title': job_title,
                'location': location,
                'experience_level': experience_level,
                'variance': variance,
                'standard_deviation': std_dev,
                'coefficient_of_variation': (std_dev / statistics.mean(salaries)) * 100 if statistics.mean(salaries) > 0 else 0,
                'sample_size': len(salaries)
            }
            
        except Exception as e:
            logger.error(f"Error calculating salary variance: {e}")
            return None
    
    @staticmethod
    def identify_salary_outliers(job_title, location, threshold=2.0):
        """Identify salary outliers using standard deviation method"""
        try:
            insights = SalaryInsight.objects.filter(
                job_title=job_title,
                location=location
            )
            
            if not insights.exists():
                return None
            
            # Collect all salary data
            all_salaries = []
            for insight in insights:
                all_salaries.extend(insight.salary_data.get('salaries', []))
            
            if len(all_salaries) < 3:
                return None
            
            import statistics
            mean_salary = statistics.mean(all_salaries)
            std_dev = statistics.stdev(all_salaries)
            
            # Identify outliers
            outliers = []
            for salary in all_salaries:
                z_score = abs((salary - mean_salary) / std_dev)
                if z_score > threshold:
                    outliers.append({
                        'salary': salary,
                        'z_score': z_score,
                        'deviation_from_mean': salary - mean_salary,
                        'percentage_deviation': ((salary - mean_salary) / mean_salary) * 100
                    })
            
            return {
                'job_title': job_title,
                'location': location,
                'mean_salary': mean_salary,
                'standard_deviation': std_dev,
                'outlier_threshold': threshold,
                'outliers': outliers,
                'outlier_count': len(outliers),
                'outlier_percentage': (len(outliers) / len(all_salaries)) * 100
            }
            
        except Exception as e:
            logger.error(f"Error identifying salary outliers: {e}")
            return None
    
    @staticmethod
    def calculate_market_efficiency(job_category, location):
        """Calculate market efficiency metrics"""
        try:
            # Get demand analysis
            demand_analyses = DemandAnalysis.objects.filter(
                job_category=job_category,
                location=location
            ).order_by('-analysis_date')
            
            if not demand_analyses.exists():
                return None
            
            latest_demand = demand_analyses.first()
            
            # Get compensation benchmarks
            benchmarks = CompensationBenchmark.objects.filter(
                job__category=job_category
            )
            
            # Calculate efficiency metrics
            efficiency_metrics = {
                'job_category': job_category,
                'location': location,
                'demand_supply_ratio': latest_demand.job_postings / latest_demand.active_candidates if latest_demand.active_candidates > 0 else 0,
                'time_to_fill_efficiency': (30 / latest_demand.time_to_fill) * 100 if latest_demand.time_to_fill > 0 else 0,  # 30 days is baseline
                'hiring_velocity_score': min(latest_demand.hiring_velocity * 10, 100),  # Scale to 0-100
                'competition_intensity': {
                    'low': latest_demand.competition_level == 'low',
                    'medium': latest_demand.competition_level == 'medium',
                    'high': latest_demand.competition_level == 'high'
                },
                'market_health': {
                    'growing': latest_demand.growth_rate > 0,
                    'stable': abs(latest_demand.growth_rate) < 5,
                    'declining': latest_demand.growth_rate < -5
                }
            }
            
            return efficiency_metrics
            
        except Exception as e:
            logger.error(f"Error calculating market efficiency: {e}")
            return None
