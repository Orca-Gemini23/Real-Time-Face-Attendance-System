from datetime import datetime
import cv2
import os
import pickle
import numpy as np
import cvzone
import firebase_admin
import face_recognition
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

cred = credentials.Certificate("serviceAccount.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://faceattendancert-a83d1-default-rtdb.firebaseio.com/",
    'storageBucket': "faceattendancert-a83d1.appspot.com"
})

bucket = storage.bucket()

# This is the code for the webcam and the graphics
cap = cv2.VideoCapture(0)
# 1 is for the external camera and 0 is for the
# To capture the video !!

cap.set(3, 640)
cap.set(4, 480)

# Graphics code
imgBackground = cv2.imread('Resources/background.png')

# Importing the mode images in the list !!
folderModePath = 'Resources/Modes'
modePathList = os.listdir(folderModePath)
imgModeList = []
for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))

# print(len(imgModeList))


# Loading the encoding file
print("Loading Encode File ... ")
file = open('EncodeFile.p', 'rb')
encodeListKnownWithIds = pickle.load(file)  ## List all the information
file.close()
encodeListKnown, studentIds = encodeListKnownWithIds
# print(studentIds)
print("Encode file loaded")

modeType = 0  # then the system is active
counter = 0  # Once the pic is detected , counter turns 1
id = -1
imgStudent = []

while True:
    success, img = cap.read()

    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCurrFrame = face_recognition.face_locations(imgS)
    # This is for the new face
    encodeCurrFrame = face_recognition.face_encodings(imgS, faceCurrFrame)
    # This will find the encoding of the face !!

    imgBackground[162:162 + 480, 55:55 + 640] = img  # For adding the background and the image too
    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

    if faceCurrFrame:

        for encodeFace, faceLoc in zip(encodeCurrFrame, faceCurrFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)

            # prints the lowest possible value if true :
            # will give a vector of length 3 , coz  3 images now!
            # print("matches", matches)
            # print("faceDis", faceDis)

            # now we want to give the lowest index
            matchIndex = np.argmin(faceDis)
            # this will print the index value !!
            # print("Match index: ", matchIndex)
            # if we get the match index value , we will say that the face is detected !!

            if matches[matchIndex]:
                # print("Face is known")
                # print(studentIds[matchIndex])

                # bbox is bounding box (for the corner bg of the image)
                y1, x2, y2, x1 = faceLoc  # wth
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                # as the image is diminished to 1/4th of image

                bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)
                id = studentIds[matchIndex]

                if counter == 0:
                    cvzone.putTextRect(imgBackground, "Loading", (275, 400))
                    cv2.imshow("Face Recognition and logging", imgBackground)
                    cv2.waitKey(1)
                    counter = 1
                    modeType = 1

        if counter != 0:
            if counter == 1:
                # Getting the data
                studentInfo = db.reference(f'Students/{id}').get()
                print(studentInfo)

                # Getting the data from the storage
                blob = bucket.get_blob(f'Images/{id}.png')
                array = np.frombuffer(blob.download_as_string(), np.uint8)
                imgStudent = cv2.imdecode(array, cv2.COLOR_BGR2RGB)

                # Update data of attendance
                datetimeObject = datetime.strptime(studentInfo['Last_attendance_time'],
                                                   "%Y-%m-%d %H:%M:%S")
                secondsElapsed = (datetime.now() - datetimeObject).total_seconds()
                print(secondsElapsed)

                if secondsElapsed > 30:
                    ref = db.reference(f'Students/{id}')
                    studentInfo['attendance'] += 1
                    ref.child('attendance').set(studentInfo['attendance'])
                    ref.child('Last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    # This is the first frame , download the data
                    # Find the info of the student which you get , obv by the id of that student !!
                else:
                    modeType = 3
                    counter = 0
                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

            if modeType != 3:
                if 10 < counter < 20:
                    modeType = 2
                imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

                # To update the attendance , modtype to 0 and 1
                if counter <= 10:
                    cv2.putText(imgBackground, str(studentInfo['attendance']), (861, 125),
                                cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(studentInfo['major']), (1006, 550),
                                cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(id), (1006, 493),
                                cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(studentInfo['Standing']), (910, 625),
                                cv2.FONT_HERSHEY_PLAIN, 1, (100, 100, 100), 1)
                    cv2.putText(imgBackground, str(studentInfo['Year']), (1025, 625),
                                cv2.FONT_HERSHEY_PLAIN, 1, (100, 100, 100), 1)
                    cv2.putText(imgBackground, str(studentInfo['starting_year']), (1125, 625),
                                cv2.FONT_HERSHEY_PLAIN, 1, (100, 100, 100), 1)

                    # Need to take the width of the full name for the division
                    (w, h), _ = cv2.getTextSize(studentInfo['name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                    offset = (414 - w) // 2
                    cv2.putText(imgBackground, str(studentInfo['name']), (808 + offset, 445),
                                cv2.FONT_HERSHEY_PLAIN, 2, (50, 50, 50), 1)

                    imgBackground[175:175 + 216, 909:909 + 216] = imgStudent

                counter += 1

                if counter >= 20:
                    counter = 0
                    modeType = 0
                    studentInfo = []
                    imgStudent = []
                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
    else:
        modeType = 0
        counter = 0
    # cv2.imshow("Webcam", img)
    cv2.imshow("Face Recognition and logging", imgBackground)
    cv2.waitKey(1)
