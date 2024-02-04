from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os
import base64

# def encrypt_message(key, plaintext):
#     iv = os.urandom(12)
#     encryptor = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend()).encryptor()
#     ciphertext = encryptor.update(plaintext.encode()) + encryptor.finalize()

#     return base64.b64encode(iv + ciphertext + encryptor.tag).decode('utf-8')

# def decrypt_message(key, encrypted_message):
#     encrypted_message_bytes = base64.b64decode(encrypted_message)
#     iv = encrypted_message_bytes[:12]
#     tag = encrypted_message_bytes[-16:]
#     ciphertext = encrypted_message_bytes[12:-16]

#     decryptor = Cipher(algorithms.AES(key), modes.GCM(iv, tag), backend=default_backend()).decryptor()
#     return decryptor.update(ciphertext) + decryptor.finalize()

def encrypt_message(key, plaintext):
    iv = os.urandom(12)
    encryptor = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend()).encryptor()
    ciphertext = encryptor.update(plaintext.encode()) + encryptor.finalize()

    return iv, ciphertext, encryptor.tag

def decrypt_message(key, iv, ciphertext, tag):
    decryptor = Cipher(algorithms.AES(key), modes.GCM(iv, tag), backend=default_backend()).decryptor()
    return decryptor.update(ciphertext) + decryptor.finalize()