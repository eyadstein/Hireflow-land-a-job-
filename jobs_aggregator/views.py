from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from .services import aggregate_jobs, ARAB_COUNTRIES

class JobAggregatorView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        query = request.query_params.get('q', 'software developer')
        country = request.query_params.get('country', 'uae')
        include_remote = request.query_params.get('remote', 'true') == 'true'
        page = int(request.query_params.get('page', 1))

        jobs = aggregate_jobs(query, country, include_remote, page)

        return Response({
            'count': len(jobs),
            'country': country,
            'query': query,
            'jobs': jobs,
        })

class CountriesView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response({
            'countries': [
                {'key': k, 'name': v['name']}
                for k, v in ARAB_COUNTRIES.items()
            ]
        })