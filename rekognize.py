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
        
        if js['Smile']['Value']:
            print("smiling")
        else:
            print("not smiling")
        print("---------------------")
        if js['EyesOpen']['Value']:
            print("no blink")
        else:
            print("blink")
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
            
                

##        print (js["
    return len(response['FaceDetails'])



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

face_count=detect_faces(sourceFile, bucket)
print("Faces detected: " + str(face_count))



##client=boto3.client('rekognition')
##
##found = 0
##for target in targetFiles:
##
##    response=client.compare_faces(SimilarityThreshold=85, SourceImage={'S3Object':{'Bucket':bucket,'Name':sourceFile}}, TargetImage={'S3Object':{'Bucket':bucket,'Name':target}})
##
##    for faceMatch in response['FaceMatches']:
##            position = faceMatch['Face']['BoundingBox']
##            confidence = str(faceMatch['Face']['Confidence'])
####            print('The face at ' +
####                       str(position['Left']) + ' ' +
####                       str(position['Top']) +
####                       ' matches with ' + confidence + '% confidence')
####            print('\n recognized file is ' + target)
##            ##print(json.dumps({"match": target, "confidence": confidence}, sort_keys=False))
##            print(target[:-4])
##            found = 1
##            break
##    if found==1:
##        break
##
##
##if found==0:
##    ##print(json.dumps({"match": "none", "confidence": 0}, sort_keys=False))
##    print('none')
##  
		   

		   
obj = s3.Object("hacktober2020", sourceFile)
obj.delete()
