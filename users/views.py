from django.shortcuts import redirect
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, login
from datetime import datetime
import json
import random

from twilio.rest import Client

from .forms import LoginForm
from .forms import UserRegisterForm
from .models import Profile
from .auth_backend import authenticate
from appmain.models import KeyModel
from support.signature import key_generator


# endpoint to register new voters
# This will be used by our application to register new voters
# /register
def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save(commit=False)
            user = form.save()
            user.refresh_from_db()
            profile, created = Profile.objects.get_or_create(user=user)
            profile.voter_id = form.cleaned_data.get('voter_id')
            profile.name = form.cleaned_data.get('name')
            profile.booth_id = form.cleaned_data.get('booth_id')
            profile.phone_number = form.cleaned_data.get('phone_number')
            profile.save()

            voter_id = form.cleaned_data.get('voter_id')
            pk = user.profile.pk
            messages.success(request, 'Account has been created for ' + voter_id + '! You can login')
            return redirect('intermediate_view')
    else:
        form = UserRegisterForm()

    form_dict = {'form': form}
    return render(request, 'register_page.html', form_dict)


# endpoint to login voters
# This will be used by our application to authenticate the voters
# /login
def login_view(request, *args, **kwargs):
    if request.POST.get('generate_otp'):
        generate_otp_view(request.POST.get('voter_id'))
    if request.POST.get('login'):
        data = request.POST
        # validate voter
        voter = Profile.objects.get(voter_id=data.get("voter_id")).__dict__
        user = authenticate(
            voter_id=data.get("voter_id"),
            otp=data.get("otp"),
            user_id=voter.get('user_id')
        )
        # user.backend = 'django.contrib.auth.backends.ModelBackend'
        if user:
            login(request, user)
            return redirect('intermediate_view')
        messages.error(request, 'Login failed..!')
    else:
        return render(request, 'login_page.html', {'form': LoginForm()})


# endpoint to generate otp
# we use this to generate otp from login page
# /generate_otp
def generate_otp_view(voter_id):
    # env.json is the file with twilio and other credentials
    with open("env.json") as json_file:
        env = json.load(json_file)
    twilio_env = env.get('TWILIO')
    account_sid = twilio_env.get('ACCOUNT_SID')
    auth_token = twilio_env.get('AUTH_TOKEN')
    client = Client(account_sid, auth_token)

    # fetch the voter data from database
    voter = Profile.objects.get(voter_id=voter_id)

    # generate otp for verification
    msg_bdy = "Your OTP is: "
    otp = ''
    for i in range(6):
        otp += str(random.randint(1, 9))

    # save otp in password field
    # voter.set_password(otp)
    voter.otp = otp
    now = datetime.now()
    timestamp = datetime.timestamp(now)
    # voter.set_otp_time(timestamp)
    voter.otp_time = timestamp
    voter.save()

    # create and send otp message to voter
    message = client.messages.create(
        body=msg_bdy+otp,                   # message data
        from_=twilio_env.get('NUMBER'),     # your number
        to=str(voter.phone_number)          # voter mobile number
    )
    print(message.sid)


# endpoint to register for voting
# this is used for the registration of the voters for election
# /register_to_vote
@login_required
def register_to_vote_view(request, *args, **kwargs):
    if request.method == 'GET':
        voter_id = request.user.profile.voter_id
        voter = Profile.objects.get(voter_id=voter_id)
        if voter.registered:
            print("registered already")
            messages.error(request, 'already registered..!')
        else:
            t_id, sk_str, vk_str = key_generator(voter_id)
            km = KeyModel.objects.create(voter_id=voter_id, temp_id=t_id, pukey=vk_str)
            voter.registered = True
            voter.save()
            print('You are registered id is: ' + str(t_id) + ' and your private key is: \n'+str(sk_str))
            messages.success(request,
                             'You are registered id is: ' + str(t_id) + ' and your private key is: '+str(sk_str))
    return redirect('intermediate_view')


# /logout_view
@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'You are logged out')
    return redirect('user_login')


