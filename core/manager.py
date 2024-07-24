from typing import Any
from django.contrib.auth.models import BaseUserManager


class CustomUserManager(BaseUserManager):
    def create_user(self,username,password,**extra_field):
        user = self.model(username=username,**extra_field)
        user.set_password(password)
        user.save(using = self.db)

        return user
    
    def create_superuser(self,username,password,**extra_field):
        extra_field.setdefault("is_superuser",True)
        extra_field.setdefault("is_staff",True)

        return self.create_user(username,password,**extra_field)
