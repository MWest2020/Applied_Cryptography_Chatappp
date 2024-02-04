import paho.mqtt.client as mqtt
import argparse
import string
import secrets
import json
import base64
from encryption import encrypt_message, decrypt_message, parse_encrypted_message, sign_message, verify_signature

# Stap 1. import voor de asymmetrissche sleuteluitwisseling 
from key_exchange import KeyManager
key_manager = KeyManager()

# TODO: not test message yet
signature = sign_message(key_manager.private_key, test_message)
encoded_signature = base64.b64encode(signature).decode()

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



# print welcome message
print(f"Basic chat started, my client id is: {args.id}")
print("Enter your message (or 'quit' to exit): ")    
    
   
    
def on_message(client, userdata, message):
    try:
        obj = json.loads(message.payload)
        if obj['type'] == 'key_exchange':
            client_id = obj['clientid']
            public_key_pem = obj['public_key']
            key_manager.store_public_key(client_id, public_key_pem)
            key_manager.store_public_key(client_id, public_key_pem)
            print("Current stored public keys:", key_manager.list_stored_public_keys())


        if obj.get('clientid') == args.id:
            return

        if obj.get('type') == 'chat':
            iv, ciphertext, tag = parse_encrypted_message(obj['message'])
            signature = base64.b64decode(obj['signature'])

            print(f"Received Signature: {base64.b64encode(signature).decode()}")


            # Verify signature
            sender_public_key = key_manager.get_public_key(obj['clientid'])
            if sender_public_key and verify_signature(sender_public_key, signature, obj['message']):
                decrypted_msg = decrypt_message(symmetric_key, iv, ciphertext, tag)
                if decrypted_msg:
                    print(f"Decrypted Message received: {decrypted_msg.decode()}")
                else:
                    print("Decryption failed.")
            else:
                print("Signature verification failed.")
    except Exception as e:
        print(f"Error type: {type(e).__name__}, Message: {str(e)}")



def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    print("Connected with result code: " + str(rc))
    client.subscribe("public_keys")
    if rc == 0:
        # Successfully connected
        # Publish the public key
        public_key_pem = key_manager.get_public_key_pem()
        client.publish("public_keys", json.dumps({
            'clientid': args.id,
            'type': 'key_exchange',
            'public_key': public_key_pem.decode()
        }), retain = True) # Retain the public key message !important. DIT DUS NIET VERGETEN
        print(f"Publishing public key for client ID: {args.id}")

        # Subscribe to the topic where public keys are published
        client.subscribe("public_keys")


client = mqtt.Client(args.id)
client.subscribe("public_keys")
# client.subscribe(args.topic)
client.on_connect = on_connect
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

while True:
    data = input("Enter message (or 'quit' to exit): ")
    if data.lower() == 'quit':
        break

    # Encrypt and sign the message
    encrypted_data = encrypt_message(symmetric_key, data)
    signature = sign_message(key_manager.private_key, data)
    encoded_signature = base64.b64encode(signature).decode()
    
    # Log the signature being sent
    print(f"Sending Signature: {encoded_signature}")

    payload = json.dumps({
        'clientid': args.id,
        'type': 'chat',
        'message': encrypted_data,
        'signature': base64.b64encode(signature).decode()
    })
    client.publish(args.topic, payload)

print("Disconnecting...")
client.loop_stop()
# Gracefully sluiten van de MQTT client
client.disconnect()