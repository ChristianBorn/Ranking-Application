# Generated by Django 2.0.3 on 2018-03-19 16:13

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ranking_application', '0006_auto_20180319_1812'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Profile',
            new_name='app_user',
        ),
    ]
