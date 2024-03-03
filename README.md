# Applied_Cryptography_Chatapp

Final assignment for the first year of applied cryptography at the HvA.

## Installation

To set up your environment for this application, you need to install:

- the paho-mqtt library
- [cryptography.io](https://cryptography.io/en/latest/)

These dependencies can be installed by running the following commands in your terminal:

```bash
pip install paho-mqtt
pip install cryptography
```

## Starting the Application

To start the application, use the following command:

`python acchat.py --host test.mosquitto.org`

This command starts the application with the Mosquitto test server. Specifying a host is mandatory.

Upon starting, if no client ID is provided, one will be assigned to you (you can specify a client ID using the --clientid flag). The client ID is a random string of 8 characters. It is important to save this ID to maintain a consistent identity across sessions.

A key pair will be generated and stored in session files upon startup.

>_Note_>: If you wish to use a different key pair, you can specify the path to your key pair using the --keypair flag. The key pair should be in a .pem file format.

## Testing the Application

To fully test the chat application, you will need to start two instances of the application. This simulates a chat session between two clients. You can start the second instance in a new terminal window using the same command as above. Ensure that each instance uses a unique client ID if you are providing them manually.

## Usage

To use the chat application, follow these steps:

1. **Start the Application:** Open two terminal windows and start an instance of the application in each using the command provided in the "Starting the Application" section. Ensure each instance has a unique client ID if manually specifying them.

2. **Connect to a Chat:** Once both instances are running, use the client ID provided (or the one you specified) to connect to the chat. You can start sending messages from one instance and receive them on the other.

3. **Message Exchange:** Type your message into the console of one instance and press Enter. The message will be encrypted and sent over the MQTT protocol. The receiving instance will decrypt the message and display it.

4. **Session Termination:** To end a chat session, simply close the terminal window or use a keyboard interrupt (Ctrl+C) in each instance of the application.

## Inner Workings

The chat application leverages the MQTT protocol for message passing, combined with robust cryptographic techniques to ensure secure communication:

- **Asymmetric Key Exchange:** Upon initiation, each client generates a public-private key pair. The public key is shared with the other party to establish an identity and enable secure message exchange. This mechanism ensures that only the intended recipient can decrypt the message, as only they possess the corresponding private key.

- **Symmetric Encryption for Messages:** Once a secure channel is established, the application uses symmetric encryption for the actual message exchange. A shared secret key is derived during the initial key exchange process and used for encrypting and decrypting messages. This approach offers a balance between security and performance, suitable for real-time communication.

- **Digital Signatures for Message Verification:** To ensure the integrity and authenticity of messages, each message is signed with the sender's private key. The recipient can then use the sender's public key to verify the signature. This process confirms that the message was indeed sent by the claimed sender and has not been tampered with during transit.

- **MQTT Protocol:** The MQTT (Message Queuing Telemetry Transport) protocol is used as the underlying messaging protocol due to its lightweight and efficient nature, making it highly suitable for real-time communication applications. The protocol facilitates message passing between clients through a publish/subscribe model, where messages are categorized into topics.

This combination of the MQTT protocol and advanced cryptographic techniques ensures that the chat application provides a secure and efficient platform for real-time communication.
