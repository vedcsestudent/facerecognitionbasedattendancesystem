import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("ServiceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':"https://faceattendancerealtime-fa990-default-rtdb.firebaseio.com/",
})

ref=db.reference('Students')
data={
    "111":{
        "name":"Ved Prakash Jaiswal",
        "major":"Computer Science",
        "starting_year":2020,
        "total_attendance":70,
        "standing":"G",
        "year":4,
        "last_attendance":"2023-11-27 00:54:34",
    },
     "222":{
        "name":"Elon Musk",
        "major":"Physics",
        "starting_year":2020,
        "total_attendance":50,
        "standing":"G",
        "year":3,
        "last_attendance":"2023-11-27 00:54:34",
    },
     "333":{
        "name":"Harry",
        "major":"Computer Science",
        "starting_year":2020,
        "total_attendance":80,
        "standing":"G",
        "year":4,
        "last_attendance":"2023-11-27 00:54:34",
    },

}
for key, value in data.items():
    ref.child(key).set(value)