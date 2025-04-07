from django.contrib.auth.models import AbstractUser
from django.db import models
from apps.shared.models import BaseModel


class User(BaseModel,AbstractUser):
    avatar = models.ImageField(upload_to='users', null=True, blank=True)

    def __str__(self):
        return self.username







