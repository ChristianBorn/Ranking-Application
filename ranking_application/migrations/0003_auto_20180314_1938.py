# Generated by Django 2.0.3 on 2018-03-14 17:38

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('ranking_application', '0002_auto_20180314_1916'),
    ]

    operations = [
        migrations.CreateModel(
            name='aggregated_score',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.DecimalField(decimal_places=9, max_digits=10)),
                ('last_updated', models.DateTimeField(default=django.utils.timezone.now)),
                ('requirement', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='ranking_application.requirement')),
            ],
        ),
        migrations.AlterField(
            model_name='ranking',
            name='rank',
            field=models.CharField(default='N', max_length=3),
        ),
        migrations.AlterField(
            model_name='ranking',
            name='ranked_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='ranking_application.app_user'),
        ),
        migrations.AlterField(
            model_name='ranking',
            name='ranked_requirement',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='ranking_application.requirement'),
        ),
    ]
