from django.db.models import Q, Avg
from django.utils import timezone
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from .models import CandidateProfile, JobRequirement, CandidateMatch, MatchingAlgorithm


class CandidateMatchingService:
    
    def __init__(self):
        self.default_weights = {
            'skills': 0.35,
            'experience': 0.20,
            'education': 0.15,
            'salary': 0.10,
            'location': 0.10,
            'keywords': 0.10
        }
    
    def calculate_skill_match(self, candidate_skills, required_skills):
        if not required_skills:
            return 100.0
        
        candidate_set = set(skill.lower() for skill in candidate_skills)
        required_set = set(skill.lower() for skill in required_skills)
        
        if not required_set:
            return 100.0
        
        intersection = candidate_set.intersection(required_set)
        match_score = (len(intersection) / len(required_set)) * 100
        
        return min(match_score, 100.0)
    
    def calculate_experience_match(self, candidate_experience, required_experience):
        if required_experience == 0:
            return 100.0
        
        if candidate_experience >= required_experience:
            return 100.0
        
        match_ratio = candidate_experience / required_experience
        return match_ratio * 100
    
    def calculate_education_match(self, candidate_education, required_education):
        education_levels = {
            'high_school': 1,
            'bachelor': 2,
            'master': 3,
            'phd': 4
        }
        
        candidate_level = education_levels.get(candidate_education, 1)
        required_level = education_levels.get(required_education, 1)
        
        if candidate_level >= required_level:
            return 100.0
        
        return (candidate_level / required_level) * 100
    
    def calculate_salary_match(self, candidate_min, candidate_max, job_min, job_max):
        if not job_min or not candidate_max:
            return 50.0
        
        if candidate_min and candidate_min > job_max:
            return 0.0
        
        if candidate_max >= job_min:
            return 100.0
        
        return (candidate_max / job_min) * 100 if job_min > 0 else 0.0
    
    def calculate_location_match(self, candidate_locations, job_locations):
        if not job_locations:
            return 100.0
        
        if not candidate_locations:
            return 0.0
        
        candidate_set = set(loc.lower() for loc in candidate_locations)
        job_set = set(loc.lower() for loc in job_locations)
        
        intersection = candidate_set.intersection(job_set)
        if intersection:
            return 100.0
        
        return 0.0
    
    def calculate_keyword_similarity(self, candidate_text, job_keywords):
        if not candidate_text or not job_keywords:
            return 50.0
        
        try:
            job_text = ' '.join(job_keywords.keys())
            
            vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
            tfidf_matrix = vectorizer.fit_transform([candidate_text, job_text])
            
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return similarity * 100
        except:
            return 50.0
    
    def calculate_overall_match(self, candidate, job_requirement, weights=None):
        if weights is None:
            weights = self.default_weights
        
        skill_score = self.calculate_skill_match(
            candidate.skills, job_requirement.required_skills
        )
        
        experience_score = self.calculate_experience_match(
            candidate.experience_years, job_requirement.experience_required
        )
        
        education_score = self.calculate_education_match(
            candidate.education_level, job_requirement.education_required
        )
        
        salary_score = self.calculate_salary_match(
            candidate.expected_salary_min, candidate.expected_salary_max,
            job_requirement.salary_min, job_requirement.salary_max
        )
        
        location_score = self.calculate_location_match(
            candidate.preferred_locations, job_requirement.locations
        )
        
        keyword_score = self.calculate_keyword_similarity(
            candidate.resume_text, job_requirement.description_weighted_keywords
        )
        
        overall_score = (
            skill_score * weights['skills'] +
            experience_score * weights['experience'] +
            education_score * weights['education'] +
            salary_score * weights['salary'] +
            location_score * weights['location'] +
            keyword_score * weights['keywords']
        )
        
        return {
            'skill_match_score': round(skill_score, 2),
            'experience_match_score': round(experience_score, 2),
            'education_match_score': round(education_score, 2),
            'salary_match_score': round(salary_score, 2),
            'location_match_score': round(location_score, 2),
            'overall_score': round(overall_score, 2),
            'match_reasons': self._generate_match_reasons(
                skill_score, experience_score, education_score, salary_score, location_score
            ),
            'missing_requirements': self._identify_missing_requirements(
                candidate, job_requirement
            )
        }
    
    def _generate_match_reasons(self, skill_score, experience_score, education_score, salary_score, location_score):
        reasons = []
        
        if skill_score >= 80:
            reasons.append("Strong skill match")
        elif skill_score >= 60:
            reasons.append("Good skill match")
        
        if experience_score >= 100:
            reasons.append("Meets experience requirements")
        elif experience_score >= 80:
            reasons.append("Close to experience requirements")
        
        if education_score >= 100:
            reasons.append("Meets education requirements")
        
        if salary_score >= 100:
            reasons.append("Within salary expectations")
        
        if location_score >= 100:
            reasons.append("Preferred location match")
        
        return reasons
    
    def _identify_missing_requirements(self, candidate, job_requirement):
        missing = []
        
        candidate_skills = set(skill.lower() for skill in candidate.skills)
        required_skills = set(skill.lower() for skill in job_requirement.required_skills)
        
        missing_skills = required_skills - candidate_skills
        if missing_skills:
            missing.extend([f"Skill: {skill}" for skill in missing_skills])
        
        if candidate.experience_years < job_requirement.experience_required:
            missing.append(f"Experience: {job_requirement.experience_required - candidate.experience_years:.1f} years")
        
        if candidate.expected_salary_max and job_requirement.salary_min:
            if candidate.expected_salary_max < job_requirement.salary_min:
                missing.append("Salary expectations below range")
        
        return missing
    
    def find_matches_for_job(self, job_id, limit=10, min_score=0.0):
        try:
            job_requirement = JobRequirement.objects.select_related('job').get(job_id=job_id)
        except JobRequirement.DoesNotExist:
            return []
        
        candidates = CandidateProfile.objects.all()
        matches = []
        
        for candidate in candidates:
            match_data = self.calculate_overall_match(candidate, job_requirement)
            
            if match_data['overall_score'] >= min_score:
                match, created = CandidateMatch.objects.update_or_create(
                    candidate=candidate,
                    job=job_requirement.job,
                    defaults=match_data
                )
                
                match.is_recommended = match_data['overall_score'] >= 75
                match.save()
                
                matches.append(match)
        
        matches.sort(key=lambda x: x.overall_score, reverse=True)
        return matches[:limit]
    
    def find_matches_for_candidate(self, candidate_id, limit=10, min_score=0.0, filters=None):
        try:
            candidate = CandidateProfile.objects.get(id=candidate_id)
        except CandidateProfile.DoesNotExist:
            return []
        
        job_requirements = JobRequirement.objects.select_related('job').all()
        
        if filters:
            if filters.get('job_types'):
                job_requirements = job_requirements.filter(job_types__overlap=filters['job_types'])
            if filters.get('locations'):
                job_requirements = job_requirements.filter(locations__overlap=filters['locations'])
            if filters.get('industries'):
                job_requirements = job_requirements.filter(industry__in=filters['industries'])
        
        matches = []
        
        for job_req in job_requirements:
            match_data = self.calculate_overall_match(candidate, job_req)
            
            if match_data['overall_score'] >= min_score:
                match, created = CandidateMatch.objects.update_or_create(
                    candidate=candidate,
                    job=job_req.job,
                    defaults=match_data
                )
                
                match.is_recommended = match_data['overall_score'] >= 75
                match.save()
                
                matches.append(match)
        
        matches.sort(key=lambda x: x.overall_score, reverse=True)
        return matches[:limit]
    
    def update_all_matches_for_candidate(self, candidate_id):
        return self.find_matches_for_candidate(candidate_id, limit=1000, min_score=0.0)
    
    def update_all_matches_for_job(self, job_id):
        return self.find_matches_for_job(job_id, limit=1000, min_score=0.0)
