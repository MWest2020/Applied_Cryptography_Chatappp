# pip3 install paho-mqtt
import paho.mqtt.client as mqtt
import argparse
import time
import string
import secrets
import json

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
    
# on message handler
def on_message(client, userdata, message):
    # This function only accepts messages that:
    #  can be parsed as JSON
    #  have a 'message' and 'clientid' element
    #  where the clientid is not our clientid (args.id)
    try:
        obj = json.loads(message.payload)
    except json.decoder.JSONDecodeError:
        # ignore messages that are not JSON formatted
        return

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

# create MQTT client
client = mqtt.Client(args.id)

# connect the message handler when something is received
client.on_message=on_message

# connect to MQTT broker
client.connect(args.host)

# start the MQTT loop
client.loop_start()

# subscribe to acchat messages
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
    
