from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from requests import post as request_post

from users.models import Profile
from users.models import Candidate


# endpoint to return intermediate page
# this page redirects to register, vote, view transaction and results pages based on request
# /intermediate_view
@login_required
def intermediate_view(request, *args, **kwargs):
    if request.POST:
        if request.POST.get('op') == 'vote_cast':
            return redirect('vote_cast')
        elif request.POST.get('op') == 'register':
            return redirect('register_to_vote_view')
        elif request.POST.get('op') == 'election_result':
            return redirect('election_result')
        elif request.POST.get('op') == 'transaction_view':
            return redirect('transaction_view')
    return render(request, 'intermediate_page.html')


# endpoint to cast vote during election
# here vote is casted on registered candidates
# /vote_cast_view
@login_required
def vote_cast_view(request, *args, **kwargs):
    candidates = Candidate.objects.all()
    print(request.user.__dict__)
    voter = Profile.objects.get(voter_id=request.user.profile.voter_id)
    if not voter.registered:
        print("not registered")
        return redirect('intermediate_view')

    elif request.POST:
        data = {
            "tempid": request.POST.get('tempid'),
            "voted": request.POST.get('voted'),
            "timestamp": request.POST.get('timestamp'),
        }
        post_data = {
            "data": str(data),
            "signature": request.POST.get('signature'),
        }
        url = 'http://'+str(request.META['HTTP_HOST'])+'/miner/update_transaction/'
        response = request_post(url, data=post_data)
        content = response.content

    return render(request, "votecast_page.html", {'candidates': candidates})


# election result view
def election_result_view(request, *args, **kwargs):
    cumulated = 'cumulated'  # last_block()
    return render(request, "result_page.html", {'cumulated': cumulated})


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
        return HttpResponse(content)
    return render(request, "register.html", {})
