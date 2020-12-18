from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, login, authenticate
from django.views.generic import DetailView
from django.core.mail import send_mail
import os

import face_recognition
import cv2
import math
import random

'''from .form import UserRegisterForm
from .form import ProfileUpdateForm
from .form import UserServiceForm
from .models import Service, Profile
from chevai.operation import get_notification'''


from django.http import HttpResponseRedirect
from django.shortcuts import render

from .forms import LoginForm
from .models import Profile


def otpmatch(voter, otp):
    return True


def facematch(loc):
    cam = cv2.VideoCapture(0)
    s, img = cam.read()
    if s:

        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        MEDIA_ROOT = os.path.join(BASE_DIR, 'pages')

        loc = (str(MEDIA_ROOT) + loc)
        face_1_image = face_recognition.load_image_file(loc)
        face_1_face_encoding = face_recognition.face_encodings(face_1_image)[0]

        small_frame = cv2.resize(img, (0, 0), fx=0.25, fy=0.25)

        rgb_small_frame = small_frame[:, :, ::-1]

        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        check = face_recognition.compare_faces(face_1_face_encoding, face_encodings)

        print(check)
        if check[0]:
            return True

        else:
            return False


def login_view(request, *args, **kwargs):
    if request.POST:
        form = LoginForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            print(data)
            voter = Profile.objects.get(voter_id=data.get("voter_id"))
            # validate voter
            if facematch(data.get("image")) and otpmatch(data.get("otp")):
                """if voter.registered:
                    login(request, voter)
                    return redirect('vote_cast_view')
                else:
                    return redirect('intermediate_view')"""
                return redirect('intermediate_view')
        messages.error(request, 'Login failed..!')
    else:
        form = LoginForm()

    return render(request, 'login_page.html', {'form': form})


def generate_otp_view(request, *args, **kwargs):
    if request.POST:
        data = request.POST.get("voter_id")
        # save otp in password field
        otp = '111111'  # generate_otp(data.get("voter_id"))
        voter = Profile.objects.get(voter_id=data.get("voter_id"))
        voter.set_password(otp)
        voter.save()


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


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'You are logged out')
    return redirect('user_login')
