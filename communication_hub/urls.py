from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MessageViewSet, MessageThreadViewSet, NotificationViewSet,
    NotificationPreferenceViewSet, MessageTemplateViewSet, CommunicationLogViewSet
)

router = DefaultRouter()
router.register(r'messages', MessageViewSet, basename='message')
router.register(r'threads', MessageThreadViewSet, basename='thread')
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'notification-preferences', NotificationPreferenceViewSet, basename='notification-preference')
router.register(r'templates', MessageTemplateViewSet, basename='template')
router.register(r'logs', CommunicationLogViewSet, basename='log')

urlpatterns = [
    path('', include(router.urls)),
]
