# Generated by Django 2.0.3 on 2018-05-05 11:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ranking_application', '0015_ranking_project'),
    ]

    operations = [
        migrations.CreateModel(
            name='assigned_criteria',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('criterion', models.CharField(max_length=99)),
                ('assigned_to_project', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='ranking_application.project')),
            ],
        ),
        migrations.AddField(
            model_name='ranking',
            name='criterion',
            field=models.CharField(default='Importance', max_length=99),
            preserve_default=False,
        ),
    ]
