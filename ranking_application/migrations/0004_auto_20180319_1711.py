# Generated by Django 2.0.3 on 2018-03-19 15:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ranking_application', '0003_auto_20180314_1938'),
    ]

    operations = [
        migrations.AddField(
            model_name='app_user',
            name='first_name',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='app_user',
            name='last_name',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
