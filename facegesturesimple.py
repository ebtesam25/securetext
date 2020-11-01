import boto3
import json
import numpy as np
import time
import sys
##import cv2

##image capture and preprocess with opencv
##time.sleep(4)
##cap = cv2.VideoCapture(1)
##ret, img = cap.read()
##cv2.imwrite('capture.png',img)
##cap.release()
##time.sleep(4)



def downloadpic(pic_url):
    

    with open('pic1.jpg', 'wb') as handle:
            response = requests.get(pic_url, stream=True)

            if not response.ok:
                print (response)

            for block in response.iter_content(1024):
                if not block:
                    break

                handle.write(block)


def detect_faces(photo, bucket):

    client=boto3.client('rekognition')

    response = client.detect_faces(Image={'S3Object':{'Bucket':bucket,'Name':photo}},Attributes=['ALL'])

    print('Detected faces for ' + photo)    
    for faceDetail in response['FaceDetails']:
        print('The detected face is between ' + str(faceDetail['AgeRange']['Low']) 
              + ' and ' + str(faceDetail['AgeRange']['High']) + ' years old')
        print('Here are the other attributes:')
        js = json.dumps(faceDetail, indent=4, sort_keys=True)
        print(js)
        js = json.loads(js)
        print(js)

        gesture = ""
        
        if js['Smile']['Value']:
            print("smiling")
            gesture = gesture + "facegesturesmile"
            
        else:
            print("not smiling")
        print("---------------------")
        if js['EyesOpen']['Value']:
            print("no blink")
        else:
            print("blink")
            gesture = gesture + "facegestureblink"
            
        print("---------------------")
        rightup = 0
        leftup = 0
        leftdown = 0
        rightdown = 0
        for l in js["Landmarks"]:
            if l["Type"] == "leftEyeUp":
                leftup = l["Y"]
            if l["Type"] == "leftEyeDown":
                leftdown = l["Y"]
            if l["Type"] == "rightEyeUp":
                rightup = l["Y"]
            if l["Type"] == "rightEyeDown":
                rightdown = l["Y"]

        diffleft = leftdown - leftup
        diffright = rightdown - rightup

        print (diffleft)
        print (diffright)

    return len(response['FaceDetails']), gesture



s3 = boto3.resource('s3')

infilename = sys.argv[1]


##for bucket in s3.buckets.all():
##    print(bucket.name)


bucket='hacktober2020'
mybucket = s3.Bucket(bucket)
targetFiles = []
for object in mybucket.objects.all():
    print(object.key)
    targetFiles.append(object.key)

##name of the source file	
sourceFile=infilename

data = open(sourceFile, 'rb')
s3.Bucket('hacktober2020').put_object(Key=sourceFile, Body=data)



##targetFile='peter.jpg'

##targetFiles = ['chris.jpg', 'peter.jpg']

face_count, gesture=detect_faces(sourceFile, bucket)
print(gesture)
print("Faces detected: " + str(face_count))

		   
obj = s3.Object("hacktober2020", sourceFile)
obj.delete()
