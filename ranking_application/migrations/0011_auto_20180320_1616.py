# Generated by Django 2.0.3 on 2018-03-20 14:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ranking_application', '0010_auto_20180320_1616'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project_owned_by',
            name='project_owner',
            field=models.ManyToManyField(to='ranking_application.app_user'),
        ),
    ]
