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
