from django.utils import timezone
from django.db.models import Q, Count, Avg
from datetime import datetime, timedelta
import logging

from .models import (
    CandidateProfile, CandidateInteraction, CandidateTask, CandidateDocument,
    CandidatePipeline, CandidatePipelineStage, CandidateTag, CandidateEmail,
    CandidateActivity, CandidateRelationship
)

logger = logging.getLogger(__name__)


class CandidateCRMService:
    
    def create_candidate_profile(self, user, source='website', source_details='', assigned_to=None):
        profile, created = CandidateProfile.objects.get_or_create(
            user=user,
            defaults={
                'source': source,
                'source_details': source_details,
                'assigned_to': assigned_to,
                'status': 'new'
            }
        )
        
        if created:
            # Log activity
            self._log_activity(
                candidate=profile,
                activity_type='profile_view',
                description='Candidate profile created',
                details={'source': source, 'source_details': source_details}
            )
        
        return profile, created
    
    def update_candidate_status(self, candidate_id, new_status, notes='', user=None):
        try:
            candidate = CandidateProfile.objects.get(id=candidate_id)
            old_status = candidate.status
            
            candidate.status = new_status
            if notes:
                candidate.notes = f"{candidate.notes}\n\n{timezone.now().strftime('%Y-%m-%d')}: {notes}"
            candidate.save()
            
            # Log status change
            self._log_activity(
                candidate=candidate,
                activity_type='status_change',
                description=f'Status changed from {old_status} to {new_status}',
                details={'old_status': old_status, 'new_status': new_status, 'notes': notes},
                user=user
            )
            
            return candidate
            
        except CandidateProfile.DoesNotExist:
            return None
    
    def assign_candidate(self, candidate_id, assigned_to_id, notes='', user=None):
        try:
            candidate = CandidateProfile.objects.get(id=candidate_id)
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            assigned_to = User.objects.get(id=assigned_to_id) if assigned_to_id else None
            old_assigned_to = candidate.assigned_to
            
            candidate.assigned_to = assigned_to
            candidate.save()
            
            # Log assignment
            self._log_activity(
                candidate=candidate,
                activity_type='profile_view',
                description=f'Assigned to {assigned_to.get_full_name() if assigned_to else "Unassigned"}',
                details={
                    'old_assigned_to': old_assigned_to.id if old_assigned_to else None,
                    'new_assigned_to': assigned_to.id if assigned_to else None,
                    'notes': notes
                },
                user=user
            )
            
            return candidate
            
        except (CandidateProfile.DoesNotExist, User.DoesNotExist):
            return None
    
    def add_interaction(self, candidate_id, interaction_type, title, description,
                     date=None, duration_minutes=None, location='', attendees=None,
                     outcome='', next_steps='', user=None):
        try:
            candidate = CandidateProfile.objects.get(id=candidate_id)
            
            interaction = CandidateInteraction.objects.create(
                candidate=candidate,
                interaction_type=interaction_type,
                title=title,
                description=description,
                date=date or timezone.now(),
                duration_minutes=duration_minutes,
                location=location,
                attendees=attendees or [],
                outcome=outcome,
                next_steps=next_steps,
                created_by=user
            )
            
            # Update last contacted
            candidate.last_contacted = interaction.date
            candidate.save()
            
            # Log activity
            self._log_activity(
                candidate=candidate,
                activity_type=interaction_type,
                description=f'{interaction_type}: {title}',
                details={'interaction_id': interaction.id},
                user=user
            )
            
            return interaction
            
        except CandidateProfile.DoesNotExist:
            return None
    
    def create_task(self, candidate_id, title, description, priority='medium',
                   due_date=None, assigned_to=None, user=None):
        try:
            candidate = CandidateProfile.objects.get(id=candidate_id)
            
            task = CandidateTask.objects.create(
                candidate=candidate,
                title=title,
                description=description,
                priority=priority,
                due_date=due_date,
                assigned_to=assigned_to,
                created_by=user
            )
            
            # Log activity
            self._log_activity(
                candidate=candidate,
                activity_type='task_completed',
                description=f'Task created: {title}',
                details={'task_id': task.id, 'priority': priority},
                user=user
            )
            
            return task
            
        except CandidateProfile.DoesNotExist:
            return None
    
    def complete_task(self, task_id, user=None):
        try:
            task = CandidateTask.objects.get(id=task_id)
            task.status = 'completed'
            task.completed_date = timezone.now()
            task.save()
            
            # Log activity
            self._log_activity(
                candidate=task.candidate,
                activity_type='task_completed',
                description=f'Task completed: {task.title}',
                details={'task_id': task.id},
                user=user
            )
            
            return task
            
        except CandidateTask.DoesNotExist:
            return None
    
    def upload_document(self, candidate_id, document_type, title, file,
                      description='', is_public=False, user=None):
        try:
            candidate = CandidateProfile.objects.get(id=candidate_id)
            
            document = CandidateDocument.objects.create(
                candidate=candidate,
                document_type=document_type,
                title=title,
                file=file,
                file_size=file.size if hasattr(file, 'size') else 0,
                file_type=file.content_type if hasattr(file, 'content_type') else '',
                description=description,
                is_public=is_public,
                uploaded_by=user
            )
            
            # Log activity
            self._log_activity(
                candidate=candidate,
                activity_type='document_download',
                description=f'Document uploaded: {title}',
                details={
                    'document_id': document.id,
                    'document_type': document_type,
                    'file_size': document.file_size
                },
                user=user
            )
            
            return document
            
        except CandidateProfile.DoesNotExist:
            return None
    
    def add_candidate_to_pipeline(self, candidate_id, pipeline_id, stage='sourcing',
                                notes='', user=None):
        try:
            candidate = CandidateProfile.objects.get(id=candidate_id)
            pipeline = CandidatePipeline.objects.get(id=pipeline_id)
            
            # Remove from existing pipeline stage if exists
            CandidatePipelineStage.objects.filter(
                candidate=candidate,
                pipeline=pipeline
            ).update(exited_at=timezone.now())
            
            # Add to new stage
            stage_obj = CandidatePipelineStage.objects.create(
                candidate=candidate,
                pipeline=pipeline,
                stage=stage,
                notes=notes,
                moved_by=user
            )
            
            # Log activity
            self._log_activity(
                candidate=candidate,
                activity_type='status_change',
                description=f'Added to pipeline: {pipeline.name} - {stage}',
                details={
                    'pipeline_id': pipeline.id,
                    'stage': stage,
                    'pipeline_stage_id': stage_obj.id
                },
                user=user
            )
            
            return stage_obj
            
        except (CandidateProfile.DoesNotExist, CandidatePipeline.DoesNotExist):
            return None
    
    def move_candidate_in_pipeline(self, candidate_id, pipeline_id, new_stage,
                                notes='', user=None):
        try:
            candidate = CandidateProfile.objects.get(id=candidate_id)
            pipeline = CandidatePipeline.objects.get(id=pipeline_id)
            
            # Get current stage
            current_stage = CandidatePipelineStage.objects.filter(
                candidate=candidate,
                pipeline=pipeline,
                exited_at__isnull=True
            ).first()
            
            if current_stage:
                # Exit current stage
                current_stage.exited_at = timezone.now()
                current_stage.save()
                
                # Create new stage
                new_stage_obj = CandidatePipelineStage.objects.create(
                    candidate=candidate,
                    pipeline=pipeline,
                    stage=new_stage,
                    stage_order=current_stage.stage_order + 1,
                    notes=notes,
                    moved_by=user
                )
                
                # Log activity
                self._log_activity(
                    candidate=candidate,
                    activity_type='status_change',
                    description=f'Moved in pipeline: {current_stage.stage} → {new_stage}',
                    details={
                        'pipeline_id': pipeline.id,
                        'old_stage': current_stage.stage,
                        'new_stage': new_stage,
                        'pipeline_stage_id': new_stage_obj.id
                    },
                    user=user
                )
                
                return new_stage_obj
            
            return None
            
        except (CandidateProfile.DoesNotExist, CandidatePipeline.DoesNotExist):
            return None
    
    def get_candidate_summary(self, candidate_id):
        try:
            candidate = CandidateProfile.objects.get(id=candidate_id)
            
            # Get statistics
            interactions_count = candidate.interactions.count()
            tasks_count = candidate.tasks.count()
            documents_count = candidate.documents.count()
            emails_count = candidate.emails.count()
            
            # Get recent activity
            recent_activities = candidate.activities.order_by('-created_at')[:5]
            
            # Get current pipeline stages
            pipeline_stages = candidate.pipeline_stages.filter(exited_at__isnull=True)
            
            # Get pending tasks
            pending_tasks = candidate.tasks.filter(status='pending').order_by('due_date')
            
            return {
                'candidate': candidate,
                'statistics': {
                    'interactions_count': interactions_count,
                    'tasks_count': tasks_count,
                    'documents_count': documents_count,
                    'emails_count': emails_count,
                    'pending_tasks_count': pending_tasks.count()
                },
                'recent_activities': recent_activities,
                'pipeline_stages': pipeline_stages,
                'pending_tasks': pending_tasks
            }
            
        except CandidateProfile.DoesNotExist:
            return None
    
    def search_candidates(self, query=None, status=None, assigned_to=None, tags=None,
                        source=None, rating_min=None, rating_max=None,
                        created_after=None, created_before=None):
        queryset = CandidateProfile.objects.select_related('user', 'assigned_to')
        
        if query:
            queryset = queryset.filter(
                Q(user__first_name__icontains=query) |
                Q(user__last_name__icontains=query) |
                Q(user__email__icontains=query) |
                Q(notes__icontains=query)
            )
        
        if status:
            queryset = queryset.filter(status=status)
        
        if assigned_to:
            queryset = queryset.filter(assigned_to_id=assigned_to)
        
        if tags:
            queryset = queryset.filter(tags__overlap=tags)
        
        if source:
            queryset = queryset.filter(source=source)
        
        if rating_min is not None:
            queryset = queryset.filter(rating__gte=rating_min)
        
        if rating_max is not None:
            queryset = queryset.filter(rating__lte=rating_max)
        
        if created_after:
            queryset = queryset.filter(created_at__gte=created_after)
        
        if created_before:
            queryset = queryset.filter(created_at__lte=created_before)
        
        return queryset.order_by('-created_at')
    
    def get_due_tasks(self, user=None, days_ahead=7):
        queryset = CandidateTask.objects.filter(
            status__in=['pending', 'in_progress']
        ).select_related('candidate', 'assigned_to')
        
        if user:
            queryset = queryset.filter(assigned_to=user)
        
        due_date = timezone.now() + timedelta(days=days_ahead)
        queryset = queryset.filter(due_date__lte=due_date)
        
        return queryset.order_by('due_date', 'priority')
    
    def get_pipeline_statistics(self, pipeline_id):
        try:
            pipeline = CandidatePipeline.objects.get(id=pipeline_id)
            
            stages = {}
            for stage_name in pipeline.stages:
                stages[stage_name] = CandidatePipelineStage.objects.filter(
                    pipeline=pipeline,
                    stage=stage_name,
                    exited_at__isnull=True
                ).count()
            
            return {
                'pipeline': pipeline,
                'stages': stages,
                'total_candidates': sum(stages.values())
            }
            
        except CandidatePipeline.DoesNotExist:
            return None
    
    def _log_activity(self, candidate, activity_type, description, details=None, user=None):
        CandidateActivity.objects.create(
            candidate=candidate,
            activity_type=activity_type,
            description=description,
            details=details or {},
            user=user,
            ip_address=getattr(user, 'ip_address', None) if user else None
        )


class CandidateAnalyticsService:
    
    @staticmethod
    def get_candidate_metrics(start_date=None, end_date=None):
        queryset = CandidateProfile.objects.all()
        
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)
        
        # Basic metrics
        total_candidates = queryset.count()
        active_candidates = queryset.filter(is_active=True).count()
        
        # Status distribution
        status_distribution = dict(
            queryset.values('status').annotate(count=Count('id')).values_list('status', 'count')
        )
        
        # Source distribution
        source_distribution = dict(
            queryset.values('source').annotate(count=Count('id')).values_list('source', 'count')
        )
        
        # Average rating
        avg_rating = queryset.aggregate(avg=Avg('rating'))['avg'] or 0
        
        # New candidates per month
        new_candidates_per_month = dict(
            queryset.extra(
                {'month': "strftime('%%Y-%%m', created_at)"}
            ).values('month').annotate(count=Count('id')).values_list('month', 'count')
        )
        
        return {
            'total_candidates': total_candidates,
            'active_candidates': active_candidates,
            'status_distribution': status_distribution,
            'source_distribution': source_distribution,
            'average_rating': round(avg_rating, 2),
            'new_candidates_per_month': new_candidates_per_month
        }
    
    @staticmethod
    def get_interaction_metrics(start_date=None, end_date=None):
        queryset = CandidateInteraction.objects.all()
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        # Total interactions
        total_interactions = queryset.count()
        
        # Interaction type distribution
        type_distribution = dict(
            queryset.values('interaction_type').annotate(count=Count('id')).values_list('interaction_type', 'count')
        )
        
        # Interactions per month
        interactions_per_month = dict(
            queryset.extra(
                {'month': "strftime('%%Y-%%m', date)"}
            ).values('month').annotate(count=Count('id')).values_list('month', 'count')
        )
        
        return {
            'total_interactions': total_interactions,
            'type_distribution': type_distribution,
            'interactions_per_month': interactions_per_month
        }
    
    @staticmethod
    def get_pipeline_metrics(pipeline_id=None):
        if pipeline_id:
            pipeline = CandidatePipeline.objects.get(id=pipeline_id)
            queryset = CandidatePipelineStage.objects.filter(pipeline=pipeline)
        else:
            queryset = CandidatePipelineStage.objects.all()
        
        # Stage distribution
        stage_distribution = dict(
            queryset.filter(exited_at__isnull=True)
            .values('stage').annotate(count=Count('id'))
            .values_list('stage', 'count')
        )
        
        # Average time in stages
        avg_time_in_stages = {}
        for stage in queryset.filter(exited_at__isnull=False).values('stage').distinct():
            stage_name = stage['stage']
            stage_data = queryset.filter(stage=stage_name, exited_at__isnull=False)
            
            if stage_data.exists():
                avg_duration = stage_data.aggregate(
                    avg_duration=Avg('exited_at') - Avg('entered_at')
                )['avg_duration']
                
                if avg_duration:
                    avg_time_in_stages[stage_name] = avg_duration.total_seconds() / 3600  # hours
        
        return {
            'stage_distribution': stage_distribution,
            'average_time_in_stages': avg_time_in_stages
        }
