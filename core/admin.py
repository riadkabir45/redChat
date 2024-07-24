from django.contrib import admin
from .models import CustomUser, ChatTable

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(ChatTable)

