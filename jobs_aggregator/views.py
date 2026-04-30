from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from .services import aggregate_jobs, ARAB_COUNTRIES
from .matcher import rank_jobs_by_match, calculate_match_score

class JobAggregatorView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        query = request.query_params.get('q', 'software developer')
        country = request.query_params.get('country', 'uae')
        include_remote = request.query_params.get('remote', 'true') == 'true'
        page = int(request.query_params.get('page', 1))

        # Collect filters
        filters = {
            'level': request.query_params.get('level'),           # student|graduate|junior|mid|senior|executive
            'job_type': request.query_params.get('job_type'),     # internship|part_time|remote|freelance|full_time
            'salary_min': request.query_params.get('salary_min'),
            'salary_max': request.query_params.get('salary_max'),
            'remote_only': request.query_params.get('remote_only'),
        }

        jobs = aggregate_jobs(query, country, include_remote, page, filters)

        # Count by level for frontend filters UI
        level_counts = {}
        for job in jobs:
            lvl = job.get('experience_level', 'unknown')
            level_counts[lvl] = level_counts.get(lvl, 0) + 1

        # Count by job type
        type_counts = {}
        for job in jobs:
            jt = job.get('job_type_detected', 'unknown')
            type_counts[jt] = type_counts.get(jt, 0) + 1

        return Response({
            'count': len(jobs),
            'country': country,
            'query': query,
            'filters_applied': {k: v for k, v in filters.items() if v},
            'level_counts': level_counts,
            'type_counts': type_counts,
            'jobs': jobs,
        })


class CountriesView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response({
            'countries': [
                {'key': k, 'name': v['name']}
                for k, v in ARAB_COUNTRIES.items()
            ],
            'levels': [
                {'key': 'student', 'label': '🎓 Student / Intern'},
                {'key': 'graduate', 'label': '🎓 Fresh Graduate'},
                {'key': 'junior', 'label': '👨‍💻 Junior (1-3 yrs)'},
                {'key': 'mid', 'label': '💼 Mid Level (3-5 yrs)'},
                {'key': 'senior', 'label': '🚀 Senior (5+ yrs)'},
                {'key': 'executive', 'label': '👔 Executive / Manager'},
            ],
            'job_types': [
                {'key': 'full_time', 'label': '⏰ Full Time'},
                {'key': 'part_time', 'label': '🕐 Part Time'},
                {'key': 'internship', 'label': '🎓 Internship'},
                {'key': 'remote', 'label': '🌍 Remote'},
                {'key': 'freelance', 'label': '💻 Freelance'},
            ],
        })


class JobLevelsStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Return job counts per level for a given query and country."""
        query = request.query_params.get('q', 'developer')
        country = request.query_params.get('country', 'uae')

        all_jobs = aggregate_jobs(query, country, True, 1, None)

        stats = {
            'student': 0, 'graduate': 0, 'junior': 0,
            'mid': 0, 'senior': 0, 'executive': 0
        }
        for job in all_jobs:
            level = job.get('experience_level', 'mid')
            if level in stats:
                stats[level] += 1

        return Response({
            'query': query,
            'country': country,
            'total': len(all_jobs),
            'by_level': stats,
        })

class JobMatchView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Search jobs and rank by match score using user profile."""
        query = request.query_params.get('q', 'developer')
        country = request.query_params.get('country', 'uae')
        page = int(request.query_params.get('page', 1))

        # Get user profile from DB
        user = request.user
        user_profile = {
            'skills': user.skills if hasattr(user, 'skills') else [],
            'experience_level': user.experience_level if hasattr(user, 'experience_level') else 'mid',
            'desired_roles': user.desired_roles if hasattr(user, 'desired_roles') else [],
            'preferred_countries': user.preferred_countries if hasattr(user, 'preferred_countries') else [],
            'prefers_remote': user.prefers_remote if hasattr(user, 'prefers_remote') else False,
        }

        jobs = aggregate_jobs(query, country, True, page, None)
        ranked_jobs = rank_jobs_by_match(jobs, user_profile)

        return Response({
            'count': len(ranked_jobs),
            'user_profile': user_profile,
            'jobs': ranked_jobs,
        })

    def post(self, request):
        """Calculate match score for a specific job with custom profile."""
        job = request.data.get('job', {})
        user_profile = request.data.get('profile', {})

        if not job:
            return Response({'error': 'job is required'}, status=400)

        match = calculate_match_score(job, user_profile)
        return Response(match)