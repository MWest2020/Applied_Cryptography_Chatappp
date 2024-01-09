# Applied_Cryptography_Chatappp

Final assignment for the first year oof applied cryptography of the HvA

## Installation

The only things you need to install are:

- the paho-mqtt library
- [cryptography.io](https://cryptography.io/en/latest/)

These can be done by running `pip install paho-mqtt` and  `pip install cryptography` in your terminal.

## Starting the application

`python acchat.py --host test.mosquitto.org` starts the application with the mosquitto test server. Specifiying a host is mandatory.

You will get a client ID assigned if none is provided (you can provide this with the `--clientid` flag). The client ID is a random string of 8 characters. SAVE THIS ID to maintain a consistent ID for sessions.

(ID not tested yet)

On start up, a keygen pair will be generated a and stored in session files.

TODO: If you want to use a different keypair, you can specify the path to the keypair with the `--keypair` flag. The keypair should be a .pem file.

## Usage

## Inner workings

## Roadmap

- Password for subscription and publishing to a topic
- Time based key rotation
- Time stamping
- Rename client ID to username
- Add a GUI
- Add a database to store messages
- Add a database to store users
- Add a database to store topics
- key storage
