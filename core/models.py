from django.db import models
from .manager import CustomUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from datetime import datetime as dt

# Create your models here.

class CustomUser(AbstractBaseUser,PermissionsMixin,models.Model):
    username = models.CharField(max_length=100,unique=True)
    password = models.CharField(max_length = 100)

    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'

    objects = CustomUserManager()

    def __str__(self):
        return self.username

class ChatLink(models.Model):
    user1 = models.ForeignKey(CustomUser, on_delete=models.CASCADE,related_name="src")
    user2 = models.ForeignKey(CustomUser, on_delete=models.CASCADE,related_name="dest")

    def __str__(self):
        return f"{self.user2.username}->{self.user1.username}"

class ChatTable(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    msg = models.CharField(max_length = 200)
    timestamp = models.DateField(default = dt.now)
    link = models.ForeignKey(ChatLink, on_delete=models.CASCADE,null=True)

    def __str__(self):
        return f"{self.user.username}->{self.msg}@{self.timestamp}"
