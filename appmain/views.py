from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from requests import post as request_post

from users.models import Profile
from miner.views import get_result
from miner.views import get_all_transactions
from miner.views import register_with_existing_node
from users.models import Candidate
from .models import KeyModel
from support.signature import sign
from support.signature import verify


# endpoint to cast vote during election
# here vote is casted on registered candidates
# /vote_cast_view
@login_required
def vote_cast_view(request, *args, **kwargs):
    candidates = Candidate.objects.all()
    voter = Profile.objects.get(voter_id=request.user.profile.voter_id)
    if not voter.registered:
        print("not registered")
        context = {"head": 'Can\'t cast vote ..!', "message": ''}
        return render(request, "home_page.html", context)

    elif request.POST:
        data = {
            "tempid": request.POST.get('tempid'),
            "voted": request.POST.get('voted'),
            "timestamp": request.POST.get('timestamp'),
        }
        sk_str = request.POST.get('sk_hex')
        t = ''
        i = 0
        for x in sk_str.split("-----")[:-1]:
            i += 1
            if i == 3:
                t += x.replace(" ", "\n") + "-----"
            else:
                t += x + "-----"
        signature = sign(sk_str=t, data=data)
        try:
            vk_str = KeyModel.objects.get(temp_id=request.POST.get('tempid')).__dict__.get("pukey")
        except KeyModel.DoesNotExist:
            print("already voted")
            context = {"head": 'Can\'t cast vote ..!', "message": ''}
            return render(request, "home_page.html", context)

        post_data = {
            "data": str(data),
            "signature": signature,
        }
        url = 'http://'+str(request.META['HTTP_HOST'])+'/miner/update_transaction/'
        response = request_post(url, data=post_data)
        content = response.content
        context = {"head": 'Casted vote successfully ..!', "message": ''}
        return render(request, "home_page.html", context)

    return render(request, "votecast_page.html", {'candidates': candidates})


# election result view
def election_result_view(request, *args, **kwargs):
    cumulated = get_result()
    return render(request, "home_page.html", {'head': 'Result', 'message': cumulated})
    # return render(request, "result_page.html", {'cumulated': cumulated})


# transaction view
def transaction_view(request, *args, **kwargs):
    transactions = get_all_transactions()
    return render(request, "home_page.html", {'head': 'Transactions', 'message': transactions})
    # return render(request, "transaction_page.html", {'transactions': transactions})


# home view
def home_view(request, *args, **kwargs):
    if request.POST:
        voterid = request.POST.get('voterid')
        otp = request.POST.get('otp')
        if voterid == '1':  # valid_user(voterid, otp):
            return redirect('vote cast')
    return render(request, "home_page.html", {})


# reg
def reg(request, *args, **kwargs):
    if request.POST:
        post_data = {
            "register_with_node_address": request.POST.get('register_with_node'),
            "current_node_address": request.META['HTTP_HOST'],
        }
        response = register_with_existing_node(post_data)
        content = response.get('content')
        if response.get('status_code') == 200:
            print("pears updated")
        return render(request, "home_page.html", {'head': content})
    return render(request, "register.html", {})
