from django.urls import path
from .views import MessageListView, SignalView, CallInviteView

urlpatterns = [
    path('<int:user_id>/', MessageListView.as_view()),
    path('signal/<str:call_id>/', SignalView.as_view()),
    path('invite/<int:user_id>/', CallInviteView.as_view()),
]