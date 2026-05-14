from django.urls import path

from .views import MessageListView

urlpatterns = [
    path("<int:user_id>/", MessageListView.as_view(), name="chat_messages"),
]