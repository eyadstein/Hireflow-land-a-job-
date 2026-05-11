from django.utils import timezone
from django.db.models import Q, Count, Avg
from datetime import datetime, timedelta
import requests
import json
import logging

from .models import (
    TalentPool, TalentCandidate, TalentSearch, TalentEngagement,
    TalentCampaign, TalentCampaignExecution, TalentInsight,
    TalentSource, TalentSourcingRule, TalentAnalytics
)

logger = logging.getLogger(__name__)


class TalentDiscoveryService:
    
    def __init__(self):
        self.sources = {
            'linkedin': 'https://api.linkedin.com/v2',
            'github': 'https://api.github.com',
            'stackoverflow': 'https://api.stackoverflow.com/2.3',
        }
    
    def create_talent_pool(self, name, pool_type, criteria=None, description='', user=None):
        pool = TalentPool.objects.create(
            name=name,
            description=description,
            pool_type=pool_type,
            criteria=criteria or {},
            created_by=user
        )
        
        return pool
    
    def add_candidate_to_pool(self, pool_id, candidate_data, source='other', source_details=''):
        try:
            pool = TalentPool.objects.get(id=pool_id)
            
            candidate = TalentCandidate.objects.create(
                pool=pool,
                first_name=candidate_data.get('first_name', ''),
                last_name=candidate_data.get('last_name', ''),
                email=candidate_data.get('email', ''),
                phone=candidate_data.get('phone', ''),
                location=candidate_data.get('location', ''),
                country=candidate_data.get('country', ''),
                title=candidate_data.get('title', ''),
                company=candidate_data.get('company', ''),
                industry=candidate_data.get('industry', ''),
                experience_years=candidate_data.get('experience_years', 0),
                skills=candidate_data.get('skills', []),
                education=candidate_data.get('education', []),
                linkedin_url=candidate_data.get('linkedin_url', ''),
                github_url=candidate_data.get('github_url', ''),
                portfolio_url=candidate_data.get('portfolio_url', ''),
                twitter_url=candidate_data.get('twitter_url', ''),
                personal_website=candidate_data.get('personal_website', ''),
                source=source,
                source_details=source_details,
                notes=candidate_data.get('notes', ''),
                tags=candidate_data.get('tags', [])
            )
            
            return candidate
            
        except TalentPool.DoesNotExist:
            return None
    
    def search_candidates(self, query, search_type='keyword', filters=None, limit=50, offset=0):
        queryset = TalentCandidate.objects.select_related('pool')
        
        if search_type == 'keyword':
            queryset = queryset.filter(
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(email__icontains=query) |
                Q(title__icontains=query) |
                Q(company__icontains=query) |
                Q(skills__overlap=[query]) |
                Q(notes__icontains=query)
            )
        
        elif search_type == 'skill':
            queryset = queryset.filter(skills__overlap=[query])
        
        elif search_type == 'location':
            queryset = queryset.filter(
                Q(location__icontains=query) |
                Q(country__icontains=query)
            )
        
        elif search_type == 'company':
            queryset = queryset.filter(company__icontains=query)
        
        elif search_type == 'industry':
            queryset = queryset.filter(industry__icontains=query)
        
        # Apply additional filters
        if filters:
            if filters.get('pool_id'):
                queryset = queryset.filter(pool_id=filters['pool_id'])
            
            if filters.get('experience_min'):
                queryset = queryset.filter(experience_years__gte=filters['experience_min'])
            
            if filters.get('experience_max'):
                queryset = queryset.filter(experience_years__lte=filters['experience_max'])
            
            if filters.get('skills'):
                queryset = queryset.filter(skills__overlap=filters['skills'])
            
            if filters.get('location'):
                queryset = queryset.filter(location__icontains=filters['location'])
            
            if filters.get('status'):
                queryset = queryset.filter(status=filters['status'])
        
        return queryset[offset:offset+limit]
    
    def search_external_sources(self, query, sources=['linkedin'], filters=None):
        candidates = []
        
        for source in sources:
            try:
                source_config = TalentSource.objects.get(source_type=source, is_active=True)
                
                if source == 'linkedin':
                    candidates.extend(self._search_linkedin(query, source_config, filters))
                elif source == 'github':
                    candidates.extend(self._search_github(query, source_config, filters))
                elif source == 'stackoverflow':
                    candidates.extend(self._search_stackoverflow(query, source_config, filters))
                
            except TalentSource.DoesNotExist:
                logger.warning(f"Source {source} not found or inactive")
                continue
            except Exception as e:
                logger.error(f"Error searching {source}: {e}")
                continue
        
        return candidates
    
    def _search_linkedin(self, query, source_config, filters=None):
        # LinkedIn API integration
        try:
            headers = {
                'Authorization': f"Bearer {source_config.api_key}",
                'Content-Type': 'application/json'
            }
            
            params = {
                'keywords': query,
                'count': 50
            }
            
            if filters:
                if filters.get('location'):
                    params['location'] = filters['location']
                if filters.get('experience'):
                    params['experience'] = filters['experience']
            
            response = requests.get(
                f"{source_config.api_endpoint}/people-search",
                headers=headers,
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_linkedin_results(data, source_config)
            
        except Exception as e:
            logger.error(f"LinkedIn search error: {e}")
        
        return []
    
    def _search_github(self, query, source_config, filters=None):
        # GitHub API integration
        try:
            headers = {
                'Authorization': f"token {source_config.api_key}",
                'Accept': 'application/vnd.github.v3+json'
            }
            
            params = {
                'q': query,
                'per_page': 50
            }
            
            if filters:
                if filters.get('location'):
                    params['q'] += f" location:{filters['location']}"
                if filters.get('language'):
                    params['q'] += f" language:{filters['language']}"
            
            response = requests.get(
                f"{source_config.api_endpoint}/search/users",
                headers=headers,
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_github_results(data, source_config)
            
        except Exception as e:
            logger.error(f"GitHub search error: {e}")
        
        return []
    
    def _search_stackoverflow(self, query, source_config, filters=None):
        # Stack Overflow API integration
        try:
            params = {
                'order': 'desc',
                'sort': 'reputation',
                'intitle': query,
                'pagesize': 50
            }
            
            if filters:
                if filters.get('location'):
                    params['location'] = filters['location']
            
            response = requests.get(
                f"{source_config.api_endpoint}/users",
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_stackoverflow_results(data, source_config)
            
        except Exception as e:
            logger.error(f"Stack Overflow search error: {e}")
        
        return []
    
    def _parse_linkedin_results(self, data, source_config):
        candidates = []
        
        for item in data.get('elements', []):
            candidate_data = {
                'first_name': item.get('firstName', ''),
                'last_name': item.get('lastName', ''),
                'title': item.get('headline', ''),
                'company': item.get('companyName', ''),
                'location': item.get('locationName', ''),
                'linkedin_url': item.get('publicProfileUrl', ''),
                'skills': [skill.get('name') for skill in item.get('skills', [])],
                'experience_years': self._calculate_experience(item.get('experience', [])),
                'source': 'linkedin',
                'source_details': f"LinkedIn profile: {item.get('publicProfileUrl', '')}"
            }
            
            candidates.append(candidate_data)
        
        return candidates
    
    def _parse_github_results(self, data, source_config):
        candidates = []
        
        for item in data.get('items', []):
            candidate_data = {
                'first_name': item.get('name', '').split()[0] if item.get('name') else '',
                'last_name': ' '.join(item.get('name', '').split()[1:]) if item.get('name') else '',
                'title': item.get('bio', ''),
                'location': item.get('location', ''),
                'github_url': item.get('html_url', ''),
                'skills': [],  # GitHub doesn't provide skills directly
                'source': 'github',
                'source_details': f"GitHub profile: {item.get('html_url', '')}"
            }
            
            candidates.append(candidate_data)
        
        return candidates
    
    def _parse_stackoverflow_results(self, data, source_config):
        candidates = []
        
        for item in data.get('items', []):
            candidate_data = {
                'first_name': item.get('display_name', '').split()[0] if item.get('display_name') else '',
                'last_name': ' '.join(item.get('display_name', '').split()[1:]) if item.get('display_name') else '',
                'title': '',
                'location': item.get('location', ''),
                'skills': [],  # Extract from tags or reputation
                'source': 'stackoverflow',
                'source_details': f"Stack Overflow profile: {item.get('link', '')}"
            }
            
            candidates.append(candidate_data)
        
        return candidates
    
    def _calculate_experience(self, experience_list):
        total_months = 0
        
        for exp in experience_list:
            start_date = exp.get('startDate')
            end_date = exp.get('endDate', timezone.now().date())
            
            if start_date:
                if isinstance(start_date, str):
                    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                if isinstance(end_date, str):
                    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                
                months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
                total_months += months
        
        return round(total_months / 12, 1)
    
    def engage_candidate(self, candidate_id, engagement_type, subject, message, template_used=None, user=None):
        try:
            candidate = TalentCandidate.objects.get(id=candidate_id)
            
            engagement = TalentEngagement.objects.create(
                candidate=candidate,
                engagement_type=engagement_type,
                subject=subject,
                message=message,
                template_used=template_used or '',
                created_by=user
            )
            
            # Update candidate's last contacted date
            candidate.last_contacted = engagement.sent_at
            candidate.save()
            
            return engagement
            
        except TalentCandidate.DoesNotExist:
            return None
    
    def create_campaign(self, name, campaign_type, target_pools, subject, message_template, user=None):
        campaign = TalentCampaign.objects.create(
            name=name,
            campaign_type=campaign_type,
            subject=subject,
            message_template=message_template,
            created_by=user
        )
        
        campaign.target_pools.set(target_pools)
        
        return campaign
    
    def launch_campaign(self, campaign_id, send_immediately=False, user=None):
        try:
            campaign = TalentCampaign.objects.get(id=campaign_id)
            
            if send_immediately:
                campaign.status = 'active'
                campaign.save()
                
                # Get candidates from target pools
                candidates = TalentCandidate.objects.filter(
                    pool__in=campaign.target_pools.all(),
                    is_active=True
                )
                
                executions = []
                for candidate in candidates:
                    execution = TalentCampaignExecution.objects.create(
                        campaign=campaign,
                        candidate=candidate,
                        personalized_subject=self._personalize_message(
                            campaign.subject, candidate, campaign.personalization_vars
                        ),
                        personalized_message=self._personalize_message(
                            campaign.message_template, candidate, campaign.personalization_vars
                        ),
                        status='pending'
                    )
                    executions.append(execution)
                
                # Send emails/engagements
                self._execute_campaign_executions(executions)
                
                # Update campaign stats
                campaign.total_sent = len(executions)
                campaign.save()
                
                return {
                    'campaign': campaign,
                    'executions_created': len(executions)
                }
            
        except TalentCampaign.DoesNotExist:
            return None
    
    def _personalize_message(self, template, candidate, vars_dict):
        # Simple personalization
        personalized = template
        
        replacements = {
            '{first_name}': candidate.first_name,
            '{last_name}': candidate.last_name,
            '{email}': candidate.email,
            '{title}': candidate.title,
            '{company}': candidate.company,
            '{location}': candidate.location
        }
        
        # Add custom variables
        replacements.update(vars_dict or {})
        
        for key, value in replacements.items():
            personalized = personalized.replace(key, str(value))
        
        return personalized
    
    def _execute_campaign_executions(self, executions):
        for execution in executions:
            try:
                # Send email/message based on campaign type
                if execution.campaign.campaign_type == 'email':
                    self._send_campaign_email(execution)
                elif execution.campaign.campaign_type == 'linkedin':
                    self._send_linkedin_message(execution)
                
                execution.status = 'sent'
                execution.sent_at = timezone.now()
                execution.save()
                
            except Exception as e:
                logger.error(f"Error executing campaign for {execution.id}: {e}")
                execution.status = 'failed'
                execution.save()
    
    def _send_campaign_email(self, execution):
        # Email sending logic
        from django.core.mail import send_mail
        
        try:
            send_mail(
                subject=execution.personalized_subject,
                message=execution.personalized_message,
                from_email='noreply@hireflow.com',
                recipient_list=[execution.candidate.email],
                fail_silently=False
            )
            
            # Create engagement record
            TalentEngagement.objects.create(
                candidate=execution.candidate,
                engagement_type='email',
                subject=execution.personalized_subject,
                message=execution.personalized_message,
                template_used=execution.campaign.name,
                status='sent'
            )
            
        except Exception as e:
            logger.error(f"Failed to send campaign email: {e}")
            raise
    
    def _send_linkedin_message(self, execution):
        # LinkedIn message sending logic
        # This would require LinkedIn API integration
        pass
    
    def generate_insight(self, insight_type, parameters=None):
        if insight_type == 'skill_trend':
            return self._generate_skill_trend_insight(parameters)
        elif insight_type == 'location_demand':
            return self._generate_location_demand_insight(parameters)
        elif insight_type == 'salary_insight':
            return self._generate_salary_insight(parameters)
        elif insight_type == 'competition_analysis':
            return self._generate_competition_analysis(parameters)
        
        return None
    
    def _generate_skill_trend_insight(self, parameters):
        # Analyze skill trends in talent pools
        candidates = TalentCandidate.objects.all()
        
        skill_counts = {}
        for candidate in candidates:
            for skill in candidate.skills:
                skill_counts[skill] = skill_counts.get(skill, 0) + 1
        
        # Sort by frequency
        trending_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        insight = TalentInsight.objects.create(
            insight_type='skill_trend',
            title='Top Trending Skills',
            description='Most in-demand skills based on talent pool analysis',
            data={
                'trending_skills': trending_skills,
                'total_candidates': candidates.count(),
                'analysis_date': timezone.now().isoformat()
            },
            confidence_score=0.85,
            source='talent_pool_analysis'
        )
        
        return insight
    
    def _generate_location_demand_insight(self, parameters):
        # Analyze location demand
        candidates = TalentCandidate.objects.all()
        
        location_counts = {}
        for candidate in candidates:
            if candidate.location:
                location_counts[candidate.location] = location_counts.get(candidate.location, 0) + 1
        
        # Sort by frequency
        top_locations = sorted(location_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        insight = TalentInsight.objects.create(
            insight_type='location_demand',
            title='Top Talent Locations',
            description='Locations with highest talent concentration',
            data={
                'top_locations': top_locations,
                'total_candidates': candidates.count(),
                'analysis_date': timezone.now().isoformat()
            },
            confidence_score=0.90,
            source='talent_pool_analysis'
        )
        
        return insight
    
    def _generate_salary_insight(self, parameters):
        # Analyze salary expectations
        candidates = TalentCandidate.objects.filter(experience_years__gt=0)
        
        experience_groups = {
            '0-2': [],
            '2-5': [],
            '5-10': [],
            '10+': []
        }
        
        for candidate in candidates:
            exp = candidate.experience_years
            if exp <= 2:
                experience_groups['0-2'].append(candidate)
            elif exp <= 5:
                experience_groups['2-5'].append(candidate)
            elif exp <= 10:
                experience_groups['5-10'].append(candidate)
            else:
                experience_groups['10+'].append(candidate)
        
        # Calculate average salary by experience (would need salary data)
        salary_insights = {}
        for group, candidates_list in experience_groups.items():
            # This would require salary data in the model
            salary_insights[group] = {
                'candidate_count': len(candidates_list),
                'avg_experience': sum(c.experience_years for c in candidates_list) / len(candidates_list) if candidates_list else 0
            }
        
        insight = TalentInsight.objects.create(
            insight_type='salary_insight',
            title='Experience-Based Salary Insights',
            description='Salary expectations by experience level',
            data={
                'experience_groups': salary_insights,
                'total_candidates': candidates.count(),
                'analysis_date': timezone.now().isoformat()
            },
            confidence_score=0.75,
            source='talent_pool_analysis'
        )
        
        return insight
    
    def _generate_competition_analysis(self, parameters):
        # Analyze competition for talent
        companies = TalentCandidate.objects.values('company').annotate(
            candidate_count=Count('id')
        ).order_by('-candidate_count')[:20]
        
        insight = TalentInsight.objects.create(
            insight_type='competition_analysis',
            title='Top Companies for Talent',
            description='Companies with most candidates in talent pools',
            data={
                'top_companies': list(companies),
                'analysis_date': timezone.now().isoformat()
            },
            confidence_score=0.95,
            source='talent_pool_analysis'
        )
        
        return insight
    
    def run_sourcing_rules(self):
        rules = TalentSourcingRule.objects.filter(is_active=True)
        
        for rule in rules:
            try:
                if self._should_run_rule(rule):
                    candidates_found = self._execute_sourcing_rule(rule)
                    
                    rule.candidates_found = len(candidates_found)
                    rule.last_run = timezone.now()
                    rule.save()
                    
            except Exception as e:
                logger.error(f"Error running sourcing rule {rule.id}: {e}")
    
    def _should_run_rule(self, rule):
        now = timezone.now()
        
        if rule.run_frequency == 'daily':
            return rule.last_run is None or rule.last_run.date() < now.date()
        elif rule.run_frequency == 'hourly':
            return rule.last_run is None or (now - rule.last_run).total_seconds() >= 3600
        elif rule.run_frequency == 'weekly':
            return rule.last_run is None or (now - rule.last_run).days >= 7
        
        return False
    
    def _execute_sourcing_rule(self, rule):
        conditions = rule.conditions
        actions = rule.actions
        
        # Search candidates based on conditions
        query = conditions.get('query', '')
        search_type = conditions.get('search_type', 'keyword')
        filters = conditions.get('filters', {})
        
        candidates = self.search_candidates(query, search_type, filters)
        
        # Add to pool if action specifies
        if actions.get('add_to_pool'):
            pool_id = actions['add_to_pool']
            candidates_added = 0
            
            for candidate_data in candidates:
                # Convert queryset result to dict format
                candidate_dict = {
                    'first_name': candidate_data.first_name,
                    'last_name': candidate_data.last_name,
                    'email': candidate_data.email,
                    'source': 'sourcing_rule',
                    'source_details': f"Sourcing rule: {rule.name}"
                }
                
                if self.add_candidate_to_pool(pool_id, candidate_dict):
                    candidates_added += 1
            
            rule.candidates_added = candidates_added
        
        return candidates


class TalentAnalyticsService:
    
    @staticmethod
    def get_pool_analytics(pool_id=None, start_date=None, end_date=None):
        queryset = TalentAnalytics.objects.filter(metric_type='pool_size')
        
        if pool_id:
            queryset = queryset.filter(pool_id=pool_id)
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        return queryset.order_by('-date')
    
    @staticmethod
    def get_engagement_analytics(pool_id=None, campaign_id=None, start_date=None, end_date=None):
        queryset = TalentAnalytics.objects.filter(metric_type='engagement_rate')
        
        if pool_id:
            queryset = queryset.filter(pool_id=pool_id)
        if campaign_id:
            queryset = queryset.filter(campaign_id=campaign_id)
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        return queryset.order_by('-date')
    
    @staticmethod
    def calculate_pool_metrics(pool_id, date=None):
        if date is None:
            date = timezone.now().date()
        
        pool = TalentPool.objects.get(id=pool_id)
        
        # Calculate metrics
        total_candidates = pool.candidates.count()
        active_candidates = pool.candidates.filter(is_active=True).count()
        new_candidates = pool.candidates.filter(status='new').count()
        engaged_candidates = TalentEngagement.objects.filter(
            candidate__pool=pool,
            created_at__date=date
        ).count()
        
        # Store analytics
        TalentAnalytics.objects.update_or_create(
            metric_type='pool_size',
            date=date,
            pool=pool,
            defaults={
                'value': total_candidates,
                'metadata': {
                    'active_candidates': active_candidates,
                    'new_candidates': new_candidates,
                    'engaged_candidates': engaged_candidates
                }
            }
        )
        
        return {
            'total_candidates': total_candidates,
            'active_candidates': active_candidates,
            'new_candidates': new_candidates,
            'engaged_candidates': engaged_candidates
        }
