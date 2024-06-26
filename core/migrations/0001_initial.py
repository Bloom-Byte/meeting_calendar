# Generated by Django 5.0.4 on 2024-05-16 18:56

import timezone_field.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BusinessHoursSettings',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('opens_at', models.TimeField(default='08:00:00', help_text='The time the business opens', verbose_name='Business opens at')),
                ('closes_at', models.TimeField(default='20:00:00', help_text='The time the business closes', verbose_name='Business closes at')),
                ('timezone', timezone_field.fields.TimeZoneField(default='UTC')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
