from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def api_root(request):
    return JsonResponse({'status': 'HireFlow API running', 'docs': '/api/users/, /api/jobs/, /api/applications/, /api/ai/'})

urlpatterns = [
    path('', api_root),
    path('admin/',               admin.site.urls),
    path('api/users/',           include('users.urls')),
    path('api/jobs/',            include('jobs.urls')),
    path('api/applications/',    include('applications.urls')),
    path('api/chat/',            include('chat.urls')),
    path('api/ai/',              include('ai_features.urls')),
    path('api/jobs-aggregator/', include('jobs_aggregator.urls')),
]