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

from .views import register_view
from .views import login_view
from .views import generate_otp_view
from .views import register_to_vote_view
from .views import logout_view

urlpatterns = [
    path('register/', register_view, name='register_view'),
    path('login/', login_view, name='login_view'),
    path('generate_otp/', generate_otp_view, name='generate_otp_view'),
    path('register_to_vote/', register_to_vote_view, name='register_to_vote_view'),
    path('logout/', logout_view, name='logout_view'),
]
