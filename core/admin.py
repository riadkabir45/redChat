from django.contrib import admin
from .models import CustomUser, ChatTable, ChatLink

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(ChatTable)
admin.site.register(ChatLink)

