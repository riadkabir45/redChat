"""
URL configuration for chatbox project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path("", views.index,name='index'),
    path("signup/", views.signup,name='signup'),
    path("signin/", views.signin,name='signin'),
    path("dashboard/", views.dashboard,name='dashboard'),
    path("chat/", views.chat,name='chat'),
    path("chat/<str:target>", views.chatTarget,name='chatTarget'),
    path("gchat/", views.gchat,name='gchat'),
    path("gchat/<str:target>/", views.gchatTarget,name='gchatTarget'),
    path("target/", views.target,name='target'),
    path("logout/", views.logout,name='logout'),
    path("post/", views.post,name='post'),
]
