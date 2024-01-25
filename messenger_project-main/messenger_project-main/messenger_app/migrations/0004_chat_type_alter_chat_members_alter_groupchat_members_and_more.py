# Generated by Django 4.2.8 on 2023-12-15 20:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('messenger_app', '0003_groupchat'),
    ]

    operations = [
        migrations.AddField(
            model_name='chat',
            name='type',
            field=models.CharField(choices=[('group', 'Group Chat'), ('private', 'Private Chat')], default='private', max_length=10),
        ),
        migrations.AlterField(
            model_name='chat',
            name='members',
            field=models.ManyToManyField(related_name='chats', to='messenger_app.userprofile'),
        ),
        migrations.AlterField(
            model_name='groupchat',
            name='members',
            field=models.ManyToManyField(related_name='group_chats', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='message',
            name='chat',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='messenger_app.chat'),
        ),
    ]