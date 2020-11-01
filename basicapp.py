from flask import Flask, request, redirect, session, url_for, Response, json, render_template, send_from_directory
from werkzeug.utils import secure_filename
from flask.json import jsonify
import json
import os
import random
import time
import requests
from pymongo import MongoClient
from pprint import pprint
from flask_cors import CORS
import boto3
import numpy as np
import sys
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import face_recognition
import numpy as np



from bson import ObjectId

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


with open('credentials.json', 'r') as f:
    creds = json.load(f)

mongostr = creds["mongostr"]
client = MongoClient(mongostr)
# response = model.predict_by_url('@@sampleTrain')


db = client["securetext"]


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config.from_object(__name__)
CORS(app)


def genkeypair():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()

    pempri = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    ##with open('private_key.pem', 'wb') as f:
    ##    f.write(pem)

    pempri = pempri.decode()
    print(type(pempri))
    print(pempri)
    print("--------------------")
    pempri = pempri.encode()
    print(pempri)
    print("--------------------")

    pempub = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    pempri = pempri.decode()
    pempub = pempub.decode()

    return pempri, pempub


def symencrypt(plaintext, code1, code2):

    password = "passwordddd".encode()

    salt = "thesaltishere".encode()

    password = code1.encode()
    salt = code2.encode()
    
    kdf = PBKDF2HMAC(
         algorithm=hashes.SHA256(),
         length=32,
         salt=salt,
         iterations=100000,
         backend=default_backend()
     )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    f = Fernet(key)
    message = plaintext
    token = f.encrypt(message)
    token = token.decode()
    return token


def symdecrypt(ciphertext, code1, code2):

    password = "passwordddd".encode()

    salt = "thesaltishere".encode()

    password = code1.encode()
    salt = code2.encode()
    
    kdf = PBKDF2HMAC(
         algorithm=hashes.SHA256(),
         length=32,
         salt=salt,
         iterations=100000,
         backend=default_backend()
     )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    f = Fernet(key)
    message = ciphertext.encode()

    poken = f.decrypt(message)
    print (poken.decode())
    return poken.decode()

def asymencrypt(pempub, plaintext):
    private_key = serialization.load_pem_private_key(
            pempri,
            password=None,
            backend=default_backend()
        )

    pempub = pempub.encode()

    public_key = serialization.load_pem_public_key(
            pempub,
            backend=default_backend()
        )

    message = plaintext.encode()

    encrypted = public_key.encrypt(
        message,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    return encrypted.decode()


def asymdecrypt(pempri, ciphertext):
    pempri = pempri.encode()
    private_key = serialization.load_pem_private_key(
        pempri,
        password=None,
        backend=default_backend()
    )

    encrypted = ciphertext.encode()

    original_message = private_key.decrypt(
        encrypted,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    return original_message.decode()

def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)

def compare(encoding, path):
    
    unknown_image = face_recognition.load_image_file(path)
    
    
    unknown_encoding = face_recognition.face_encodings(unknown_image)[0]
    results = face_recognition.compare_faces([encoding], unknown_encoding)
    return results[0]

def encoding2string(encoding):
    return str(encoding)

def string2encoding(x):
    x = x.replace('[', '')
    x = x.replace(']', '')
    l = x.split(" ")
    z = []
    for i in l:
        if not hasNumbers(i):
            continue
        i = i.strip()
##        print (i)
        ##print(len(i))
        z.append(float(i))
    return np.array(z)

def getfaceencoding(filename):
    image = face_recognition.load_image_file(filename)
    encoding = face_recognition.face_encodings(image)[0]
    x = encoding2string(encoding)
    print(x)
    return x

def comparefaceencodings(e1, e2)    
    y = string2encoding(e1)
    z = string2encoding(e2)

    results = face_recognition.compare_faces([y], [z])
    return results[0]


def downloadpic(pic_url):
    

    with open('pic1.jpg', 'wb') as handle:
            response = requests.get(pic_url, stream=True)

            if not response.ok:
                print (response)

            for block in response.iter_content(1024):
                if not block:
                    break

                handle.write(block)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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




@app.route("/file_upload", methods=["POST"])
def fileupload():

    if 'file' not in request.files:
          return "No file part"
    file = request.files['file']
    # if user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
      return "No selected file"
    if file and allowed_file(file.filename):
        UPLOAD_FOLDER = "./uploads"
  
        filename = secure_filename(file.filename)
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        uploadtogcp(os.path.join(UPLOAD_FOLDER, filename))
        return 'file uploaded successfully'
    
    return 'file not uploaded successfully'





@app.route("/file_analysis", methods=["POST"])
def fileanalysis():

    if 'file' not in request.files:
          return "No file part"
    file = request.files['file']
    # if user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
      return "No selected file"
    if file and allowed_file(file.filename):
        UPLOAD_FOLDER = "./uploads"
  
        filename = secure_filename(file.filename)
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        # uploadtogcp(os.path.join(UPLOAD_FOLDER, filename))
        with open(os.path.join(UPLOAD_FOLDER, filename), 'rb') as ff:
            content = ff.read()

        project_id = '127305337349'
        model_id = 'ICN2229277417501884416'

        result = get_prediction(content, project_id, model_id)

        print (result.payload[0].display_name)

        return result.payload[0].display_name
    
    return 'file not uploaded successfully'



@app.route("/pill_analysis2", methods=["POST"])
def pillanalysis2():

    print(request.data)
    res = request.get_json()
    print (res)


    pic_url = res["imgurl"]


    if pic_url is not None:    
        
        # UPLOAD_FOLDER = "./uploads"

        downloadpic(pic_url)
  
        # filename = secure_filename(file.filename)
        # file.save(os.path.join(UPLOAD_FOLDER, filename))
        # uploadtogcp(os.path.join(UPLOAD_FOLDER, filename))
        
        # with open(os.path.join(UPLOAD_FOLDER, filename), 'rb') as ff:
        #     content = ff.read()
        filename = "pic1.jpg"
        with open((filename), 'rb') as ff:
            content = ff.read()

        project_id = '127305337349'
        model_id = 'ICN7331299442429001728'

        result = get_prediction(content, project_id, model_id)

        print (result.payload[0].display_name)

        resname = result.payload[0].display_name

        resjson = {}
        resjson["result"] = resname

        resp = Response(resjson, status=200, mimetype='application/json')
        ##resp.headers['Link'] = 'http://google.com'

        return resp
    else :
        resjson = {}
        resjson["result"] = "IMAGE URL EMPTY"

        resp = Response(resjson, status=200, mimetype='application/json')

        # return result.payload[0].display_name
    print ("file not uploaded successfully")
    return 'file not uploaded successfully'



@app.route("/dummyJson", methods=['GET', 'POST'])
def dummyJson():

    print(request)

    res = request.get_json()
    print (res)

    resraw = request.get_data()
    print (resraw)

##    args = request.args
##    form = request.form
##    values = request.values

##    print (args)
##    print (form)
##    print (values)

##    sres = request.form.to_dict()
 

    status = {}
    status["server"] = "up"
    status["message"] = "some random message here"
    status["request"] = res 

    statusjson = json.dumps(status)

    print(statusjson)

    js = "<html> <body>OK THIS WoRKS</body></html>"

    resp = Response(statusjson, status=200, mimetype='application/json')
    ##resp.headers['Link'] = 'http://google.com'

    return resp


@app.route("/testdata", methods=['GET', 'POST'])
def testdata():

    ts = str(int(time.time()))
    ##res = request.json
    # args = request.args
    form = request.form
    # print(args)
    print (form.get('temperature'))
    print (form.get('humidity'))
    print (form.get('pressure'))
    print (form.get('steps'))

    col = db.readings
    payload = {}
    payload['ts'] = ts
    payload['humid'] = form.get('humidity')
    payload['press'] = form.get('pressure')
    payload['tempout'] = form.get('temperature')
    print (payload)

    result=db.readings.insert_one(payload)

    print(result)

    col = db.steps
    area  = col.find_one({"status": "current"})
    oldpop = float(area["steps"])
    newpop = oldpop+float(form.get('steps'))
    col.update_one({"status":"current"}, {"$set":{"steps":str(newpop)}})
    payload = {}
    payload['ts'] = ts
    payload['steps'] = str(newpop)
    print (payload)

    result=db.allsteps.insert_one(payload)
    print(result)



    js = "<html> <body>OK THIS WoRKS</body></html>"

    resp = Response(js, status=200, mimetype='text/html')
    ##resp.headers['Link'] = 'http://google.com'

    return resp


@app.route("/putdata2", methods=['GET', 'POST'])
def putdata2():

    ts = str(int(time.time()))
    ##res = request.json
    # args = request.args
    form = request.form
    # print(args)
    print (form.get('USERID'))
    print (form.get('GSR'))
    print (form.get('steps'))

    col = db.creadings2
    payload = {}
    payload['ts'] = ts
    payload['userid'] = form.get('USERID')
    payload['gsr'] = form.get('GSR')
    payload['steps'] = form.get('steps')
    print (payload)

    superpayload = {}

    superpayload["patient"] = form.get('patient')
    superpayload["doctor"] = form.get('doctor')
    superpayload["record"] = payload
    print ("testing")
    fileId = hederainsert(superpayload)
    payload["fileId"] = fileId

    result=col.insert_one(payload)

    payload = {}
    col = db.readingchain
    payload["ts"] = ts
    payload['fileId'] = fileId
    result=col.insert_one(payload)


    col = db.currentreadings
    area  = col.find_one({"status": "current"})
    oldgsr = float(area["gsr"])
    newgsr = (oldgsr + float(form.get('GSR')))/2.0
    oldsteps =  float(area["steps"])
    newsteps = oldsteps+float(form.get('steps'))
    col.update_one({"status":"current"}, {"$set":{"gsr":str(newgsr)}})
    col.update_one({"status":"current"}, {"$set":{"steps":str(newsteps)}})
    area  = col.find_one({"status": "current"})
    superpayload = {}
    superpayload["patient"] = form.get('patient')
    superpayload["doctor"] = form.get('doctor')
    area = JSONEncoder().encode(area)
    superpayload["record"] = area

    fileId = hederainsert(superpayload) 

    col.update_one({"status":"current"}, {"$set":{"fileId":fileId}})

    # oldpop = float(area["steps"])
    # newpop = oldpop+float(form.get('steps'))
    # col.update_one({"status":"current"}, {"$set":{"steps":str(newpop)}})
    # payload = {}
    # payload['ts'] = ts
    # payload['steps'] = str(newpop)
    # print (payload)

    retjson = {}

    retjson['fileId'] = fileId
    retjson['mongoresult'] = "successfully added"

    print(retjson)



    js = "<html> <body>OK THIS WoRKS</body></html>"

    resp = Response(js, status=200, mimetype='text/html')
    ##resp.headers['Link'] = 'http://google.com'

    return resp


@app.route("/putdata", methods=['GET', 'POST'])
def putdata():

    ts = str(int(time.time()))
    ##res = request.json
    # args = request.args
    form = request.form
    # print(args)
    print (form.get('USERID'))
    print (form.get('HR'))
    print (form.get('spo2'))
    print (form.get('temp'))

    col = db.creadings
    payload = {}
    
    payload["userid"] = form.get('USERID')
    payload["pulse"] = form.get('HR')
    payload["spo2"] = form.get('spo2')
    payload["temp"] = form.get('temp')
    payload["ts"] = ts
    superpayload = {}

    superpayload["patient"] = form.get('patient')
    superpayload["doctor"] = form.get('doctor')
    superpayload["record"] = payload
    print ("testing")
    fileId = hederainsert(superpayload)
    payload["fileId"] = fileId

    result=col.insert_one(payload)

    payload = {}
    col = db.readingchain
    payload["ts"] = ts
    payload['fileId'] = fileId
    result=col.insert_one(payload)


    col = db.currentreadings
    area  = col.find_one({"status": "current"})
    oldpulse = float(area["pulse"])
    newpulse = (oldpulse + float(form.get('HR')))/2.0
    oldspo2 =  float(area["spo2"])
    newspo2 = (oldspo2 + float(form.get('spo2')))/2.0
    col.update_one({"status":"current"}, {"$set":{"pulse":str(newpulse)}})
    col.update_one({"status":"current"}, {"$set":{"spo2":str(newspo2)}})
    area  = col.find_one({"status": "current"})
    superpayload = {}
    superpayload["patient"] = form.get('patient')
    superpayload["doctor"] = form.get('doctor')
    area = JSONEncoder().encode(area)
    superpayload["record"] = area

    fileId = hederainsert(superpayload) 

    col.update_one({"status":"current"}, {"$set":{"fileId":fileId}})

    # oldpop = float(area["steps"])
    # newpop = oldpop+float(form.get('steps'))
    # col.update_one({"status":"current"}, {"$set":{"steps":str(newpop)}})
    # payload = {}
    # payload['ts'] = ts
    # payload['steps'] = str(newpop)
    # print (payload)

    retjson = {}

    retjson['fileId'] = fileId
    retjson['mongoresult'] = "successfully added"

    print(retjson)

    js = "<html> <body>OK THIS WoRKS</body></html>"

    resp = Response(js, status=200, mimetype='text/html')
    ##resp.headers['Link'] = 'http://google.com'

    return resp


@app.route("/getcurrent")

def getcurrent():
    col = db.currentreadings
    area  = col.find_one({"status": "current"})
    fileId = area["fileId"]

    area = JSONEncoder().encode(area)
    retjson = {}
    print (area)
    retjson['data'] = area
    retjson['fileId'] = fileId

    print(retjson)

    js = "<html> <body>OK THIS WoRKS</body></html>"

    resp = Response(json.dumps(retjson), status=200, mimetype='application/json')
    ##resp.headers['Link'] = 'http://google.com'

    return resp

@app.route("/testdata2", methods=['GET', 'POST'])
def testdata2():

    ts = str(int(time.time()))
    ##res = request.json
    # args = request.args
    form = request.form
    # print(args)
    print (form.get('BPM'))
    print (form.get('OX'))
    print (form.get('GSR'))
    print (form.get('temperature'))

    col = db.readings
    payload = {}
    payload['ts'] = ts
    payload['gsr'] = form.get('GSR')
    payload['ox'] = form.get('OX')
    payload['pulse'] = form.get('BPM')
    payload['tempint'] = form.get('temperature')
    print (payload)

    result=db.internal.insert_one(payload)

    print(result)

    col = db.ox
    area  = col.find_one({"status": "current"})
    oldpop = float(area["ox"])
    newpop = float(form.get('OX'))
    col.update_one({"status":"current"}, {"$set":{"ox":str(newpop)}})
    payload = {}
    payload['ts'] = ts
    payload['ox'] = str(newpop)
    print (payload)

    result=db.ox.insert_one(payload)
    print(result)

    col = db.heartrates
    area  = col.find_one({"status": "current"})
    oldpop = float(area["pulse"])
    newpop = float(form.get('BPM'))
    col.update_one({"status":"current"}, {"$set":{"pulse":str(newpop)}})
    payload = {}
    payload['ts'] = ts
    payload['pulse'] = str(newpop)
    print (payload)

    result=db.heartrates.insert_one(payload)
    print(result)



    js = "<html> <body>OK THIS WoRKS</body></html>"

    resp = Response(js, status=200, mimetype='text/html')
    ##resp.headers['Link'] = 'http://google.com'

    return resp


@app.route("/dummy", methods=['GET', 'POST'])
def dummy():

    ##res = request.json

    js = "<html> <body>OK THIS WoRKS</body></html>"

    resp = Response(js, status=200, mimetype='text/html')
    ##resp.headers['Link'] = 'http://google.com'

    return resp

@app.route("/api", methods=["GET"])
def index():
    if request.method == "GET":
        return {"hello": "world"}
    else:
        return {"error": 400}


if __name__ == "__main__":
    app.run(debug=True, host = 'localhost', port = 8002)
    # app.run(debug=True, host = '45.79.199.42', port = 8002)
