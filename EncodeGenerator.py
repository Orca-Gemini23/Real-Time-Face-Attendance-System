import cv2
import face_recognition
import os
import pickle
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

# Importing the students images  !!
folderPath = 'Images'
pathList = os.listdir(folderPath)
print(pathList)
imgList = []
studentIds = []

# For the firebase:
cred = credentials.Certificate("serviceAccount.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://faceattendancert-a83d1-default-rtdb.firebaseio.com/",
    'storageBucket': "faceattendancert-a83d1.appspot.com"
})
# Now we want to student directory , we gonna have ids and required information

for path in pathList:
    imgList.append(cv2.imread(os.path.join(folderPath, path)))
    # print(path)
    # print(os.path.splitext(path)[0])
    studentIds.append(os.path.splitext(path)[0])
    # To remove the number before the extension and to print the student ids

    # Sending the images to the databases;
    fileName = f'{folderPath}/{path}' # Getting the file name
    # Create a folder called images and that add the images in that folder
    bucket = storage.bucket()
    blob = bucket.blob(fileName)
    blob.upload_from_filename(fileName)

print(len(imgList))


def findEncodings(imagesList):
    encodeList = []
    # loop through every image and encode every one of them
    # Encoding : Change color first
    for img in imagesList:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # find the encodings
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList


print("Encoding started .. ")
encodeListKnown = findEncodings(imgList)

# case : we need to see which id is linked with which code :
encodeListKnownWithIds = [encodeListKnown, studentIds]
print("Encoding completed")

file = open("EncodeFile.p", 'wb')
# dump the list in the file
pickle.dump(encodeListKnownWithIds, file)
file.close()
print("File saved")
