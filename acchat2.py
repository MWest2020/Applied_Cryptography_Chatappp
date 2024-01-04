# pip3 install paho-mqtt
import paho.mqtt.client as mqtt
import argparse
import time
import string
import secrets
import json
# check if os.urandom mag volgens studiegids / veilig genoeg is
import os
# encryptie voor de chat
import message_encryption 

parser = argparse.ArgumentParser(description='Basic chat application')
parser.add_argument('--host', help='Hostname of the MQTT service, i.e. test.mosquitto.org', required=True)
parser.add_argument('--topic', help="MQTT chat topic (default '/acchat')", default='/acchat', required=False)
parser.add_argument('--id', help="MQTT client identifier (default, a random string)", required=False)
args = parser.parse_args()

if args.id is None:
    alphabet = string.ascii_letters + string.digits
    args.id = ''.join(secrets.choice(alphabet) for i in range(8))

print(f"Basic chat started, my client id is: {args.id}")


# sleutelgeneratie voor de chat
key = os.urandom(32) # 32 bytes voor AES256
   
# on message handler
def on_message(client, userdata, message):
    try:
        obj = json.loads(message.payload.decode())
        if 'clientid' in obj and 'iv' in obj and 'message' in obj:
            if obj['clientid'] != args.id:  # Negeer berichten die ik zelf heb verzonden
                iv = bytes.fromhex(obj['iv'])
                ct = bytes.fromhex(obj['message'])
                print(f"Converted IV (bytes): {iv}")
                print(f"Converted encrypted message (bytes): {ct}")
                decrypted_message = message_encryption.decrypt_message(iv, ct, key)
                print(f"Decrypted message: {decrypted_message}")
                print(f"Received from {obj['clientid']}: {decrypted_message}")
    
    
    except json.JSONDecodeError:
        pass  # Negeer ongeldige berichten voor nu
    
    if not 'clientid' in obj:
        # ignore messages that do not have a client id
        return

    if obj['clientid'] == args.id:
        # ignore messages sent by me
        return

    if not 'message' in obj:
        # ignore messages without a message
        return

    # print the message
    print(f"Received: '{obj['message']}' from '{obj['clientid']}'")


# MQTT client stappen voor aanmaken, verbinden en abonneren op een topic
client = mqtt.Client(args.id)
client.on_message=on_message
client.connect(args.host)
client.loop_start()
client.subscribe(args.topic)

# start an endless loop and wait for input on the commandline
# publish all messages as a JSON object and stop when the input is 'quit'
while True:
    data = input()
    if data == 'quit':
        break

    
    # # versleutel de boodschap en publiceer deze
    iv, encrypted_message = message_encryption.encrypt_message(data, key)
    payload= json.dumps({
        'clientid':args.id,
        'iv':iv.hex(),
        'message': encrypted_message.hex()
    })
    client.publish(args.topic, payload)
    
    
    # publish a message to the chat
    # client.publish(args.topic,json.dumps({
    #     'clientid':args.id,
    #     'message':data
    # }))
    print(f"Published to {args.topic}: {data}")

print("Stopping...")
# terminate the MQTT client loop
client.loop_stop()
    
