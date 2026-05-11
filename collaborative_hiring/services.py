from django.utils import timezone
from django.db.models import Q, Count, Avg
from datetime import datetime, timedelta
import logging

from .models import (
    HiringTeam, HiringDecision, InterviewSchedule, CandidateFeedback,
    HiringWorkflow, JobWorkflow, TeamCollaboration, InterviewKit,
    JobInterviewKit, HiringAnalytics, TeamNotification
)

logger = logging.getLogger(__name__)


class CollaborativeHiringService:
    
    def __init__(self):
        pass
    
    def create_hiring_team(self, name, team_type, job_id, member_ids, description='', user=None):
        """Create a new hiring team"""
        try:
            team = HiringTeam.objects.create(
                name=name,
                description=description,
                team_type=team_type,
                job_id=job_id,
                created_by=user
            )
            
            if member_ids:
                team.members.set(member_ids)
            
            return team
            
        except Exception as e:
            logger.error(f"Error creating hiring team: {e}")
            return None
    
    def add_decision(self, application_id, reviewer_id, decision, score=0, comments='', strengths=None, concerns=None, recommendation='', is_final=False, user=None):
        """Add a hiring decision"""
        try:
            decision = HiringDecision.objects.create(
                application_id=application_id,
                reviewer_id=reviewer_id,
                decision=decision,
                score=score,
                comments=comments,
                strengths=strengths or [],
                concerns=concerns or [],
                recommendation=recommendation,
                is_final=is_final,
                created_by=user
            )
            
            return decision
            
        except Exception as e:
            logger.error(f"Error adding hiring decision: {e}")
            return None
    
    def schedule_interview(self, application_id, interview_type, title, description, scheduled_date, duration_minutes=60, location='', meeting_url='', interviewer_ids=None, user=None):
        """Schedule an interview"""
        try:
            interview = InterviewSchedule.objects.create(
                application_id=application_id,
                interview_type=interview_type,
                title=title,
                description=description,
                scheduled_date=scheduled_date,
                duration_minutes=duration_minutes,
                location=location,
                meeting_url=meeting_url,
                created_by=user
            )
            
            if interviewer_ids:
                interview.interviewers.set(interviewer_ids)
            
            return interview
            
        except Exception as e:
            logger.error(f"Error scheduling interview: {e}")
            return None
    
    def add_feedback(self, application_id, reviewer_id, feedback_type, score=None, max_score=10, strengths=None, weaknesses=None, observations='', recommendations='', is_shared_with_candidate=False, is_shared_with_team=True, user=None):
        """Add candidate feedback"""
        try:
            feedback = CandidateFeedback.objects.create(
                application_id=application_id,
                reviewer_id=reviewer_id,
                feedback_type=feedback_type,
                score=score,
                max_score=max_score,
                strengths=strengths or [],
                weaknesses=weaknesses or [],
                observations=observations,
                recommendations=recommendations,
                is_shared_with_candidate=is_shared_with_candidate,
                is_shared_with_team=is_shared_with_team,
                created_by=user
            )
            
            return feedback
            
        except Exception as e:
            logger.error(f"Error adding feedback: {e}")
            return None
    
    def create_workflow(self, name, workflow_type, stages, job_id, is_default=False, is_active=True, description='', user=None):
        """Create a hiring workflow"""
        try:
            workflow = HiringWorkflow.objects.create(
                name=name,
                description=description,
                workflow_type=workflow_type,
                stages=stages,
                is_default=is_default,
                is_active=is_active,
                created_by=user
            )
            
            # Assign to job
            JobWorkflow.objects.create(
                job_id=job_id,
                workflow=workflow,
                current_stage='application_review',
                is_active=True
            )
            
            return workflow
            
        except Exception as e:
            logger.error(f"Error creating workflow: {e}")
            return None
    
    def create_collaboration(self, application_id, collaboration_type, title, message, participant_ids=None, priority='medium', user=None):
        """Create a team collaboration"""
        try:
            collaboration = TeamCollaboration.objects.create(
                application_id=application_id,
                collaboration_type=collaboration_type,
                title=title,
                message=message,
                initiator=user,
                priority=priority
            )
            
            if participant_ids:
                collaboration.participants.set(participant_ids)
            
            return collaboration
            
        except Exception as e:
            logger.error(f"Error creating collaboration: {e}")
            return None
    
    def create_interview_kit(self, name, description, job_category, questions=None, evaluation_criteria=None, scoring_rubric=None, time_allocations=None, resources=None, templates=None, is_public=False, user=None):
        """Create an interview kit"""
        try:
            kit = InterviewKit.objects.create(
                name=name,
                description=description,
                job_category=job_category,
                questions=questions or [],
                evaluation_criteria=evaluation_criteria or {},
                scoring_rubric=scoring_rubric or {},
                time_allocations=time_allocations or {},
                resources=resources or [],
                templates=templates or [],
                is_public=is_public,
                created_by=user
            )
            
            return kit
            
        except Exception as e:
            logger.error(f"Error creating interview kit: {e}")
            return None
    
    def assign_interview_kit(self, job_id, kit_id, is_active=True, user=None):
        """Assign interview kit to job"""
        try:
            assignment = JobInterviewKit.objects.create(
                job_id=job_id,
                interview_kit_id=kit_id,
                is_active=is_active,
                assigned_by=user
            )
            
            return assignment
            
        except Exception as e:
            logger.error(f"Error assigning interview kit: {e}")
            return None
    
    def send_notification(self, team_id, notification_type, title, message, related_object_id=None, related_object_type='', delivery_method='in_app', user=None):
        """Send team notification"""
        try:
            notification = TeamNotification.objects.create(
                team_id=team_id,
                notification_type=notification_type,
                title=title,
                message=message,
                related_object_id=related_object_id,
                related_object_type=related_object_type,
                delivery_method=delivery_method,
                is_sent=True,
                sent_at=timezone.now()
            )
            
            return notification
            
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
            return None
    
    def update_interview_status(self, interview_id, status, feedback=None, rating=None, would_hire=None, internal_notes=None, candidate_notes=None, user=None):
        """Update interview status"""
        try:
            interview = InterviewSchedule.objects.get(id=interview_id)
            
            interview.status = status
            interview.feedback = feedback
            interview.rating = rating
            interview.would_hire = would_hire
            interview.internal_notes = internal_notes
            interview.candidate_notes = candidate_notes
            
            if status == 'completed':
                interview.conducted_at = timezone.now()
            
            interview.save()
            
            return interview
            
        except InterviewSchedule.DoesNotExist:
            logger.error(f"Interview not found: {interview_id}")
            return None
        except Exception as e:
            logger.error(f"Error updating interview: {e}")
            return None
    
    def resolve_collaboration(self, collaboration_id, resolution, resolved_by_id, user=None):
        """Resolve team collaboration"""
        try:
            collaboration = TeamCollaboration.objects.get(id=collaboration_id)
            
            collaboration.status = 'resolved'
            collaboration.resolution = resolution
            collaboration.resolved_by_id = resolved_by_id
            collaboration.resolved_at = timezone.now()
            
            collaboration.save()
            
            return collaboration
            
        except TeamCollaboration.DoesNotExist:
            logger.error(f"Collaboration not found: {collaboration_id}")
            return None
        except Exception as e:
            logger.error(f"Error resolving collaboration: {e}")
            return None
    
    def get_hiring_analytics(self, metric_type=None, start_date=None, end_date=None, job_id=None, team_id=None, workflow_id=None):
        """Get hiring analytics"""
        try:
            queryset = HiringAnalytics.objects.all()
            
            if metric_type:
                queryset = queryset.filter(metric_type=metric_type)
            
            if start_date:
                queryset = queryset.filter(date__gte=start_date)
            
            if end_date:
                queryset = queryset.filter(date__lte=end_date)
            
            if job_id:
                queryset = queryset.filter(job_id=job_id)
            
            if team_id:
                queryset = queryset.filter(team_id=team_id)
            
            if workflow_id:
                queryset = queryset.filter(workflow_id=workflow_id)
            
            return queryset.order_by('-date')
            
        except Exception as e:
            logger.error(f"Error getting analytics: {e}")
            return None


class HiringAnalyticsService:
    
    @staticmethod
    def calculate_time_to_hire(application_id):
        """Calculate time to hire for an application"""
        try:
            from applications.models import Application
            application = Application.objects.get(id=application_id)
            
            # Get application submission date
            application_date = application.applied_at
            
            # Get latest interview completion date
            latest_interview = InterviewSchedule.objects.filter(
                application_id=application_id,
                status='completed'
            ).order_by('-conducted_at').first()
            
            if latest_interview:
                interview_date = latest_interview.conducted_at
                days_to_hire = (interview_date - application_date).days
            else:
                days_to_hire = None
            
            return days_to_hire
            
        except Application.DoesNotExist:
            logger.error(f"Application not found: {application_id}")
            return None
        except Exception as e:
            logger.error(f"Error calculating time to hire: {e}")
            return None
    
    @staticmethod
    def calculate_interview_to_offer_rate(job_id, start_date=None, end_date=None):
        """Calculate interview to offer rate"""
        try:
            # Get completed interviews for the job
            completed_interviews = InterviewSchedule.objects.filter(
                application__job_id=job_id,
                status='completed'
            )
            
            if start_date:
                completed_interviews = completed_interviews.filter(conducted_at__gte=start_date)
            
            if end_date:
                completed_interviews = completed_interviews.filter(conducted_at__lte=end_date)
            
            total_interviews = completed_interviews.count()
            
            # Get offers made
            from applications.models import Application
            offers = Application.objects.filter(
                job_id=job_id,
                offered_at__isnull=False
            )
            
            if start_date:
                offers = offers.filter(offered_at__gte=start_date)
            
            if end_date:
                offers = offers.filter(offered_at__lte=end_date)
            
            total_offers = offers.count()
            
            if total_interviews > 0:
                return (total_offers / total_interviews) * 100
            else:
                return 0
                
        except Exception as e:
            logger.error(f"Error calculating interview to offer rate: {e}")
            return 0
    
    @staticmethod
    def calculate_team_effectiveness(team_id, start_date=None, end_date=None):
        """Calculate team effectiveness metrics"""
        try:
            team = HiringTeam.objects.get(id=team_id)
            
            # Get decisions made by team
            decisions = HiringDecision.objects.filter(
                application__job__hiring_teams=team_id
            )
            
            if start_date:
                decisions = decisions.filter(created_at__gte=start_date)
            
            if end_date:
                decisions = decisions.filter(created_at__lte=end_date)
            
            total_decisions = decisions.count()
            
            # Calculate decision breakdown
            approve_count = decisions.filter(decision='approve').count()
            reject_count = decisions.filter(decision='reject').count()
            maybe_count = decisions.filter(decision='maybe').count()
            
            # Calculate average score
            avg_score = decisions.aggregate(Avg('score'))['score__avg'] or 0
            
            # Calculate time to decision
            from applications.models import Application
            applications_with_decisions = Application.objects.filter(
                id__in=decisions.values_list('application_id'),
                job__hiring_teams=team_id
            )
            
            if start_date:
                applications_with_decisions = applications_with_decisions.filter(applied_at__gte=start_date)
            
            if end_date:
                applications_with_decisions = applications_with_decisions.filter(applied_at__lte=end_date)
            
            total_applications = applications_with_decisions.count()
            
            avg_time_to_decision = 0
            if total_applications > 0:
                # Simplified calculation - in real implementation, this would be more complex
                avg_time_to_decision = 7  # Default to 7 days
            
            return {
                'team_id': team_id,
                'total_decisions': total_decisions,
                'decision_breakdown': {
                    'approve': approve_count,
                    'reject': reject_count,
                    'maybe': maybe_count
                },
                'average_score': avg_score,
                'average_time_to_decision': avg_time_to_decision
            }
            
        except HiringTeam.DoesNotExist:
            logger.error(f"Team not found: {team_id}")
            return None
        except Exception as e:
            logger.error(f"Error calculating team effectiveness: {e}")
            return None
