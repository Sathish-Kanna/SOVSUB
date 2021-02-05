from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
import pickle
from datetime import datetime

import face_recognition
import cv2

from .models import Profile


def otpmatch(voter_id, otp, otp_time):
    now = datetime.now()
    timenow = datetime.timestamp(now)
    # TODO remove the comment statement
    """if timenow - float(otp_time) > 300: 
        return False"""
    voter = Profile.objects.get(voter_id=voter_id).__dict__
    return otp == voter.get('otp')


def facematch(voter_id):
    return True  # TODO remove this return statement
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


def authenticate(voter_id, otp, otp_time, user_id):
    try:
        if facematch(voter_id) and otpmatch(voter_id, otp, otp_time):
            user = User.objects.get(id=user_id)
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            return user
        else:
            return None
    except User.DoesNotExist:
        return None
