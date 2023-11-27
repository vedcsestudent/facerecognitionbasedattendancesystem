import cv2
import os
import pickle
import face_recognition
import numpy as np
import cvzone
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
import numpy as np
from datetime import datetime

cred = credentials.Certificate("ServiceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':"https://faceattendancerealtime-fa990-default-rtdb.firebaseio.com/",
    'storageBucket':"faceattendancerealtime-fa990.appspot.com",
})
bucket= storage.bucket()


# code for opening a web cam using python
cap=cv2.VideoCapture(0)
cap.set(3,640)
cap.set(4,480)

#importing the mode and the background
background_image=cv2.imread("Resources/background.png") #background

folderModePath="Resources/Modes"
modePathList=os.listdir(folderModePath)
imgModeList=[]

for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath,path)))#loading all the mode images


#load the encoding file
print("loading encode file")
file=open('EncodeFile.p','rb')
encodeListKnownWithIds=pickle.load(file)
file.close()
encodeListKnown, studentIds=encodeListKnownWithIds
print("loaded encode file")


modetype=0
id=-1
counter =0
imgStudent=[]

while True:
    success,img=cap.read()

    imgS=cv2.resize(img, (0,0),None, 0.25,0.25)
    imgS=cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)


    faceCurFrame=face_recognition.face_locations(imgS)
    encodeCurFrame=face_recognition.face_encodings(imgS,faceCurFrame)


    background_image[162:162+480,55:55+640]=img #the first part is height and the second part is width
    background_image[44:44+633,808:808+414]=imgModeList[modetype]
    
    if faceCurFrame:
        
        for encodeFace,faceLoc in zip(encodeCurFrame,faceCurFrame):
            matches=face_recognition.compare_faces(encodeListKnown,encodeFace)
            facedis=face_recognition.face_distance(encodeListKnown, encodeFace)
       

            matchIndex=np.argmin(facedis)

            if matches[matchIndex]:
                print("known face detected")
                y1,x2,y2,x1=faceLoc
                y1,x2,y2,x1=y1*4,x2*4,y2*4,x1*4
                bbox=55+x1,162+y1,x2-x1,y2-y1
                background_image= cvzone.cornerRect(background_image,bbox,rt=0)
                id=studentIds[matchIndex]

                if counter==0:
                    counter=1
                    modetype=1
                    
                  

        if counter!=0:
            
            if counter==1:
                #get the data
                studentInfo=db.reference(f'Students/{id}').get()
                print(studentInfo)
                #get the  image from the storage
                blob=bucket.get_blob(f'images/{id}.jpeg')
                array= np.frombuffer(blob.download_as_string(),np.uint8)
                imgStudent=cv2.imdecode(array,cv2.COLOR_BGRA2BGR)

                #update data attendance

                datetimeobject=datetime.strptime(studentInfo['last_attendance'],"%Y-%m-%d %H:%M:%S")
                secondsElapsed= (datetime.now()-datetimeobject).total_seconds()
                print(secondsElapsed)
                if secondsElapsed>30:
                    ref=db.reference(f'Students/{id}')
                    studentInfo['total_attendance']+=1
                    ref.child('total_attendance').set(studentInfo['total_attendance'])
                    ref.child('last_attendance').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                else:
                    modetype=3
                    counter=0
                    background_image[44:44+633,808:808+414]=imgModeList[modetype]

            if modetype!=3:
                if 10<counter<20:
                    modetype=2
                background_image[44:44+633,808:808+414]=imgModeList[modetype]
                if counter<=10:
                    cv2.putText(background_image,str(studentInfo['total_attendance']),(861,125),cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),1)
       
                    cv2.putText(background_image,str(studentInfo['major']),(1006,550),cv2.FONT_HERSHEY_COMPLEX,.3,(255,255,255),1)
                    cv2.putText(background_image,str(id),(1006,493),cv2.FONT_HERSHEY_COMPLEX,.5,(255,255,255),1)
                    cv2.putText(background_image,str(studentInfo['standing']),(910,625),cv2.FONT_HERSHEY_COMPLEX,.6,(100,100,100),1)
                    cv2.putText(background_image,str(studentInfo['year']),(1025,625),cv2.FONT_HERSHEY_COMPLEX,.6,(100,100,100),1)
                    cv2.putText(background_image,str(studentInfo['starting_year']),(1125,625),cv2.FONT_HERSHEY_COMPLEX,.6,(100,100,100),1)
                    (w,h),_=cv2.getTextSize(studentInfo['name'],cv2.FONT_HERSHEY_COMPLEX,1,1)
                    offset=(414-w)//2
                    cv2.putText(background_image,str(studentInfo['name']),(808+offset,445),cv2.FONT_HERSHEY_COMPLEX,1,(50,50,50),1)

                    background_image[175:175+225,909:909+225]=imgStudent

       


                counter+=1
                if counter>=20:
                    counter=0
                    modetype=0
                    studentInfo=[]
                    imgStudent=[]
                    background_image[44:44+633,808:808+414]=imgModeList[modetype]
    else:
        modetype=0
        counter=0


    cv2.imshow("background window", background_image)
    cv2.waitKey(1)