from django.db import models

class FontModel(models.Model):
    # Your fields here
    name = models.CharField(max_length=100)
    # Add other fields as necessary
from django.contrib.auth.models import User
from django.db import models

class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('designer', 'Designer'),
        ('editor', 'Editor'),
    )
    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return self.user.username + " - " + self.role