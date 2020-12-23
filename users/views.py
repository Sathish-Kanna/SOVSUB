from django.shortcuts import redirect
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, login
from datetime import datetime
import json
import pickle
import random

from twilio.rest import Client
import face_recognition
import cv2

from .forms import LoginForm
from .models import Profile
from appmain.models import KeyModel
from support.signature import key_generator


# endpoint to login voters
# This will be used by our application to authenticate the voters
# /login_view
def login_view(request, *args, **kwargs):
    if request.POST.get('generate_otp'):
        generate_otp_view(request.POST.get('voter_id'))
    if request.POST.get('login'):
        data = request.POST
        # validate voter
        if facematch(data.get("voter_id")) and otpmatch(data.get("voter_id"), data.get("otp")):
            voter = Profile.objects.get(voter_id=data.get("voter_id"))
            # login(request, voter)
            return redirect('intermediate_view')
        messages.error(request, 'Login failed..!')
    else:
        form = LoginForm()

    return render(request, 'login_page.html', {'form': form})


# endpoint to generate otp
# we use this to generate otp from login page
# /generate_otp_view
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
# /register_to_vote_view
@login_required
def register_to_vote_view(request, *args, **kwargs):
    print(request.POST)
    if request.POST:
        voter_id = request.user.voter_id
        voter = Profile.objects.get(voter_id=voter_id)
        if not voter.registered:
            messages.error(request, 'already registered..!')
        else:
            t_id, sk_hex, pk_hex = key_generator(voter_id)
            km = KeyModel.objects.create(voter_id=voter_id, temp_id=t_id, pukey=pk_hex)
            voter.set_registered(True)
            voter.save()
            messages.success(request,
                             'You are registered id is:' + t_id + 'and your private key is: '+sk_hex)
    return redirect('intermediate_view')


# /logout_view
@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'You are logged out')
    return redirect('user_login')


def otpmatch(voter_id, otp):
    voter = Profile.objects.get(voter_id=voter_id).__dict__
    return otp == voter.get('otp')


def facematch(voter_id):
    return True
    # define a video capture object
    video_feed = cv2.VideoCapture(0)
    # Capture the video frame by frame
    rtn_tru, img = video_feed.read()

    if rtn_tru:
        # read encoded face of voter from dataset
        with open("./face_encodings/encodings.pickle", "rb") as f:
            data = pickle.loads(f.read())
        encoded_face_ds = data.get(voter_id)

        # resize image
        small_frame = cv2.resize(img, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = small_frame[:, :, ::-1]
        # locate face in resized image
        face_locations = face_recognition.face_locations(rgb_small_frame)
        # encode the located face
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        # compare the encoded face with encoded face dataset
        check = face_recognition.compare_faces(encoded_face_ds, face_encodings)

        print(check)
        if check[0]:
            return True
        else:
            return False
