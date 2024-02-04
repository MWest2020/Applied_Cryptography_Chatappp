import time
import paho.mqtt.client as mqtt
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os

# MQTT Broker settings
MQTT_BROKER = "test.mosquitto.org"
MQTT_PORT = 1883
MQTT_TOPIC = "my/test/topic"


symmetric_key= None

# Encryption and Decryption functions
def encrypt_message(key, plaintext):
    iv = os.urandom(12)
    encryptor = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend()).encryptor()
    ciphertext = encryptor.update(plaintext.encode()) + encryptor.finalize()
    encrypted_message = base64.b64encode(iv + ciphertext + encryptor.tag)
    return encrypted_message.decode('utf-8')

def decrypt_message(key, iv, ciphertext, tag):
    try:
        decryptor = Cipher(algorithms.AES(key), modes.GCM(iv, tag), backend=default_backend()).decryptor()
        return decryptor.update(ciphertext) + decryptor.finalize()
    except Exception as e:
        print(f"Internal decryption error: {type(e).__name__}, {str(e)}")
        return None

# MQTT Callbacks
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    try:
        print(f"Received message on topic {msg.topic}")
        iv, ciphertext, tag = parse_encrypted_message(msg.payload)

        # Debugging: Print the IV, ciphertext, and tag
        print(f"IV: {iv.hex()}")
        print(f"Ciphertext: {base64.b64encode(ciphertext).decode()}")
        print(f"Tag: {tag.hex()}")

        decrypted_message = decrypt_message(symmetric_key, iv, ciphertext, tag)
        print(f"Decrypted Message: {decrypted_message.decode()}")
    except Exception as e:
        print(f"Decryption error: {e}")

def parse_encrypted_message(encrypted_message):
    decoded_message = base64.b64decode(encrypted_message)
    iv = decoded_message[:12]
    tag = decoded_message[-16:]
    ciphertext = decoded_message[12:-16]
    return iv, ciphertext, tag

# Main
def main():
    global symmetric_key
    # Define a 32-byte (256-bit) static key for testing = works
    symmetric_key = b"12345678901234567890123456789012"
    # symmetric_key = os.urandom(32)  

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()

    client.subscribe(MQTT_TOPIC)

    try:
        while True:
            message = input("Enter message (or 'quit' to exit): ")
            if message.lower() == 'quit':
                break

            encrypted_data = encrypt_message(symmetric_key, message)
            print(f"Encrypted message: {encrypted_data}")

            # Static Data Test: Directly decrypt the message after encryption
            iv, ciphertext, tag = parse_encrypted_message(encrypted_data)
            decrypted_message = decrypt_message(symmetric_key, iv, ciphertext, tag)
            if decrypted_message:
                print(f"Decrypted message (static test): {decrypted_message.decode()}")

            client.publish(MQTT_TOPIC, encrypted_data)

            # Sleep for a short while to prevent high CPU usage
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        client.loop_stop()

if __name__ == "__main__":
    main()
