import re

def calculate_match_score(job, user_profile):
    """
    Calculate how well a job matches a user profile.
    Returns a score 0-100 and breakdown.
    """
    score = 0
    breakdown = {}

    job_text = f"{job.get('title', '')} {job.get('description', '')}".lower()

    # ── Skills match (40 points) ──────────────────────────────
    user_skills = [s.lower().strip() for s in user_profile.get('skills', [])]
    if user_skills:
        matched_skills = [s for s in user_skills if s in job_text]
        skills_score = int((len(matched_skills) / len(user_skills)) * 40)
        score += skills_score
        breakdown['skills'] = {
            'score': skills_score,
            'max': 40,
            'matched': matched_skills,
            'missing': [s for s in user_skills if s not in matched_skills],
        }
    else:
        breakdown['skills'] = {'score': 0, 'max': 40, 'matched': [], 'missing': []}

    # ── Experience level match (25 points) ───────────────────
    user_level = user_profile.get('experience_level', '').lower()
    job_level = job.get('experience_level', '').lower()

    level_order = ['student', 'graduate', 'junior', 'mid', 'senior', 'executive']

    if user_level and job_level:
        try:
            user_idx = level_order.index(user_level)
            job_idx = level_order.index(job_level)
            diff = abs(user_idx - job_idx)
            if diff == 0:
                level_score = 25
            elif diff == 1:
                level_score = 15
            elif diff == 2:
                level_score = 5
            else:
                level_score = 0
        except ValueError:
            level_score = 10
    else:
        level_score = 10

    score += level_score
    breakdown['experience_level'] = {
        'score': level_score,
        'max': 25,
        'user_level': user_level,
        'job_level': job_level,
    }

    # ── Job title match (20 points) ───────────────────────────
    desired_roles = [r.lower().strip() for r in user_profile.get('desired_roles', [])]
    job_title = job.get('title', '').lower()

    if desired_roles:
        title_score = 0
        for role in desired_roles:
            if role in job_title or any(word in job_title for word in role.split()):
                title_score = 20
                break
            elif any(word in job_title for word in role.split() if len(word) > 3):
                title_score = max(title_score, 10)
        score += title_score
        breakdown['title'] = {'score': title_score, 'max': 20}
    else:
        breakdown['title'] = {'score': 0, 'max': 20}

    # ── Location match (15 points) ────────────────────────────
    preferred_countries = [c.lower() for c in user_profile.get('preferred_countries', [])]
    job_location = job.get('location', '').lower()
    is_remote = job.get('is_remote', False)
    prefers_remote = user_profile.get('prefers_remote', False)

    if is_remote and prefers_remote:
        location_score = 15
    elif preferred_countries:
        location_score = 15 if any(c in job_location for c in preferred_countries) else 0
    else:
        location_score = 10

    score += location_score
    breakdown['location'] = {
        'score': location_score,
        'max': 15,
        'job_location': job.get('location'),
        'is_remote': is_remote,
    }

    # ── Final label ───────────────────────────────────────────
    if score >= 80:
        label = 'Excellent Match'
        color = '#38a169'
    elif score >= 60:
        label = 'Good Match'
        color = '#3182ce'
    elif score >= 40:
        label = 'Fair Match'
        color = '#d69e2e'
    else:
        label = 'Low Match'
        color = '#e53e3e'

    return {
        'score': min(score, 100),
        'label': label,
        'color': color,
        'breakdown': breakdown,
    }


def rank_jobs_by_match(jobs, user_profile):
    """Add match score to each job and sort by score."""
    for job in jobs:
        match = calculate_match_score(job, user_profile)
        job['match_score'] = match['score']
        job['match_label'] = match['label']
        job['match_color'] = match['color']
        job['match_breakdown'] = match['breakdown']

    jobs.sort(key=lambda j: j['match_score'], reverse=True)
    return jobs