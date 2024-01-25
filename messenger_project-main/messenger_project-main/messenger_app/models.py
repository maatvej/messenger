from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    first_name = models.CharField(max_length=30, null=True, blank=True)
    last_name = models.CharField(max_length=30, null=True, blank=True)

    def __str__(self):
        return self.user.username


class Chat(models.Model):
    CHAT_TYPES = (
        ('group', 'Group Chat'),
        ('private', 'Private Chat'),
    )

    name = models.CharField(max_length=255)
    type = models.CharField(max_length=10, choices=CHAT_TYPES, default='private')
    members = models.ManyToManyField(UserProfile, related_name='chats')

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"

    def get_chat_display_name(self):
        if self.type == 'group':
            if self.name:
                return self.name
            else:
                return ", ".join([member.user.username for member in self.members.all()])
        elif self.type == 'private':
            members_names = [member.user.username for member in self.members.all()]
            return ', '.join(members_names)
        else:
            return "Неизвестный чат"

    def get_members_display(self):
        return ", ".join([member.user.username for member in self.members.all()])


class Message(models.Model):
    sender = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    recipient = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='recipient_messages', null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        return reverse('user_profile_detail', args=[str(self.id)])

    def __str__(self):
        return self.sender.user.username if self.sender and self.sender.user else "No User"
