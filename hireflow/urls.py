from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/',               admin.site.urls),
    path('api/users/',           include('users.urls')),
    path('api/jobs/',            include('jobs.urls')),
    path('api/applications/',    include('applications.urls')),
    path('api/chat/',            include('chat.urls')),
    path('api/ai/',              include('ai_features.urls')),
    path('api/jobs-aggregator/', include('jobs_aggregator.urls')),
    path('api/candidate-matching/', include('candidate_matching.urls')),
    path('api/communication-hub/', include('communication_hub.urls')),
    path('api/follow-up-system/', include('follow_up_system.urls')),
    path('api/candidate-crm/', include('candidate_crm.urls')),
    path('api/talent-discovery/', include('talent_discovery.urls')),
    path('api/collaborative-hiring/', include('collaborative_hiring.urls')),
    path('api/talent-visualization/', include('talent_visualization.urls')),
    path('api/market-insights/', include('market_insights.urls')),
]