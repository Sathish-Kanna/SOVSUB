from django.shortcuts import redirect
from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, login
import json
import pickle

from twilio.rest import Client
import face_recognition
import cv2
import random

from .forms import LoginForm
from .models import Profile


def otpmatch(voter_id, otp):
    voter = Profile.objects.get(voter_id=voter_id)
    return otp == voter.get('password')


def facematch(voter_id):
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


# endpoint to login voters
# This will be used by our application to authenticate the voters
# /login_view
def login_view(request, *args, **kwargs):
    if request.POST:
        form = LoginForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            print(data)
            # validate voter
            if facematch(data.get("image")) and otpmatch(data.get("voter_id"), data.get("otp")):
                return redirect('intermediate_view')
        messages.error(request, 'Login failed..!')
    else:
        form = LoginForm()

    return render(request, 'login_page.html', {'form': form})


# endpoint to generate otp
# we use this to generate otp from login page
# /generate_otp_view
def generate_otp_view(request, *args, **kwargs):
    if request.POST:
        # env.json is the file with twilio and other credentials
        with open("env.json") as json_file:
            env = json.load(json_file)
        account_sid = env.get('TWILIO_ACCOUNT_SID')
        auth_token = env.get('TWILIO_AUTH_TOKEN')
        client = Client(account_sid, auth_token)

        data = request.POST.get("voter_id")
        # fetch the voter data from database
        voter = Profile.objects.get(voter_id=data.get("voter_id"))

        # generate otp for verification
        msg_bdy = "Your OTP is: "
        otp = ''
        for i in range(6):
            otp += str(random.randint(1, 9))

        # save otp in password field
        voter.set_password(otp)
        voter.save()

        # create and send otp message to voter
        message = client.messages.create(
            body=msg_bdy+otp,               # message data
            from_=env.get('TWILIO_NUM'),    # your number
            to=str(voter.phone_number)      # voter mobile number
        )
        print(message.sid)


# endpoint to register for voting
# this is used for the registration of the voters for election
# /register_to_vote_view
@login_required
def register_to_vote_view(request, *args, **kwargs):
    if request.POST:
        voter = Profile.objects.get(voter_id=request.user.voter_id)
        if not voter.registered:
            messages.error(request, 'already registered..!')
        else:
            voter.set_registered(True)
            voter.save()
            messages.success(request, 'You are registered')
    return redirect('intermediate_view')


# /logout_view
@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'You are logged out')
    return redirect('user_login')
