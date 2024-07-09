import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccount.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://faceattendancert-a83d1-default-rtdb.firebaseio.com/"
    # Now we want to student directory , we gonna have ids and required information
})

ref = db.reference('Students')

# Adding data
data = {
    # giving in values
    "123": {
        "name": "Nordibek Ab",
        "major": "Chess",
        "starting_year": 2016,
        "attendance": 7,
        "Standing": "G",
        "Year": 4,
        "Last_attendance_time": "2023-12-06 00:54:34"
    },

    "456": {
        "name": "Verstappen",
        "major": "F1",
        "starting_year": 2017,
        "attendance": 3,
        "Standing": "D",
        "Year": 4,
        "Last_attendance_time": "2023-12-06 00:54:36"
    },
    "789": {
        "name": "Narendra Modi",
        "major": "Politics",
        "starting_year": 2014,
        "attendance": 10,
        "Standing": "E",
        "Year": 5,
        "Last_attendance_time": "2023-12-06 00:53:42"
    }
}

# Sending data
for key, value in data.items():
    ref.child(key).set(value)