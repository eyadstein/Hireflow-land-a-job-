from django.contrib import admin
from django.urls import path, include, re_path
from django.http import JsonResponse
from django.views.generic import TemplateView

def api_root(request):
    return JsonResponse({'status': 'HireFlow API running', 'docs': '/api/users/, /api/jobs/, /api/applications/, /api/ai/'})

urlpatterns = [
    path('admin/',                  admin.site.urls),
    path('api/',                    api_root),
    path('api/users/',              include('users.urls')),
    path('api/jobs/',               include('jobs.urls')),
    path('api/applications/',       include('applications.urls')),
    path('api/chat/',               include('chat.urls')),
    path('api/ai/',                 include('ai_features.urls')),
    path('api/jobs-aggregator/',    include('jobs_aggregator.urls')),
    path('api/candidate-matching/', include('candidate_matching.urls')),
    path('api/candidate-crm/',      include('candidate_crm.urls')),

    # Serve React SPA for every other route
    re_path(r'^.*$', TemplateView.as_view(template_name='index.html')),
]
