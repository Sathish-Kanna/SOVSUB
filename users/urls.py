"""SOVSUB.appmain URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.urls import path

from .views import login_view
from .views import generate_otp_view
from .views import register_to_vote_view
from .views import intermediate_view

urlpatterns = [
    path('login_view/', login_view, name='login view'),
    path('generate_otp_view/', generate_otp_view, name='generate otp view'),
    path('register_to_vote_view/', register_to_vote_view, name='register to vote view'),
    path('intermediate_view/', intermediate_view, name='intermediate view'),
]
