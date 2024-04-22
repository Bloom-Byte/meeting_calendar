# Generated by Django 5.0.4 on 2024-04-19 12:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0002_initial'),
        ('links', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='session',
            name='link',
            field=models.ForeignKey(blank=True, help_text='The link to the session', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='session', to='links.link', verbose_name='Link'),
        ),
    ]