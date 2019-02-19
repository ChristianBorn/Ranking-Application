from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class project(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    creation_date = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey('app_user', on_delete=models.CASCADE, null=True)


    def __str__(self):
        return self.title


class app_user(models.Model):
    username = models.OneToOneField(User, on_delete=models.CASCADE)
    ROLES = (
        ('PM', 'Project manager'),
        ('TL', 'Technical lead'),
        ('PO', 'Project owner'),
        ('SD', 'Senior designer'),
        ('SM', 'Senior manager'),
        ('QM', 'Quality manager'),
        ('CR', 'Customer representative')
    )
    role = models.CharField(max_length=2, choices=ROLES)
    active_project = models.ForeignKey('project', on_delete=models.SET_NULL, blank=True, null=True)

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            app_user.objects.create(username=instance)

    def get_role(self):
        return self.role



class assigned_criteria(models.Model):
    assigned_to_project = models.ForeignKey('project', on_delete=models.CASCADE, null=True)
    criterion = models.CharField(max_length=99)

class project_owned_by(models.Model):
    project = models.ForeignKey('project', on_delete=models.CASCADE, null=True)
    project_owner = models.ManyToManyField(app_user)


class requirement(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    assigned_to_project = models.ForeignKey('project', on_delete=models.CASCADE, null=True)
    created_by = models.ForeignKey('app_user', on_delete=models.CASCADE, null=True)
    creation_date = models.DateTimeField(default=timezone.now)
    id_in_project = models.IntegerField(blank=False)

    def __str__(self):
        return self.title


class project_assignees(models.Model):
    assigned_to_project = models.ForeignKey('project', on_delete=models.CASCADE, null=True)
    assigned_user = models.ManyToManyField(app_user)



class ranking(models.Model):
    ranked_requirement = models.ForeignKey('requirement', on_delete=models.CASCADE, null=True)
    ranked_by = models.ForeignKey('app_user', on_delete=models.CASCADE, null=True)
    rank = models.CharField(max_length=3, default='N')
    last_updated = models.DateTimeField(default=timezone.now)
    project = models.ForeignKey('project', on_delete=models.CASCADE, null=True)
    criterion = models.CharField(max_length=99)


class aggregated_score(models.Model):
    requirement = models.ForeignKey('requirement', on_delete=models.CASCADE, null=True)
    score = models.DecimalField(max_digits=10, decimal_places=9)
    last_updated = models.DateTimeField(default=timezone.now)
