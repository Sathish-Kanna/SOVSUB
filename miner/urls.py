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

from .views import update_transaction
from .views import set_new_transaction
from .views import get_chain
from .views import mine_unconfirmed_transactions
from .views import register_new_peers
from .views import register_with_existing_node
from .views import verify_and_add_block
from .views import get_pending_tx

urlpatterns = [
    path('update_transaction/', update_transaction, name='update transaction'),
    path('new_transaction/', set_new_transaction, name='set new transaction'),
    path('chain/', get_chain, name='get chain'),
    path('mine/', mine_unconfirmed_transactions, name='mine unconfirmed transactions'),
    path('register_node/', register_new_peers, name='register new peers'),
    path('register_with/', register_with_existing_node, name='register with existing node'),
    path('add_block/', verify_and_add_block, name='verify and add block'),
    path('pending_tx/', get_pending_tx, name='get pending tx'),
    path('pending_tx/', get_pending_tx, name='get_pending_tx'),
    path('pending_tx/', get_pending_tx, name='get_pending_tx'),
]
