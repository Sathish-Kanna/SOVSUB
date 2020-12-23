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

from .views import intermediate_view
from .views import home_view
from .views import vote_cast_view
from .views import election_result_view
from .views import transaction_view
from .views import reg

urlpatterns = [
    path('intermediate_view/', intermediate_view, name='intermediate_view'),
    path('', home_view, name='home'),
    path('vote/', vote_cast_view, name='vote_cast'),
    path('result/', election_result_view, name='election_result'),
    path('transaction_view/', transaction_view, name='transaction_view'),
    path('reg/', reg, name='reg'),
]
