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
    
    
    
# Maak een instantie van KeyManager om de sleutels uit te wissselen en op te slaan
key_manager = KeyManager()  
    
# on message handler
def on_message(client, userdata, message):
    try:
        obj = json.loads(message.payload)
        
        # Controleer op de aanwezigheid van een publieke sleutel
        if 'public_key' in obj and 'clientid' in obj:
            key_manager.store_public_key(obj['clientid'], obj['public_key'])
            print(f"Received public key from {obj['clientid']}")
            return
    except json.decoder.JSONDecodeError:
        print("Received a non-JSON message")
        return

    if not 'clientid' in obj or obj['clientid'] == args.id:
        # Negeer berichten zonder client ID of berichten verzonden door mezelf
        return

    if 'message' in obj:
        if key_manager.get_public_key(obj['clientid']):
            # Verwerk het bericht alleen als de publieke sleutel bekend is
            print(f"Received: '{obj['message']}' from '{obj['clientid']}'")
        else:
            print(f"Received a message from an unknown or untrusted client '{obj['clientid']}'")
    else:
        print(f"Received a message without text from '{obj['clientid']}'")


# create MQTT client
client = mqtt.Client(args.id)
client.on_message=on_message
client.connect(args.host)
client.loop_start()

# aanmaken pubkey en versturen
public_key_pem = key_manager.get_public_key_pem()
client.publish(args.topic, json.dumps({
    'clientid': args.id,
    'public_key': public_key_pem.decode()
}))

client.subscribe(args.topic)

# start an endless loop and wait for input on the commandline
# publish all messages as a JSON object and stop when the input is 'quit'
while True:
    data = input()
    if data == 'quit':
        print("Stopping application")
        break

    print(f"Sending: `{data}`")
    
    # publish a message to the chat
    client.publish(args.topic,json.dumps({
        'clientid':args.id,
        'message':data
    }))


# terminate the MQTT client loop
client.loop_stop()
    