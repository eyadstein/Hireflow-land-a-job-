import requests
import os
from django.conf import settings
from datetime import datetime, timezone
from .filters import detect_experience_level, detect_job_type, filter_jobs

# ── Arab countries config ─────────────────────────────────────
# adzuna_country: must be one of Adzuna's supported codes.
# All Arab countries map to 'gb' (global/UK endpoint — broadest coverage).
# The country name is appended to the search query so results stay relevant.
ARAB_COUNTRIES = {
    'egypt':   {'jsearch': 'Egypt',        'adzuna': 'gb', 'name': 'Egypt'},
    'uae':     {'jsearch': 'UAE',           'adzuna': 'gb', 'name': 'UAE'},
    'saudi':   {'jsearch': 'Saudi Arabia',  'adzuna': 'gb', 'name': 'Saudi Arabia'},
    'qatar':   {'jsearch': 'Qatar',         'adzuna': 'gb', 'name': 'Qatar'},
    'kuwait':  {'jsearch': 'Kuwait',        'adzuna': 'gb', 'name': 'Kuwait'},
    'jordan':  {'jsearch': 'Jordan',        'adzuna': 'gb', 'name': 'Jordan'},
    'morocco': {'jsearch': 'Morocco',       'adzuna': 'gb', 'name': 'Morocco'},
    'bahrain': {'jsearch': 'Bahrain',       'adzuna': 'gb', 'name': 'Bahrain'},
    'oman':    {'jsearch': 'Oman',          'adzuna': 'gb', 'name': 'Oman'},
    'lebanon': {'jsearch': 'Lebanon',       'adzuna': 'gb', 'name': 'Lebanon'},
    'tunisia': {'jsearch': 'Tunisia',       'adzuna': 'gb', 'name': 'Tunisia'},
    'algeria': {'jsearch': 'Algeria',       'adzuna': 'gb', 'name': 'Algeria'},
}

# ── JSearch API ───────────────────────────────────────────────
def fetch_jsearch(query, country_name, page=1):
    # country_name is a human-readable string e.g. "Egypt", "UAE"
    try:
        res = requests.get(
            'https://jsearch.p.rapidapi.com/search',
            headers={
                'X-RapidAPI-Key': settings.JSEARCH_KEY,
                'X-RapidAPI-Host': 'jsearch.p.rapidapi.com'
            },
            params={
                'query': f'{query} in {country_name}',
                'page': page,
                'num_results': 20,
                'date_posted': 'month',
            },
            timeout=10
        )
        data = res.json()
        jobs = []
        for j in data.get('data', []):
            # Skip expired jobs
            if j.get('job_is_remote') is False and not j.get('job_apply_link'):
                continue
            jobs.append({
                'id': f"jsearch_{j.get('job_id')}",
                'source': 'JSearch',
                'title': j.get('job_title'),
                'company': j.get('employer_name'),
                'location': f"{j.get('job_city', '')}, {j.get('job_country', '')}",
                'description': j.get('job_description', '')[:500],
                'apply_link': j.get('job_apply_link'),
                'salary_min': j.get('job_min_salary'),
                'salary_max': j.get('job_max_salary'),
                'salary_currency': j.get('job_salary_currency', 'USD'),
                'job_type': j.get('job_employment_type'),
                'posted_at': j.get('job_posted_at_datetime_utc'),
                'expires_at': j.get('job_offer_expiration_datetime_utc'),
                'logo': j.get('employer_logo'),
                'is_remote': j.get('job_is_remote', False),
            })
        return jobs
    except Exception as e:
        print(f"JSearch error: {e}")
        return []

# ── Adzuna API ────────────────────────────────────────────────
def fetch_adzuna(query, country_code, page=1, location_hint=''):
    # country_code must be a supported Adzuna code (gb, us, au, etc.)
    # location_hint is appended to the query so results stay geographically relevant
    try:
        what_query = f'{query} {location_hint}'.strip() if location_hint else query
        res = requests.get(
            f'https://api.adzuna.com/v1/api/jobs/{country_code}/search/{page}',
            params={
                'app_id': settings.ADZUNA_APP_ID,
                'app_key': settings.ADZUNA_APP_KEY,
                'what': what_query,
                'results_per_page': 20,
                'sort_by': 'date',
                'content-type': 'application/json',
            },
            timeout=10
        )
        data = res.json()
        jobs = []
        for j in data.get('results', []):
            jobs.append({
                'id': f"adzuna_{j.get('id')}",
                'source': 'Adzuna',
                'title': j.get('title'),
                'company': j.get('company', {}).get('display_name'),
                'location': j.get('location', {}).get('display_name'),
                'description': j.get('description', '')[:500],
                'apply_link': j.get('redirect_url'),
                'salary_min': j.get('salary_min'),
                'salary_max': j.get('salary_max'),
                'salary_currency': 'USD',
                'job_type': j.get('contract_type'),
                'posted_at': j.get('created'),
                'expires_at': None,
                'logo': None,
                'is_remote': False,
            })
        return jobs
    except Exception as e:
        print(f"Adzuna error: {e}")
        return []

# ── Remotive API (remote jobs) ────────────────────────────────
def fetch_remotive(query):
    try:
        res = requests.get(
            'https://remotive.com/api/remote-jobs',
            params={'search': query, 'limit': 20},
            timeout=10
        )
        data = res.json()
        jobs = []
        for j in data.get('jobs', []):
            jobs.append({
                'id': f"remotive_{j.get('id')}",
                'source': 'Remotive',
                'title': j.get('title'),
                'company': j.get('company_name'),
                'location': 'Remote',
                'description': j.get('description', '')[:500],
                'apply_link': j.get('url'),
                'salary_min': None,
                'salary_max': None,
                'salary_currency': 'USD',
                'job_type': j.get('job_type'),
                'posted_at': j.get('publication_date'),
                'expires_at': None,
                'logo': j.get('company_logo'),
                'is_remote': True,
            })
        return jobs
    except Exception as e:
        print(f"Remotive error: {e}")
        return []

# ── The Muse API ──────────────────────────────────────────────
def fetch_themuse(query, page=1):
    try:
        res = requests.get(
            'https://www.themuse.com/api/public/jobs',
            params={
                'query': query,
                'page': page,
                'descending': True,
            },
            timeout=10
        )
        data = res.json()
        jobs = []
        for j in data.get('results', []):
            locations = j.get('locations', [])
            location = locations[0].get('name') if locations else 'Unknown'
            jobs.append({
                'id': f"themuse_{j.get('id')}",
                'source': 'The Muse',
                'title': j.get('name'),
                'company': j.get('company', {}).get('name'),
                'location': location,
                'description': j.get('contents', '')[:500],
                'apply_link': j.get('refs', {}).get('landing_page'),
                'salary_min': None,
                'salary_max': None,
                'salary_currency': 'USD',
                'job_type': j.get('type'),
                'posted_at': j.get('publication_date'),
                'expires_at': None,
                'logo': j.get('company', {}).get('refs', {}).get('landing_page'),
                'is_remote': 'remote' in location.lower(),
            })
        return jobs
    except Exception as e:
        print(f"The Muse error: {e}")
        return []

# ── Main aggregator ───────────────────────────────────────────
def aggregate_jobs(query, country='uae', include_remote=True, page=1, filters=None):
    country_config = ARAB_COUNTRIES.get(country.lower(), ARAB_COUNTRIES['uae'])

    all_jobs = []
    country_name = country_config['name']

    def safe_result(future, source_name):
        try:
            return future.result()
        except Exception as e:
            print(f"[aggregator] {source_name} future raised: {e}")
            return []

    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=8) as executor:
        jsearch_p1 = executor.submit(fetch_jsearch, query, country_name, page)
        jsearch_p2 = executor.submit(fetch_jsearch, query, country_name, page + 1)
        adzuna_p1  = executor.submit(fetch_adzuna,  query, country_config['adzuna'], page,     country_name)
        adzuna_p2  = executor.submit(fetch_adzuna,  query, country_config['adzuna'], page + 1, country_name)
        remotive_future = executor.submit(fetch_remotive, query) if include_remote else None
        themuse_p1 = executor.submit(fetch_themuse, query, page)
        themuse_p2 = executor.submit(fetch_themuse, query, page + 1)

        all_jobs.extend(safe_result(jsearch_p1, 'JSearch p1'))
        all_jobs.extend(safe_result(jsearch_p2, 'JSearch p2'))
        all_jobs.extend(safe_result(adzuna_p1,  'Adzuna p1'))
        all_jobs.extend(safe_result(adzuna_p2,  'Adzuna p2'))
        if remotive_future:
            all_jobs.extend(safe_result(remotive_future, 'Remotive'))
        all_jobs.extend(safe_result(themuse_p1, 'TheMuse p1'))
        all_jobs.extend(safe_result(themuse_p2, 'TheMuse p2'))

    print(f"[aggregator] raw results: {len(all_jobs)} jobs for '{query}' in {country_name}")

    # Remove expired jobs
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)

    def is_valid(job):
        expires = job.get('expires_at')
        if not expires:
            return True
        try:
            exp_date = datetime.fromisoformat(expires.replace('Z', '+00:00'))
            return exp_date > now
        except:
            return True

    all_jobs = [j for j in all_jobs if is_valid(j)]

    # Add experience level and job type detection to each job
    for job in all_jobs:
        job['experience_level'] = detect_experience_level(
            job.get('title', ''),
            job.get('description', '')
        )
        job['job_type_detected'] = detect_job_type(
            job.get('title', ''),
            job.get('description', '')
        )

    # Apply filters
    if filters:
        all_jobs = filter_jobs(all_jobs, filters)

    # Remove duplicates
    seen = set()
    unique_jobs = []
    for job in all_jobs:
        key = f"{job['title']}_{job['company']}".lower()
        if key not in seen:
            seen.add(key)
            unique_jobs.append(job)

    # Sort by posted date
    unique_jobs.sort(key=lambda j: j.get('posted_at') or '', reverse=True)

    return unique_jobs