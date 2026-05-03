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
    path('api/otp/', include('otp.urls')),
]