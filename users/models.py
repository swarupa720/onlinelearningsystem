from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('faculty', 'Faculty'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    # Personal info fields
    phone = models.CharField(max_length=20, blank=True, null=True)

    @property
    def full_name(self):
        # Returns full name or username if names are empty
        if self.first_name or self.last_name:
            return f"{self.first_name} {self.last_name}".strip()
        return self.username

    def __str__(self):
        return self.username
