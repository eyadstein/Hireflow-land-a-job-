# Keywords that indicate experience level
LEVEL_KEYWORDS = {
    'student': [
        'student', 'internship', 'intern', 'undergraduate', 'part-time student',
        'university', 'college', 'fresh', 'no experience required', 'training'
    ],
    'graduate': [
        'fresh graduate', 'entry level', 'graduate', '0-1 years', '0 years',
        'recent graduate', 'new graduate', 'junior graduate', 'no experience'
    ],
    'junior': [
        'junior', '1-2 years', '1-3 years', '2 years experience',
        'less than 3 years', 'early career', 'associate'
    ],
    'mid': [
        'mid', 'middle', '3-5 years', '4 years', '5 years',
        'intermediate', 'experienced', '3+ years', '4+ years'
    ],
    'senior': [
        'senior', '5+ years', '6+ years', '7+ years', '8+ years',
        '5-10 years', 'lead', 'principal', 'staff engineer', 'tech lead'
    ],
    'executive': [
        'executive', 'director', 'head of', 'vp ', 'vice president',
        'chief', 'cto', 'ceo', 'coo', 'manager', '10+ years', 'c-level'
    ],
}

JOB_TYPE_KEYWORDS = {
    'internship': ['intern', 'internship', 'trainee', 'training program'],
    'part_time': ['part time', 'part-time', 'parttime'],
    'remote': ['remote', 'work from home', 'wfh', 'distributed', 'anywhere'],
    'freelance': ['freelance', 'contract', 'consultant', 'self-employed'],
    'full_time': ['full time', 'full-time', 'permanent', 'fulltime'],
}


def detect_experience_level(title='', description=''):
    """Detect experience level from job title and description."""
    text = f"{title} {description}".lower()

    # Check title first (more reliable)
    title_lower = title.lower()

    for level, keywords in LEVEL_KEYWORDS.items():
        for kw in keywords:
            if kw in title_lower:
                return level

    # Then check description
    scores = {level: 0 for level in LEVEL_KEYWORDS}
    for level, keywords in LEVEL_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                scores[level] += 1

    best = max(scores, key=scores.get)
    if scores[best] > 0:
        return best

    return 'mid'  # default


def detect_job_type(title='', description=''):
    """Detect job type from title and description."""
    text = f"{title} {description}".lower()

    for job_type, keywords in JOB_TYPE_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                return job_type

    return 'full_time'  # default


def filter_jobs(jobs, filters):
    """Apply filters to job list."""
    filtered = jobs

    # Filter by experience level
    level = filters.get('level')
    if level and level != 'all':
        filtered = [j for j in filtered if j.get('experience_level') == level]

    # Filter by job type
    job_type = filters.get('job_type')
    if job_type and job_type != 'all':
        filtered = [j for j in filtered if j.get('job_type_detected') == job_type]

    # Filter by salary min
    salary_min = filters.get('salary_min')
    if salary_min:
        try:
            min_val = float(salary_min)
            filtered = [
                j for j in filtered
                if j.get('salary_min') is None or
                (j.get('salary_min') and float(j['salary_min']) >= min_val)
            ]
        except ValueError:
            pass

    # Filter by salary max
    salary_max = filters.get('salary_max')
    if salary_max:
        try:
            max_val = float(salary_max)
            filtered = [
                j for j in filtered
                if j.get('salary_max') is None or
                (j.get('salary_max') and float(j['salary_max']) <= max_val)
            ]
        except ValueError:
            pass

    # Filter by remote only
    remote_only = filters.get('remote_only')
    if remote_only == 'true':
        filtered = [j for j in filtered if j.get('is_remote')]

    return filtered