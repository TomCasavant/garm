import base64
import hashlib
import urllib.parse

import requests
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from flask import json
from datetime import datetime
import datetime as dt
from cryptography.hazmat.primitives import serialization as crypto_serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend as crypto_default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization

def generate_key_pair():
    """
    Generate a key pair
    """
    key = rsa.generate_private_key(
        backend=crypto_default_backend(),
        public_exponent=65537,
        key_size=2048
    )

    private_key = key.private_bytes(
        crypto_serialization.Encoding.PEM,
        crypto_serialization.PrivateFormat.PKCS8,
        crypto_serialization.NoEncryption())

    public_key = key.public_key().public_bytes(
        crypto_serialization.Encoding.PEM,
        crypto_serialization.PublicFormat.SubjectPublicKeyInfo
    )

    return private_key, public_key

def create_digest(message_json):
    # Serialize the message with sorted keys to ensure consistent formatting
    digest = base64.b64encode(hashlib.sha256(message_json.encode('utf-8')).digest())
    return digest


def sign_and_send(message, private_key_blob, recipient_inbox, sender_key):
    print("SIGN AND SEND")
    message_json = json.dumps(message)
    print(f"MESSAGE JSON\n\n{message_json}")
    digest = create_digest(message_json)
    message = json.loads(message_json)
    print(f"MESSAGE\n\n{message}")

    # Parse the recipient's inbox URL
    print(f"Recipient Inbox: {recipient_inbox}")
    parsed = urllib.parse.urlparse(recipient_inbox)
    recipient_host = parsed.netloc
    recipient_path = parsed.path

    current_date = datetime.now(dt.timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')
    print(f"Recipient Path: {recipient_path} + type: {type(recipient_path)}")
    print(f"Recipient Host: {recipient_host} + type: {type(recipient_host)}")
    print(f"Current Date: {current_date} + type: {type(current_date)}")
    signature_text = b'(request-target): post %s\ndigest: SHA-256=%s\nhost: %s\ndate: %s' % ( recipient_path.encode('utf-8'), digest, recipient_host.encode('utf-8'), current_date.encode('utf-8'))

    private_key = serialization.load_pem_private_key(private_key_blob, password=None, backend=crypto_default_backend())

    # Sign the signature text
    raw_signature = private_key.sign(
        signature_text,
        padding.PKCS1v15(),
        hashes.SHA256()
    )

    # Create the signature header
    signature_header = 'keyId="%s",algorithm="rsa-sha256",headers="(request-target) digest host date",signature="%s"' % (
        sender_key,
        base64.b64encode(raw_signature).decode('utf-8')
    )

    # Prepare headers for the request
    headers = {
        'Date': current_date,
        'Content-Type': 'application/activity+json',
        'Host': recipient_host,
        'Digest': "SHA-256=" + digest.decode('utf-8'),
        'Signature': signature_header
    }

    # Send the request
    r = requests.post(recipient_inbox, headers=headers, json=message)

    print(f"Response: {r.status_code} {r.text}")
    return r


def verification_testing(actor_url, raw_signature, signature_text):

    # Fetch the actor's public key from the actor URL
    public_key_response = requests.get(actor_url, headers={'Accept': 'application/activity+json'})

    if public_key_response.status_code != 200:
        print(f"Failed to retrieve public key: {public_key_response.status_code} {public_key_response.text}")
        return

    public_key_json = public_key_response.json()

    # Extract the public key in PEM format
    public_key_pem = public_key_json['publicKey']['publicKeyPem']

    # Load the public key
    public_key = serialization.load_pem_public_key(
        public_key_pem.encode(),
        backend=default_backend()
    )

    # Verify the signature
    try:
        public_key.verify(
            raw_signature,
            signature_text,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        print("Signature verification successful")
    except Exception as e:
        print(f"Signature verification failed: {e}")
