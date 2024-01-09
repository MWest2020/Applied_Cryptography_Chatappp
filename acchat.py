# pip3 install paho-mqtt
import paho.mqtt.client as mqtt
import argparse
import time
import string
import secrets
import json
import os


# importeer de encryptifuncties
import encryption

# Stap 1. import voor de asymmetrissche sleuteluitwisseling 
from key_exchange import KeyManager

# Stap 2 genereren van een symmetrische sleutel voor het berichtverkeer.
symmetric_key = os.urandom(32) # 32 bytes = 256 bits


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

        # Negeer berichten die ik zelf heb verzonden
        if obj.get('clientid') == args.id:
            return
     
       
        # Controleer of het bericht een sleuteluitwisselingsbericht is
        if obj.get('type') == 'key_exchange':
            if 'public_key' in obj and 'clientid' in obj:
                key_manager.store_public_key(obj['clientid'], obj['public_key'])
                print(f"Received public key from {obj['clientid']}")
            return

        # Verwerk chatberichten
        elif obj.get('type') == 'chat':
            encrypted_msg = obj['message']
            print(f"Received encrypted message: {encrypted_msg}")
            # Ontsleutel het bericht
            decrypted_msg = encryption.decrypt_message(symmetric_key, encrypted_msg)
            print(f"Received: '{decrypted_msg}' from '{obj['clientid']}'")
    
    except Exception as e:
        print(f"Error: {e}")

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

    # Verstuur een chatbericht
    #versleutel het bericht hier
    encrypted_data = encryption.encrypt_message(symmetric_key, data)
    print(f"Encrypted message: {encrypted_data}")
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