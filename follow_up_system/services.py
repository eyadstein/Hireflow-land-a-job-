from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.db.models import Q, Count, Avg
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
import logging

from .models import (
    FollowUpTemplate, FollowUpRule, FollowUpSchedule, FollowUpHistory,
    FollowUpTrigger, FollowUpAnalytics, FollowUpBlacklist
)

User = get_user_model()

logger = logging.getLogger(__name__)


class FollowUpService:
    
    def __init__(self):
        self.default_from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@hireflow.com')
    
    def create_trigger(self, event_type, candidate, application=None, job=None, event_data=None):
        trigger = FollowUpTrigger.objects.create(
            event_type=event_type,
            application=application,
            candidate=candidate,
            job=job,
            event_data=event_data or {}
        )
        
        # Process trigger immediately
        self.process_trigger(trigger)
        
        return trigger
    
    def process_trigger(self, trigger):
        try:
            # Find matching rules
            matching_rules = self._find_matching_rules(trigger)
            
            schedules_created = 0
            errors = []
            
            for rule in matching_rules:
                try:
                    schedules = self._create_schedules_from_rule(rule, trigger)
                    schedules_created += len(schedules)
                except Exception as e:
                    errors.append(f"Rule {rule.name}: {str(e)}")
                    logger.error(f"Error processing rule {rule.name}: {e}")
            
            # Update trigger
            trigger.processed = True
            trigger.processed_at = timezone.now()
            trigger.schedules_created = schedules_created
            trigger.errors = errors
            trigger.save()
            
            return schedules_created, errors
            
        except Exception as e:
            logger.error(f"Error processing trigger {trigger.id}: {e}")
            return 0, [str(e)]
    
    def _find_matching_rules(self, trigger):
        active_rules = FollowUpRule.objects.filter(
            is_active=True
        ).prefetch_related('templates')
        
        matching_rules = []
        
        for rule in active_rules:
            if self._rule_matches_trigger(rule, trigger):
                matching_rules.append(rule)
        
        return matching_rules
    
    def _rule_matches_trigger(self, rule, trigger):
        # Check date range
        now = timezone.now()
        if rule.start_date and now < rule.start_date:
            return False
        if rule.end_date and now > rule.end_date:
            return False
        
        # Check conditions based on rule type
        conditions = rule.conditions
        
        if rule.condition_type == 'all':
            return True
        
        elif rule.condition_type == 'specific_job':
            if trigger.job and trigger.job.id in conditions.get('job_ids', []):
                return True
        
        elif rule.condition_type == 'job_category':
            if trigger.job and trigger.job.category in conditions.get('categories', []):
                return True
        
        elif rule.condition_type == 'candidate_stage':
            # Check if candidate is in specific stage
            if trigger.application:
                current_stage = trigger.application.status
                if current_stage in conditions.get('stages', []):
                    return True
        
        elif rule.condition_type == 'time_based':
            # Check time-based conditions
            days_since_application = 0
            if trigger.application:
                days_since_application = (timezone.now() - trigger.application.created_at).days
            
            min_days = conditions.get('min_days', 0)
            max_days = conditions.get('max_days', 999)
            
            if min_days <= days_since_application <= max_days:
                return True
        
        elif rule.condition_type == 'custom':
            # Custom conditions logic
            return self._evaluate_custom_conditions(conditions, trigger)
        
        return False
    
    def _evaluate_custom_conditions(self, conditions, trigger):
        # Implement custom condition evaluation logic
        # This can be extended based on specific requirements
        
        for condition in conditions.get('rules', []):
            field = condition.get('field')
            operator = condition.get('operator')
            value = condition.get('value')
            
            if field == 'candidate_experience':
                try:
                    from candidate_matching.models import CandidateProfile
                    profile = CandidateProfile.objects.filter(user=trigger.candidate).first()
                    if profile:
                        experience = profile.experience_years
                        if operator == 'gt' and experience > value:
                            return True
                        elif operator == 'lt' and experience < value:
                            return True
                        elif operator == 'eq' and experience == value:
                            return True
                except:
                    pass
            
            elif field == 'job_salary':
                if trigger.job and trigger.job.salary_min:
                    salary = trigger.job.salary_min
                    if operator == 'gt' and salary > value:
                        return True
                    elif operator == 'lt' and salary < value:
                        return True
                    elif operator == 'eq' and salary == value:
                        return True
        
        return False
    
    def _create_schedules_from_rule(self, rule, trigger):
        schedules = []
        
        for template in rule.templates.filter(is_active=True):
            # Check if candidate is blacklisted
            if self._is_candidate_blacklisted(trigger.candidate, template, rule):
                continue
            
            # Check if template trigger matches
            if template.trigger_type != trigger.event_type and template.trigger_type != 'custom':
                continue
            
            # Check one-time constraint
            if template.is_one_time:
                existing_count = FollowUpSchedule.objects.filter(
                    candidate=trigger.candidate,
                    template=template,
                    status='sent'
                ).count()
                
                if existing_count >= rule.max_sends_per_candidate:
                    continue
            
            # Calculate scheduled time
            scheduled_time = trigger.created_at + timedelta(
                days=template.delay_days,
                hours=template.delay_hours
            )
            
            # Prepare variables
            variables = self._prepare_template_variables(trigger)
            
            # Render subject and content
            subject = self._render_template(template.subject, variables)
            content = self._render_template(template.content, variables)
            
            # Create schedule
            schedule = FollowUpSchedule.objects.create(
                candidate=trigger.candidate,
                application=trigger.application,
                job=trigger.job,
                template=template,
                rule=rule,
                scheduled_at=scheduled_time,
                recipient_email=trigger.candidate.email,
                subject=subject,
                content=content,
                variables_used=variables
            )
            
            schedules.append(schedule)
            
            # Log history
            FollowUpHistory.objects.create(
                schedule=schedule,
                action_type='scheduled',
                details={'trigger_id': trigger.id, 'rule_id': rule.id}
            )
        
        return schedules
    
    def _is_candidate_blacklisted(self, candidate, template=None, rule=None):
        blacklist = FollowUpBlacklist.objects.filter(
            candidate=candidate
        )
        
        if template:
            blacklist = blacklist.filter(Q(template=template) | Q(template__isnull=True))
        
        if rule:
            blacklist = blacklist.filter(Q(rule=rule) | Q(rule__isnull=True))
        
        # Check if any blacklist entry is active
        for entry in blacklist:
            if entry.is_permanent:
                return True
            if entry.expires_at and entry.expires_at > timezone.now():
                return True
        
        return False
    
    def _prepare_template_variables(self, trigger):
        variables = {
            'candidate_name': trigger.candidate.get_full_name(),
            'candidate_email': trigger.candidate.email,
            'candidate_first_name': trigger.candidate.first_name,
            'candidate_last_name': trigger.candidate.last_name,
            'event_type': trigger.event_type,
            'trigger_date': trigger.created_at.strftime('%Y-%m-%d'),
        }
        
        if trigger.job:
            variables.update({
                'job_title': trigger.job.title,
                'job_company': trigger.job.company,
                'job_location': trigger.job.location,
                'job_type': trigger.job.job_type,
            })
        
        if trigger.application:
            variables.update({
                'application_id': trigger.application.id,
                'application_status': trigger.application.status,
                'application_date': trigger.application.created_at.strftime('%Y-%m-%d'),
            })
        
        # Add custom event data
        variables.update(trigger.event_data)
        
        return variables
    
    def _render_template(self, template_content, variables):
        try:
            # Simple variable replacement
            content = template_content
            for key, value in variables.items():
                content = content.replace(f'{{{key}}}', str(value))
            
            return content
        except Exception as e:
            logger.error(f"Error rendering template: {e}")
            return template_content
    
    def send_scheduled_follow_ups(self):
        now = timezone.now()
        
        # Get pending schedules that are due
        due_schedules = FollowUpSchedule.objects.filter(
            status='pending',
            scheduled_at__lte=now
        ).select_related('candidate', 'template', 'rule')
        
        sent_count = 0
        failed_count = 0
        
        for schedule in due_schedules:
            try:
                success = self._send_follow_up_email(schedule)
                
                if success:
                    schedule.status = 'sent'
                    schedule.sent_at = now
                    sent_count += 1
                    
                    # Log success
                    FollowUpHistory.objects.create(
                        schedule=schedule,
                        action_type='sent',
                        details={'sent_at': now.isoformat()}
                    )
                else:
                    schedule.status = 'failed'
                    schedule.attempts += 1
                    failed_count += 1
                    
                    # Log failure
                    FollowUpHistory.objects.create(
                        schedule=schedule,
                        action_type='failed',
                        details={'attempt': schedule.attempts}
                    )
                
                schedule.save()
                
            except Exception as e:
                schedule.status = 'failed'
                schedule.attempts += 1
                schedule.last_error = str(e)
                schedule.save()
                
                failed_count += 1
                logger.error(f"Error sending follow-up {schedule.id}: {e}")
        
        return {
            'sent': sent_count,
            'failed': failed_count,
            'total': len(due_schedules)
        }
    
    def _send_follow_up_email(self, schedule):
        try:
            send_mail(
                subject=schedule.subject,
                message=schedule.content,
                from_email=self.default_from_email,
                recipient_list=[schedule.recipient_email],
                html_message=render_to_string('emails/follow_up.html', {
                    'schedule': schedule,
                    'candidate': schedule.candidate,
                    'content': schedule.content
                })
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send follow-up email: {e}")
            schedule.last_error = str(e)
            return False
    
    def track_email_open(self, schedule_id):
        try:
            schedule = FollowUpSchedule.objects.get(id=schedule_id)
            
            if not schedule.opened_at:
                schedule.opened_at = timezone.now()
                schedule.save()
                
                # Log open event
                FollowUpHistory.objects.create(
                    schedule=schedule,
                    action_type='opened',
                    details={'opened_at': schedule.opened_at.isoformat()}
                )
            
            return True
            
        except FollowUpSchedule.DoesNotExist:
            return False
    
    def track_email_click(self, schedule_id):
        try:
            schedule = FollowUpSchedule.objects.get(id=schedule_id)
            
            if not schedule.clicked_at:
                schedule.clicked_at = timezone.now()
                schedule.save()
                
                # Log click event
                FollowUpHistory.objects.create(
                    schedule=schedule,
                    action_type='clicked',
                    details={'clicked_at': schedule.clicked_at.isoformat()}
                )
            
            return True
            
        except FollowUpSchedule.DoesNotExist:
            return False
    
    def test_template(self, template_id, candidate_id, variables=None):
        try:
            template = FollowUpTemplate.objects.get(id=template_id)
            candidate = User.objects.get(id=candidate_id)
            
            # Prepare test variables
            test_variables = variables or {}
            test_variables.update({
                'candidate_name': candidate.get_full_name(),
                'candidate_email': candidate.email,
                'candidate_first_name': candidate.first_name,
                'candidate_last_name': candidate.last_name,
            })
            
            # Render template
            subject = self._render_template(template.subject, test_variables)
            content = self._render_template(template.content, test_variables)
            
            return {
                'success': True,
                'subject': subject,
                'content': content,
                'variables_used': test_variables
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_analytics(self, start_date=None, end_date=None, template_id=None, rule_id=None):
        queryset = FollowUpAnalytics.objects.all()
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        if template_id:
            queryset = queryset.filter(template_id=template_id)
        if rule_id:
            queryset = queryset.filter(rule_id=rule_id)
        
        return queryset.order_by('-date')
    
    def update_analytics(self, date=None):
        if date is None:
            date = timezone.now().date()
        
        # Get all templates
        templates = FollowUpTemplate.objects.filter(is_active=True)
        
        for template in templates:
            # Calculate metrics for the date
            schedules = FollowUpSchedule.objects.filter(
                template=template,
                created_at__date=date
            )
            
            total_scheduled = schedules.count()
            total_sent = schedules.filter(status='sent').count()
            total_failed = schedules.filter(status='failed').count()
            total_opened = schedules.exclude(opened_at__isnull=True).count()
            total_clicked = schedules.exclude(clicked_at__isnull=True).count()
            total_replied = schedules.exclude(replied_at__isnull=True).count()
            
            # Calculate rates
            open_rate = (total_opened / total_sent * 100) if total_sent > 0 else 0
            click_rate = (total_clicked / total_opened * 100) if total_opened > 0 else 0
            reply_rate = (total_replied / total_opened * 100) if total_opened > 0 else 0
            success_rate = (total_sent / total_scheduled * 100) if total_scheduled > 0 else 0
            
            # Update or create analytics
            analytics, created = FollowUpAnalytics.objects.update_or_create(
                date=date,
                template=template,
                defaults={
                    'total_scheduled': total_scheduled,
                    'total_sent': total_sent,
                    'total_failed': total_failed,
                    'total_opened': total_opened,
                    'total_clicked': total_clicked,
                    'total_replied': total_replied,
                    'open_rate': open_rate,
                    'click_rate': click_rate,
                    'reply_rate': reply_rate,
                    'success_rate': success_rate,
                }
            )


class FollowUpAutomationService:
    
    @staticmethod
    def run_daily_tasks():
        service = FollowUpService()
        
        # Send scheduled follow-ups
        results = service.send_scheduled_follow_ups()
        
        # Update analytics for yesterday
        yesterday = timezone.now().date() - timedelta(days=1)
        service.update_analytics(yesterday)
        
        # Clean up old triggers
        old_triggers = FollowUpTrigger.objects.filter(
            processed=True,
            created_at__lt=timezone.now() - timedelta(days=30)
        )
        old_triggers.delete()
        
        return {
            'follow_ups_sent': results,
            'analytics_updated': True,
            'old_triggers_cleaned': old_triggers.count()
        }
