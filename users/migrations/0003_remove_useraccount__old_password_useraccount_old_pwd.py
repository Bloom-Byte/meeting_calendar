# Generated by Django 5.0.4 on 2024-04-19 19:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_useraccount__old_password'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='useraccount',
            name='_old_password',
        ),
        migrations.AddField(
            model_name='useraccount',
            name='old_pwd',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]