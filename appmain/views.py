from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from requests import post as request_post

from support.signature import sign
from users.models import Profile


# home view
def home_view(request, *args, **kwargs):
    if request.POST:
        voterid = request.POST.get('voterid')
        otp = request.POST.get('otp')
        if voterid == '1':  # valid_user(voterid, otp):
            return redirect('vote cast')
    return render(request, "home_page.html", {})


# vote cast view
@login_required
def vote_cast_view(request, *args, **kwargs):
    voter = Profile.objects.get(voter_id=request.user.voter_id)
    if request.POST and voter.registered:
        data = {
            "tempid": request.POST.get('tempid'),
            "voted": request.POST.get('voted'),
            "timestamp": request.POST.get('timestamp'),
        }
        post_data = {
            "data": str(data),
            "signature": request.POST.get('signature'),
        }
        response = request_post("http://"+str(request.META['HTTP_HOST'])+'/miner/update_transaction/', data=post_data)
        content = response.content

    return render(request, "votecast_page.html", {})


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


# election result view
def election_result_view(request, *args, **kwargs):
    if request.POST:
        print(request)
    return HttpResponse("Election Result")
