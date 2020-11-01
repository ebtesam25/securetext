import face_recognition
import numpy as np

from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from builtins import bytes
import base64
from Crypto import Random

def encrypt(string, password):
    """
    It returns an encrypted string which can be decrypted just by the 
    password.
    """
    key = password_to_key(password)
    IV = make_initialization_vector()
    encryptor = AES.new(key, AES.MODE_CBC, IV)

    # store the IV at the beginning and encrypt
    return IV + encryptor.encrypt(pad_string(string))

def decrypt(string, password):
    key = password_to_key(password)   

    # extract the IV from the beginning
    IV = string[:AES.block_size]  
    decryptor = AES.new(key, AES.MODE_CBC, IV)

    string = decryptor.decrypt(string[AES.block_size:])
    return unpad_string(string)

def password_to_key(password):
    """
    Use SHA-256 over our password to get a proper-sized AES key.
    This hashes our password into a 256 bit string. 
    """
    return SHA256.new(password).digest()
def make_initialization_vector():
   
    return Random.new().read(AES.block_size)

def pad_string(string, chunk_size=AES.block_size):
  
    assert chunk_size  <= 256, 'We are using one byte to represent padding'
    to_pad = (chunk_size - (len(string) + 1)) % chunk_size
    return bytes([to_pad]) + string + bytes([0] * to_pad)
def unpad_string(string):
    to_pad = string[0]
    return string[1:-to_pad]

print(decrypt(b';\xde\xbf\t\xe7\x8f@D \xb0\xae\n\x81iB\xe5"\xba)\x05\t9\xf7\x8a\xd2P5\xdaq9#\xf3', bytes("hello", encoding='utf-8')))

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



image = face_recognition.load_image_file("ebtesam.jpg")
encoding = face_recognition.face_encodings(image)[0]
x = str(encoding)
x = encoding2string(encoding)
print(x)
y = string2encoding(x)



##print(y)
##print(type(y))
print("---------------")
##print(encoding)
print(compare(y, "test.jpg"))
print(compare(y, "test2.jpg"))
