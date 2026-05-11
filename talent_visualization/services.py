from django.utils import timezone
from django.db.models import Q, Count, Avg, Sum, F
from datetime import datetime, timedelta
import logging

from .models import (
    TalentPool, TalentPoolCandidate, TalentVisualization, TalentAnalytics,
    TalentDashboard, UserDashboard, TalentReport, ReportSchedule, TalentInsight
)

logger = logging.getLogger(__name__)


class TalentVisualizationService:
    
    def __init__(self):
        pass
    
    def create_talent_pool(self, name, pool_type, job_category='', skills=None, experience_levels=None, locations=None, description='', user=None):
        """Create a new talent pool"""
        try:
            pool = TalentPool.objects.create(
                name=name,
                description=description,
                pool_type=pool_type,
                job_category=job_category,
                skills=skills or [],
                experience_levels=experience_levels or [],
                locations=locations or [],
                created_by=user
            )
            
            return pool
            
        except Exception as e:
            logger.error(f"Error creating talent pool: {e}")
            return None
    
    def add_candidate_to_pool(self, pool_id, candidate_id, skills=None, experience_years=None, education_level='', location='', salary_expectation=None, availability='', notes='', user=None):
        """Add candidate to talent pool"""
        try:
            candidate = TalentPoolCandidate.objects.create(
                talent_pool_id=pool_id,
                candidate_id=candidate_id,
                skills=skills or [],
                experience_years=experience_years,
                education_level=education_level,
                location=location,
                salary_expectation=salary_expectation,
                availability=availability,
                notes=notes,
                last_contacted=timezone.now()
            )
            
            return candidate
            
        except Exception as e:
            logger.error(f"Error adding candidate to pool: {e}")
            return None
    
    def create_visualization(self, name, chart_type, description='', configuration=None, data=None, filters=None, is_public=False, user=None):
        """Create a talent visualization"""
        try:
            visualization = TalentVisualization.objects.create(
                name=name,
                chart_type=chart_type,
                description=description,
                configuration=configuration or {},
                data=data or {},
                filters=filters or {},
                is_public=is_public,
                created_by=user
            )
            
            return visualization
            
        except Exception as e:
            logger.error(f"Error creating visualization: {e}")
            return None
    
    def create_dashboard(self, name, dashboard_type, description='', layout=None, widgets=None, filters=None, refresh_interval=300, is_public=False, user=None):
        """Create a talent dashboard"""
        try:
            dashboard = TalentDashboard.objects.create(
                name=name,
                dashboard_type=dashboard_type,
                description=description,
                layout=layout or {},
                widgets=widgets or [],
                filters=filters or {},
                refresh_interval=refresh_interval,
                is_public=is_public,
                created_by=user
            )
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Error creating dashboard: {e}")
            return None
    
    def assign_dashboard_to_user(self, user_id, dashboard_id, is_favorite=False, custom_filters=None, custom_layout=None):
        """Assign dashboard to user"""
        try:
            user_dashboard = UserDashboard.objects.create(
                user_id=user_id,
                dashboard_id=dashboard_id,
                is_favorite=is_favorite,
                custom_filters=custom_filters or {},
                custom_layout=custom_layout or {}
            )
            
            return user_dashboard
            
        except Exception as e:
            logger.error(f"Error assigning dashboard to user: {e}")
            return None
    
    def create_report(self, name, report_type, description='', template=None, data=None, filters=None, format='pdf', is_scheduled=False, schedule_frequency='', user=None):
        """Create a talent report"""
        try:
            report = TalentReport.objects.create(
                name=name,
                report_type=report_type,
                description=description,
                template=template or {},
                data=data or {},
                filters=filters or {},
                format=format,
                is_scheduled=is_scheduled,
                schedule_frequency=schedule_frequency,
                created_by=user
            )
            
            return report
            
        except Exception as e:
            logger.error(f"Error creating report: {e}")
            return None
    
    def schedule_report(self, report_id, recipient_ids, frequency, next_run=None, user=None):
        """Schedule a report"""
        try:
            if not next_run:
                # Set next run based on frequency
                next_run = self._calculate_next_run(frequency)
            
            schedule = ReportSchedule.objects.create(
                report_id=report_id,
                frequency=frequency,
                next_run=next_run,
                created_by=user
            )
            
            schedule.recipients.set(recipient_ids)
            
            return schedule
            
        except Exception as e:
            logger.error(f"Error scheduling report: {e}")
            return None
    
    def create_insight(self, title, insight_type, description, data_points=None, confidence_score=0.0, impact_level='medium', action_items=None, expires_at=None, user=None):
        """Create a talent insight"""
        try:
            insight = TalentInsight.objects.create(
                title=title,
                insight_type=insight_type,
                description=description,
                data_points=data_points or [],
                confidence_score=confidence_score,
                impact_level=impact_level,
                action_items=action_items or [],
                expires_at=expires_at,
                created_by=user
            )
            
            return insight
            
        except Exception as e:
            logger.error(f"Error creating insight: {e}")
            return None
    
    def calculate_pool_metrics(self, pool_id):
        """Calculate metrics for a talent pool"""
        try:
            pool = TalentPool.objects.get(id=pool_id)
            candidates = pool.candidates.all()
            
            # Basic metrics
            total_candidates = candidates.count()
            active_candidates = candidates.filter(status='active').count()
            contacted_candidates = candidates.filter(status='contacted').count()
            interviewing_candidates = candidates.filter(status='interviewing').count()
            offered_candidates = candidates.filter(status='offered').count()
            hired_candidates = candidates.filter(status='hired').count()
            
            # Experience distribution
            experience_data = candidates.aggregate(
                avg_experience=Avg('experience_years'),
                min_experience=F('experience_years'),
                max_experience=F('experience_years')
            )
            
            # Location distribution
            location_counts = candidates.values('location').annotate(count=Count('id'))
            
            # Skills distribution
            all_skills = []
            for candidate in candidates:
                all_skills.extend(candidate.skills or [])
            
            skill_counts = {}
            for skill in all_skills:
                skill_counts[skill] = skill_counts.get(skill, 0) + 1
            
            return {
                'pool_id': pool_id,
                'pool_name': pool.name,
                'total_candidates': total_candidates,
                'active_candidates': active_candidates,
                'contacted_candidates': contacted_candidates,
                'interviewing_candidates': interviewing_candidates,
                'offered_candidates': offered_candidates,
                'hired_candidates': hired_candidates,
                'conversion_rates': {
                    'contact_to_interview': (interviewing_candidates / contacted_candidates * 100) if contacted_candidates > 0 else 0,
                    'interview_to_offer': (offered_candidates / interviewing_candidates * 100) if interviewing_candidates > 0 else 0,
                    'offer_to_hire': (hired_candidates / offered_candidates * 100) if offered_candidates > 0 else 0,
                },
                'experience_metrics': experience_data,
                'location_distribution': list(location_counts),
                'skill_distribution': skill_counts,
                'last_updated': timezone.now()
            }
            
        except TalentPool.DoesNotExist:
            logger.error(f"Talent pool not found: {pool_id}")
            return None
        except Exception as e:
            logger.error(f"Error calculating pool metrics: {e}")
            return None
    
    def generate_funnel_data(self, pool_id=None, job_id=None, start_date=None, end_date=None):
        """Generate hiring funnel data"""
        try:
            queryset = TalentPoolCandidate.objects.all()
            
            if pool_id:
                queryset = queryset.filter(talent_pool_id=pool_id)
            
            if job_id:
                # Filter by applications to specific job
                from applications.models import Application
                job_applications = Application.objects.filter(job_id=job_id)
                candidate_ids = job_applications.values_list('applicant_id', flat=True)
                queryset = queryset.filter(candidate_id__in=candidate_ids)
            
            if start_date:
                queryset = queryset.filter(added_at__gte=start_date)
            
            if end_date:
                queryset = queryset.filter(added_at__lte=end_date)
            
            # Funnel stages
            funnel_data = {
                'active': queryset.filter(status='active').count(),
                'contacted': queryset.filter(status='contacted').count(),
                'screening': queryset.filter(status='screening').count(),
                'interviewing': queryset.filter(status='interviewing').count(),
                'offered': queryset.filter(status='offered').count(),
                'hired': queryset.filter(status='hired').count(),
            }
            
            # Calculate conversion rates
            total_active = funnel_data['active']
            if total_active > 0:
                conversion_rates = {
                    'contacted_rate': (funnel_data['contacted'] / total_active) * 100,
                    'screening_rate': (funnel_data['screening'] / funnel_data['contacted']) * 100 if funnel_data['contacted'] > 0 else 0,
                    'interviewing_rate': (funnel_data['interviewing'] / funnel_data['screening']) * 100 if funnel_data['screening'] > 0 else 0,
                    'offered_rate': (funnel_data['offered'] / funnel_data['interviewing']) * 100 if funnel_data['interviewing'] > 0 else 0,
                    'hired_rate': (funnel_data['hired'] / funnel_data['offered']) * 100 if funnel_data['offered'] > 0 else 0,
                }
            else:
                conversion_rates = {}
            
            return {
                'funnel_data': funnel_data,
                'conversion_rates': conversion_rates,
                'total_candidates': total_active,
                'generated_at': timezone.now()
            }
            
        except Exception as e:
            logger.error(f"Error generating funnel data: {e}")
            return None
    
    def generate_skill_gap_analysis(self, pool_id, required_skills=None):
        """Generate skill gap analysis"""
        try:
            pool = TalentPool.objects.get(id=pool_id)
            candidates = pool.candidates.all()
            
            # Get all skills from candidates
            candidate_skills = []
            for candidate in candidates:
                candidate_skills.extend(candidate.skills or [])
            
            # Count skill frequency
            skill_counts = {}
            for skill in candidate_skills:
                skill_counts[skill] = skill_counts.get(skill, 0) + 1
            
            # Calculate skill gaps if required skills are provided
            skill_gaps = []
            if required_skills:
                for skill in required_skills:
                    count = skill_counts.get(skill, 0)
                    coverage = (count / candidates.count()) * 100 if candidates.count() > 0 else 0
                    skill_gaps.append({
                        'skill': skill,
                        'available_candidates': count,
                        'coverage_percentage': coverage,
                        'gap': 100 - coverage
                    })
            
            return {
                'pool_id': pool_id,
                'total_candidates': candidates.count(),
                'skill_distribution': skill_counts,
                'skill_gaps': skill_gaps,
                'analysis_date': timezone.now()
            }
            
        except TalentPool.DoesNotExist:
            logger.error(f"Talent pool not found: {pool_id}")
            return None
        except Exception as e:
            logger.error(f"Error generating skill gap analysis: {e}")
            return None
    
    def update_candidate_status(self, candidate_id, pool_id, status, notes=''):
        """Update candidate status in talent pool"""
        try:
            candidate = TalentPoolCandidate.objects.get(
                candidate_id=candidate_id,
                talent_pool_id=pool_id
            )
            
            candidate.status = status
            if notes:
                candidate.notes = notes
            
            if status == 'contacted':
                candidate.last_contacted = timezone.now()
            
            candidate.save()
            
            return candidate
            
        except TalentPoolCandidate.DoesNotExist:
            logger.error(f"Candidate not found in pool: {candidate_id}")
            return None
        except Exception as e:
            logger.error(f"Error updating candidate status: {e}")
            return None
    
    def _calculate_next_run(self, frequency):
        """Calculate next run time based on frequency"""
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
            return now + timedelta(days=7)  # Default to weekly


class TalentAnalyticsService:
    
    @staticmethod
    def calculate_pipeline_velocity(pool_id=None, start_date=None, end_date=None):
        """Calculate pipeline velocity metrics"""
        try:
            queryset = TalentPoolCandidate.objects.all()
            
            if pool_id:
                queryset = queryset.filter(talent_pool_id=pool_id)
            
            if start_date:
                queryset = queryset.filter(added_at__gte=start_date)
            
            if end_date:
                queryset = queryset.filter(added_at__lte=end_date)
            
            # Calculate time spent in each stage
            velocity_data = {}
            for candidate in queryset:
                status_history = []  # In real implementation, track status changes
                # Simplified calculation
                if candidate.status in ['active', 'contacted', 'screening', 'interviewing']:
                    days_in_stage = (timezone.now() - candidate.added_at).days
                    velocity_data[candidate.status] = velocity_data.get(candidate.status, [])
                    velocity_data[candidate.status].append(days_in_stage)
            
            # Calculate averages
            avg_velocity = {}
            for stage, days_list in velocity_data.items():
                if days_list:
                    avg_velocity[stage] = sum(days_list) / len(days_list)
                else:
                    avg_velocity[stage] = 0
            
            return {
                'pool_id': pool_id,
                'velocity_data': avg_velocity,
                'total_candidates': queryset.count(),
                'calculated_at': timezone.now()
            }
            
        except Exception as e:
            logger.error(f"Error calculating pipeline velocity: {e}")
            return None
    
    @staticmethod
    def calculate_source_effectiveness(pool_id=None, start_date=None, end_date=None):
        """Calculate source effectiveness metrics"""
        try:
            queryset = TalentPoolCandidate.objects.all()
            
            if pool_id:
                queryset = queryset.filter(talent_pool_id=pool_id)
            
            if start_date:
                queryset = queryset.filter(added_at__gte=start_date)
            
            if end_date:
                queryset = queryset.filter(added_at__lte=end_date)
            
            # Group by talent pool (as source)
            source_data = {}
            for pool in TalentPool.objects.all():
                pool_candidates = queryset.filter(talent_pool=pool)
                hired_candidates = pool_candidates.filter(status='hired')
                
                total = pool_candidates.count()
                hired = hired_candidates.count()
                
                source_data[pool.name] = {
                    'total_candidates': total,
                    'hired_candidates': hired,
                    'hire_rate': (hired / total * 100) if total > 0 else 0,
                    'source_type': pool.pool_type
                }
            
            return {
                'source_effectiveness': source_data,
                'total_sources': len(source_data),
                'calculated_at': timezone.now()
            }
            
        except Exception as e:
            logger.error(f"Error calculating source effectiveness: {e}")
            return None
    
    @staticmethod
    def generate_diversity_metrics(pool_id=None, start_date=None, end_date=None):
        """Generate diversity metrics"""
        try:
            queryset = TalentPoolCandidate.objects.all()
            
            if pool_id:
                queryset = queryset.filter(talent_pool_id=pool_id)
            
            if start_date:
                queryset = queryset.filter(added_at__gte=start_date)
            
            if end_date:
                queryset = queryset.filter(added_at__lte=end_date)
            
            # Simplified diversity metrics (in real implementation, would analyze demographic data)
            diversity_data = {
                'gender_distribution': {},  # Would need gender field
                'ethnicity_distribution': {},  # Would need ethnicity field
                'age_distribution': {},  # Would need age field
                'location_diversity': {},
                'education_diversity': {},
                'experience_diversity': {}
            }
            
            # Location diversity
            location_counts = queryset.values('location').annotate(count=Count('id'))
            for item in location_counts:
                diversity_data['location_diversity'][item['location']] = item['count']
            
            # Education diversity
            education_counts = queryset.values('education_level').annotate(count=Count('id'))
            for item in education_counts:
                diversity_data['education_diversity'][item['education_level']] = item['count']
            
            # Experience diversity
            experience_ranges = {
                '0-2': 0,
                '3-5': 0,
                '6-10': 0,
                '11+': 0
            }
            
            for candidate in queryset:
                exp = candidate.experience_years or 0
                if exp <= 2:
                    experience_ranges['0-2'] += 1
                elif exp <= 5:
                    experience_ranges['3-5'] += 1
                elif exp <= 10:
                    experience_ranges['6-10'] += 1
                else:
                    experience_ranges['11+'] += 1
            
            diversity_data['experience_diversity'] = experience_ranges
            
            return {
                'diversity_metrics': diversity_data,
                'total_candidates': queryset.count(),
                'calculated_at': timezone.now()
            }
            
        except Exception as e:
            logger.error(f"Error generating diversity metrics: {e}")
            return None
