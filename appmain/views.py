from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from requests import post as request_post

from users.models import Profile
from miner.views import get_result
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
        return redirect('home')

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
        vk_str = KeyModel.objects.get(temp_id=request.POST.get('tempid')).__dict__.get("pukey")
        post_data = {
            "data": str(data),
            "signature": signature,
        }
        url = 'http://'+str(request.META['HTTP_HOST'])+'/miner/update_transaction/'
        response = request_post(url, data=post_data)
        content = response.content

    return render(request, "votecast_page.html", {'candidates': candidates})


# election result view
def election_result_view(request, *args, **kwargs):
    cumulated = get_result()
    return render(request, "home_page.html", {'head': 'Result', 'message': cumulated})
    # return render(request, "result_page.html", {'cumulated': cumulated})


# election result view
def transaction_view(request, *args, **kwargs):
    transactions = 'trans'  # all_transaction_in_block()
    return render(request, "transaction_page.html", {'transactions': transactions})


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
            "register_with_node": request.POST.get('register_with_node'),
            "node_address": request.META['HTTP_HOST'],
        }
        response = request_post("http://"+request.META['HTTP_HOST'] + '/miner/register_with/', data=post_data)
        content = response.content
        if response.status_code == 200:
            print("pears updated")
        return render(request, "home_page.html", {'head': content.decode()})
    return render(request, "register.html", {})
