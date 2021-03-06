# Generated by Django 2.0.3 on 2018-03-20 09:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ranking_application', '0007_auto_20180319_1813'),
    ]

    operations = [
        migrations.CreateModel(
            name='project_owned_by',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='ranking_application.project')),
                ('project_owner', models.ManyToManyField(to='ranking_application.app_user')),
            ],
        ),
    ]
