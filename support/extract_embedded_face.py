import cv2
import face_recognition
import pickle


def extract_face_embedding():
    voter_id = input("Voter ID: ")
    # define a video capture object
    video_feed = cv2.VideoCapture(0)
    # Capture the video frame by frame
    rtn_tru, img = video_feed.read()

    if rtn_tru:
        # resize image
        small_frame = cv2.resize(img, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = small_frame[:, :, ::-1]
        # locate face in resized image
        face_locations = face_recognition.face_locations(rgb_small_frame)
        # encode the located face
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)[0]

        data = {voter_id: face_encodings}
        with open("./face_encodings/encodings.pickle", "wb") as f:
            pickle.dump(data, f)
    cv2.imshow("Frame", img)
