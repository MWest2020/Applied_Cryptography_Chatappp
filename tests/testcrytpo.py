import os
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

# Encryption function
def encrypt_message(key, plaintext):
    iv = os.urandom(12)
    encryptor = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend()).encryptor()
    ciphertext = encryptor.update(plaintext.encode()) + encryptor.finalize()
    return iv, ciphertext, encryptor.tag

# Decryption function
def decrypt_message(key, iv, ciphertext, tag):
    decryptor = Cipher(algorithms.AES(key), modes.GCM(iv, tag), backend=default_backend()).decryptor()
    return decryptor.update(ciphertext) + decryptor.finalize()

# Parse encrypted message
def parse_encrypted_message(encrypted_message):
    decoded_message = base64.b64decode(encrypted_message)
    iv = decoded_message[:12]
    tag = decoded_message[-16:]
    ciphertext = decoded_message[12:-16]
    return iv, ciphertext, tag

# Test encryption
def test_encryption():
    key = os.urandom(32)  # Generate a new key for testing
    plaintext = "Test Message"
    iv, ciphertext, tag = encrypt_message(key, plaintext)
    encrypted_data = base64.b64encode(iv + ciphertext + tag).decode('utf-8')
    print("Encrypted Data:", encrypted_data)
    return key, encrypted_data

# Test decryption
def test_decryption(key, encrypted_data):
    iv, ciphertext, tag = parse_encrypted_message(encrypted_data)
    decrypted_message = decrypt_message(key, iv, ciphertext, tag)
    print("Decrypted Message:", decrypted_message.decode())

# Main testing logic
if __name__ == "__main__":
    key, encrypted_data = test_encryption()
    test_decryption(key, encrypted_data)
