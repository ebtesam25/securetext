from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os
import json

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

##with open('public_key.pem', 'wb') as f:
##    f.write(pem)

print(pempub)


private_key = serialization.load_pem_private_key(
        pempri,
        password=None,
        backend=default_backend()
    )

public_key = serialization.load_pem_public_key(
        pempub,
        backend=default_backend()
    )

message = "the secret goes here".encode()

encrypted = public_key.encrypt(
    message,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
)


print(type(encrypted))

original_message = private_key.decrypt(
    encrypted,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
)


print(original_message.decode())

print("-----------------")

print(os.urandom(16))



password = "passwordddd".encode()

salt = "thesaltishere".encode()
kdf = PBKDF2HMAC(
     algorithm=hashes.SHA256(),
     length=32,
     salt=salt,
     iterations=100000,
     backend=default_backend()
 )
key = base64.urlsafe_b64encode(kdf.derive(password))
f = Fernet(key)
message = pempri
token = f.encrypt(pempri)
token = token.decode()
print(token)
print(type(token))
tk = token
token = tk.encode()
poken = f.decrypt(token)
print (poken.decode())

print("--------------------xxxxxxxxxxx")
payload = {}
payload["uid"] = "eee"
payload["cipherpvtkey"] = tk

print (json.dumps(payload))

