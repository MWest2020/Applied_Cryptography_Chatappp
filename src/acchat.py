import paho.mqtt.client as mqtt
import argparse
import string
import secrets
import json
import os
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

# Encryption and Decryption functions
def encrypt_message(key, plaintext):
    iv = os.urandom(12)
    encryptor = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend()).encryptor()
    ciphertext = encryptor.update(plaintext.encode()) + encryptor.finalize()
    return base64.b64encode(iv + ciphertext + encryptor.tag).decode('utf-8')

def decrypt_message(key, iv, ciphertext, tag):
    decryptor = Cipher(algorithms.AES(key), modes.GCM(iv, tag), backend=default_backend()).decryptor()
    return decryptor.update(ciphertext) + decryptor.finalize()

def parse_encrypted_message(encrypted_message):
    decoded_message = base64.b64decode(encrypted_message)
    iv = decoded_message[:12]
    tag = decoded_message[-16:]
    ciphertext = decoded_message[12:-16]
    return iv, ciphertext, tag


# Stap 1. import voor de asymmetrissche sleuteluitwisseling 
from key_exchange import KeyManager

# Stap 2 genereren van een symmetrische sleutel voor het berichtverkeer.
# symmetric_key = os.urandom(32) # 32 bytes = 256 bits

# Dit werkt nog niet met een random key, omdat exchange 1 en 2 een andere key aanmaken. (normaal zou ik een databse gebruken o.i.d , maar gaat te ver)
symmetric_key = b"12345678901234567890123456789012"


# parse arguments
parser = argparse.ArgumentParser(description='Basic chat application')
parser.add_argument('--host', help='Hostname of the MQTT service, i.e. test.mosquitto.org', required=True)
parser.add_argument('--topic', help="MQTT chat topic (default '/acchat')", default='/acchat', required=False)
parser.add_argument('--id', help="MQTT client identifier (default, a random string)", required=False)
args = parser.parse_args()

# generate a random client id if nothing is provided
if args.id is None:
    alphabet = string.ascii_letters + string.digits
    args.id = ''.join(secrets.choice(alphabet) for i in range(8))

key_manager = KeyManager()
if key_manager:
    print("Generated RSA keypair")
else:
    print("Failed to generate RSA keypair")

# print welcome message
print(f"Basic chat started, my client id is: {args.id}")
print("Enter your message (or 'quit' to exit): ")    
    
    
    
    
def on_message(client, userdata, message):
    try:
        obj = json.loads(message.payload)

        if obj.get('clientid') == args.id:
            return

        if obj.get('type') == 'chat':
            iv, ciphertext, tag = parse_encrypted_message(obj['message'])
            decrypted_msg = decrypt_message(symmetric_key, iv, ciphertext, tag).decode('utf-8')
            print(f"Received: '{decrypted_msg}' from '{obj['clientid']}'")
    except Exception as e:
        print(f"Error type: {type(e).__name__}, Message: {str(e)}")




client = mqtt.Client(args.id)
client.on_message = on_message
client.connect(args.host)
client.loop_start()

# Verstuur de publieke sleutel als een apart bericht
public_key_pem = key_manager.get_public_key_pem()
client.publish("public_keys", json.dumps({
    'clientid': args.id,
    'type': 'key_exchange',
    'public_key': public_key_pem.decode()
}))

client.subscribe(args.topic)

while True:
    data = input()
    if data.lower() == 'quit':
        break

    encrypted_data = encrypt_message(symmetric_key, data)
    client.publish(args.topic, json.dumps({
        'clientid': args.id,
        'type': 'chat',
        'message': encrypted_data
    }))
    print(f"Sent: {data}")

print("Disconnecting...")
client.loop_stop()
# Gracefully sluiten van de MQTT client
client.disconnect()