import paho.mqtt.client as mqtt
import argparse
import string
import secrets
import json
from encryption import encrypt_message, decrypt_message, parse_encrypted_message
from key_exchange import KeyManager

key_manager = KeyManager()
       
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
  
def on_message(client, userdata, message):
    try:
        # print(f"Received raw payload: {message.payload}")
        obj = json.loads(message.payload)
        if obj['type'] == 'key_exchange':
            client_id = obj['clientid']
            public_key_pem = obj['public_key']
            key_manager.store_public_key(client_id, public_key_pem)

        if obj.get('clientid') == args.id:
            return

        if obj.get('type') == 'chat':
            iv, ciphertext, tag = parse_encrypted_message(obj['message'])
            # part for no signing:
            decrypted_msg = decrypt_message(symmetric_key, iv, ciphertext, tag)
            if decrypted_msg:
                print(f"Decrypted Message received: {decrypted_msg.decode()}")
                print("Enter a message:")
            else:
                print("Decryption failed.")
    except Exception as e:
        print(f"Error type: {type(e).__name__}, Message: {str(e)}")

def on_connect(client, userdata, flags, rc):
    # subbing for excahnge 1 and 2
    client.subscribe("public_keys")
    if rc == 0:
        public_key_pem = key_manager.get_public_key_pem()
        client.publish("public_keys", json.dumps({
            'clientid': args.id,
            'type': 'key_exchange',
            'public_key': public_key_pem.decode()
        }), retain = True) # Retain the public key message !important. DIT DUS NIET VERGETEN
      
        client.subscribe("public_keys")

client = mqtt.Client(args.id)
# TODO: subscribe to the public_keys topic or cli, see if this conflicts?
# client.subscribe("public_keys")
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
# okaayyyy.... don;t move this up.
client.subscribe(args.topic)

while True:
    data = input("Enter message (or 'quit' to exit): ")
    if data.lower() == 'quit':
        break
    encrypted_data = encrypt_message(symmetric_key, data)
    

    payload = json.dumps({
        'clientid': args.id,
        'type': 'chat',
        'message': encrypted_data,
    })
    client.publish(args.topic, payload)
   
print("Disconnecting...")
client.loop_stop()
# Gracefully sluiten van de MQTT client
client.disconnect()