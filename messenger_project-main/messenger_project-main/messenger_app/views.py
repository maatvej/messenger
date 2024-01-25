from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView, UpdateView, TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import UserProfile, Chat, Message
from .forms import UserProfileForm, MessageForm, GroupChatCreationForm
from django.contrib.auth.models import User
from django.urls import reverse, reverse_lazy
from django.contrib import messages

from .serializers import MessageSerializer


# ПРОФИЛЬ

# Просмотр профиля

class UserProfileDetailView(View):
    template_name = 'profile_detail.html'

    def get(self, request, *args, **kwargs):
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        user_form = UserProfileForm(instance=user_profile)
        return render(request, self.template_name, {'user_profile': user_profile, 'user_form': user_form})


# Редактирование профиля

@method_decorator(login_required, name='dispatch')
class EditProfileView(UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'edit_profile.html'
    success_url = '/api/profile'

    def get_object(self, queryset=None):
        return self.request.user.userprofile

    def form_valid(self, form):
        response = super().form_valid(form)
        user_profile = form.save(commit=False)
        user_profile.user.first_name = form.cleaned_data['first_name']
        user_profile.user.last_name = form.cleaned_data['last_name']
        user_profile.user.save()
        messages.success(self.request, 'Профиль успешно обновлен.')
        return response


# СООБЩЕНИЯ

# Отправка сообщения

class SendMessageView(View):
    template_name = 'send_message.html'

    def get_or_create_private_chat(self, sender, recipient):
        chat = Chat.objects.filter(members=sender).filter(members=recipient).filter(type='private').first()
        if chat is not None:
            return chat

        chat = Chat.objects.create(type='private')
        chat.members.add(sender, recipient)
        return chat

    def post(self, request, username):
        sender = request.user.userprofile
        recipient = get_object_or_404(User, username=username)
        recipient_profile, created = UserProfile.objects.get_or_create(user=recipient)
        content = request.POST.get('content', '')

        chat = self.get_or_create_private_chat(sender, recipient_profile)

        message = Message.objects.create(sender=sender, chat=chat, content=content, recipient=recipient_profile)

        # Отладочный вывод:
        print("Sending a message...")
        print("Messages:", Message.objects.filter(chat=chat).order_by('timestamp'))

        return render(request, 'chat_with_user.html', {'recipient_profile': recipient_profile,
                                                       'messages': Message.objects.filter(chat=chat).order_by(
                                                           'timestamp')})


# Редактирование сообщения

@method_decorator(login_required, name='dispatch')
class EditMessageView(View):
    template_name = 'edit_message.html'

    def get(self, request, message_id):
        message = get_object_or_404(Message, id=message_id, sender=request.user.userprofile)
        form = MessageForm(instance=message)
        return render(request, self.template_name, {'form': form, 'message_id': message_id})

    def post(self, request, message_id):
        message = get_object_or_404(Message, id=message_id, sender=request.user.userprofile)
        form = MessageForm(request.POST, instance=message)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('messenger_app:chat-with-user', args=[message.recipient.user.username]))
        return render(request, self.template_name, {'form': form, 'message_id': message_id})


# Удаление сообщения

@method_decorator(login_required, name='dispatch')
class DeleteMessageView(View):
    template_name = 'delete_message.html'

    def get(self, request, message_id):
        message = get_object_or_404(Message, id=message_id, sender=request.user.userprofile)
        return render(request, self.template_name,
                      {'message_id': message_id, 'recipient_username': message.recipient.user.username})

    def post(self, request, message_id):
        message = get_object_or_404(Message, id=message_id, sender=request.user.userprofile)
        recipient_username = message.recipient.user.username
        message.delete()
        return HttpResponseRedirect(reverse('messenger_app:chat-with-user', args=[recipient_username]))


# Отправка сообщения в групповой чат

class SendGroupMessageView(APIView):
    def post(self, request, chat_id, *args, **kwargs):
        chat = get_object_or_404(Chat, pk=chat_id, type='group')

        if request.user.userprofile not in chat.members.all():
            return Response({'status': 'Failed to send group message',
                             'errors': {'detail': 'You are not a member of this group chat.'}},
                            status=status.HTTP_403_FORBIDDEN)

        content = request.data.get('content', '')

        message = Message.objects.create(
            sender=request.user.userprofile,
            content=content,
            chat=chat,
            recipient=None
        )

        serializer = MessageSerializer(message)
        data = serializer.data

        sender_data = {
            'id': message.sender.id,
            'username': message.sender.user.username,
            'avatar': str(message.sender.avatar) if message.sender.avatar else None,
            'first_name': message.sender.first_name,
            'last_name': message.sender.last_name,
        }

        if message.recipient:
            recipient_data = {
                'id': message.recipient.id,
                'username': message.recipient.user.username,
                'avatar': str(message.recipient.avatar) if message.recipient.avatar else None,
                'first_name': message.recipient.first_name,
                'last_name': message.recipient.last_name,
            }
        else:
            recipient_data = {}

        data['sender'] = sender_data
        data['recipient'] = recipient_data

        return Response(data, status=status.HTTP_201_CREATED)


# ЧАТЫ

# Просмотр чатов

@method_decorator(login_required, name='dispatch')
class ChatListView(TemplateView):
    template_name = 'chat_list.html'

    def get_context_data(self, **kwargs):
        user_profile = self.request.user.userprofile
        chats = Chat.objects.filter(members=user_profile)
        chat_members = [
            {'chat': chat, 'chat_member': chat.members.exclude(id=user_profile.id).first()}
            for chat in chats
        ]

        for chat_member in chat_members:
            chat = chat_member['chat']
            if not chat.name:
                if chat.is_group_chat:
                    chat.name = "Групповой чат"
                else:
                    chat.name = ", ".join(
                        [member.user.username for member in chat.members.all() if member != user_profile])
                chat.save()

        context = {'chat_members': chat_members, 'user_profile': user_profile}
        return context


# Cоздание группового чата

@method_decorator(login_required, name='dispatch')
class GroupChatCreateView(View):
    template_name = 'group_chat_create.html'

    def get(self, request, *args, **kwargs):
        form = GroupChatCreationForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = GroupChatCreationForm(request.POST)
        if form.is_valid():
            group_chat = Chat.objects.create(type='group', name=form.cleaned_data['name'])

            group_chat.members.add(request.user.userprofile, *form.cleaned_data['members'])

            return JsonResponse({'status': 'success', 'redirect_url': reverse_lazy('messenger_app:group-chat-detail',
                                                                                   kwargs={'pk': group_chat.id})})

        return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)


# Просмотр группового чата

@method_decorator(login_required, name='dispatch')
class GroupChatDetailView(View):
    template_name = 'group_chat_detail.html'

    def get(self, request, pk):
        group_chat = Chat.objects.get(pk=pk)
        send_group_message_url = reverse('messenger_app:send-group-message', kwargs={'chat_id': pk})
        form = MessageForm()
        return render(request, self.template_name,
                      {'group_chat': group_chat, 'send_group_message_url': send_group_message_url, 'form': form})


# Чат с пользователем

class ChatWithUserView(View):
    template_name = 'chat_with_user.html'

    def get_or_create_private_chat(self, sender, recipient):
        chat = Chat.objects.filter(members=sender).filter(members=recipient).filter(type='private').first()
        if chat is not None:
            return chat

        # Если чат не найден, попробуем найти его в обратном порядке
        chat = Chat.objects.filter(members=recipient).filter(members=sender).filter(type='private').first()
        if chat is not None:
            return chat

        # Если чат не найден, создаем новый
        chat = Chat.objects.create(type='private')
        chat.members.add(sender, recipient)
        return chat

    def get(self, request, username):
        recipient = get_object_or_404(UserProfile, user__username=username)
        sender = request.user.userprofile

        chat = self.get_or_create_private_chat(sender, recipient)

        messages = Message.objects.filter(chat=chat).order_by('timestamp')

        # Отладочный вывод
        print("Chat members:", chat.members.all())

        return render(request, self.template_name, {
            'recipient_profile': recipient,
            'messages': messages,
        })

    def post(self, request, username):
        sender = request.user.userprofile
        recipient = get_object_or_404(User, username=username)
        recipient_profile, created = UserProfile.objects.get_or_create(user=recipient)
        content = request.POST.get('content', '')
        message_id = request.POST.get('message_id', None)

        chat = self.get_or_create_private_chat(sender, recipient_profile)

        if message_id:
            message = get_object_or_404(Message, pk=message_id, sender=sender, chat=chat)
            message.content = content
            message.save()
        else:
            message = Message.objects.create(sender=sender, chat=chat, content=content, recipient=recipient_profile)

        # Отладочный вывод:
        print("Sending a message...")
        print("Messages:", Message.objects.filter(chat=chat).order_by('timestamp'))

        return HttpResponseRedirect(reverse('messenger_app:chat-with-user', args=[username]))


# ПОЛЬЗОВАТЕЛИ

# Список пользователей

@method_decorator(login_required, name='dispatch')
class UserListView(ListView):
    model = User
    template_name = 'user_list.html'
    context_object_name = 'users'

    def get_queryset(self):
        return User.objects.exclude(pk=self.request.user.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = self.get_queryset()
        return context


# РЕГИСТРАЦИЯ И АВТОРИЗАЦИЯ

# Авторизация

class CustomLoginView(View):
    template_name = 'registration/login.html'

    def get(self, request, *args, **kwargs):
        form = AuthenticationForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('messenger_app:chat-list')
        return render(request, self.template_name, {'form': form})


# Регистрация

class CustomRegisterView(View):
    template_name = 'registration/register.html'

    def get(self, request, *args, **kwargs):
        form = UserCreationForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('messenger_app:chat-list')
        return render(request, self.template_name, {'form': form})
