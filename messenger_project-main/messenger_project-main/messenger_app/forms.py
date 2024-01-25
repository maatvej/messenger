from django import forms
from .models import UserProfile, Chat, Message


# Форма для редактирования профиля

class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(label='Имя', max_length=100)
    last_name = forms.CharField(label='Фамилия', max_length=100)

    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'avatar']
        labels = {
            'avatar': 'Аватар',
        }
        widgets = {
            'avatar': forms.FileInput(attrs={'accept': 'image/*'}),
        }

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        self.fields['avatar'].required = False


# Форма для чата

class ChatForm(forms.ModelForm):
    members = forms.ModelMultipleChoiceField(
        queryset=UserProfile.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = Chat
        fields = ['name', 'members']


# Форма редактирования сообщения

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content']


# Форма для создания группового чата

class GroupChatCreationForm(forms.ModelForm):
    class Meta:
        model = Chat
        fields = ['name', 'members']


# Форма для отправки сообщения в групповом чате

class GroupMessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content', 'recipient']

    def __init__(self, *args, **kwargs):
        super(GroupMessageForm, self).__init__(*args, **kwargs)
        if 'chat' in self.fields and self.instance.chat.type == 'group':
            self.fields['recipient'].widget = forms.HiddenInput()
