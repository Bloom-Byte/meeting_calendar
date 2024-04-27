# Generated by Django 5.0.4 on 2024-04-27 15:56

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(help_text='Give a title to the session', max_length=255, verbose_name='Session title')),
                ('start', models.DateTimeField(help_text='When does this session start?', verbose_name='Starts')),
                ('end', models.DateTimeField(help_text='When does this session end?', verbose_name='Ends')),
                ('has_held', models.BooleanField(default=False, help_text='Has this session been held? If so, check this.')),
                ('cancelled', models.BooleanField(default=False, help_text='Check this if you want to cancel this session')),
                ('rescheduled_at', models.DateTimeField(blank=True, help_text='When was this session date or time changed?', null=True, verbose_name='Rescheduled at')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Session',
                'verbose_name_plural': 'Sessions',
                'ordering': ['-start__date', 'start__time'],
            },
        ),
        migrations.CreateModel(
            name='UnavailablePeriod',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('start', models.DateTimeField(help_text='From what date and time you will be unavailable?', verbose_name='From')),
                ('end', models.DateTimeField(help_text='Till what date and time you will be unavailable?', verbose_name='To')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Unavailable Period',
                'verbose_name_plural': 'Unavailable Periods',
                'ordering': ['start'],
            },
        ),
    ]
