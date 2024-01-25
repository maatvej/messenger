# messenger_app/urls.py
from django.urls import path
from .views import (
    UserListView,
    EditProfileView,
    UserProfileDetailView,
    ChatWithUserView,
    ChatListView, SendMessageView, EditMessageView, DeleteMessageView, GroupChatCreateView, GroupChatDetailView,
    SendGroupMessageView,
)

app_name = 'messenger_app'

urlpatterns = [
    path('user-list/', UserListView.as_view(), name='user-list'),
    path('profile/', UserProfileDetailView.as_view(), name='profile'),
    path('chat/<str:username>/', ChatWithUserView.as_view(), name='chat-with-user'),
    path('edit-profile/', EditProfileView.as_view(), name='edit-profile'),
    path('chats/', ChatListView.as_view(), name='chat-list'),
    path('send-message/<str:username>/', SendMessageView.as_view(), name='send-message'),
    path('edit-message/<int:message_id>/', EditMessageView.as_view(), name='edit-message'),
    path('delete-message/<int:message_id>/', DeleteMessageView.as_view(), name='delete-message'),
    path('group-chat-create/', GroupChatCreateView.as_view(), name='group-chat-create'),
    path('group-chats/<int:pk>/', GroupChatDetailView.as_view(), name='group-chat-detail'),
    path('send-group-message/<int:chat_id>/', SendGroupMessageView.as_view(), name='send-group-message'),
]

