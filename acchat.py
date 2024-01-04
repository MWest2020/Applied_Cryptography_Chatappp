# pip3 install paho-mqtt
import paho.mqtt.client as mqtt
import argparse
import time
import string
import secrets
import json

# import voor de asymmetrissche sleuteluitwisseling 
from key_exchange import KeyManager

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
    
    
key_manager = KeyManager()
if key_manager:
    print("Generated RSA keypair")
else:
    print("Failed to generate RSA keypair")
    
    
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
            if 'message' in obj and obj['clientid'] != args.id:
                # Voeg hier eventueel versleuteling/ontsleuteling toe
                print(f"Received: '{obj['message']}' from '{obj['clientid']}'")
            else:
                print(f"Received a message from an unknown or untrusted client '{obj['clientid']}'")
    except json.decoder.JSONDecodeError:
        print("Received a non-JSON message")
        return

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
    client.publish(args.topic, json.dumps({
        'clientid': args.id,
        'type': 'chat',
        'message': data
    }))
    print(f"Sent: {data}")

print("Disconnecting...")
client.loop_stop()
# Gracefully sluiten van de MQTT client
client.disconnect()