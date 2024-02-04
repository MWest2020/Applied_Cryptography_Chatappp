from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

def sign_message(private_key, message):
    message = message.encode() if isinstance(message, str) else message
    print(f"Signing message: {message}")
    signature = private_key.sign(
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return signature

def verify_signature(public_key, signature, message):
    message = message.encode() if isinstance(message, str) else message
    print(f"Verifying message: {message}")
    try:
        public_key.verify(
            signature,
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except Exception as e:
        print(f"Verification failed with error: {e}")
        return False

def encrypt_message(key, plaintext):
    iv = os.urandom(12)
    encryptor = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend()).encryptor()
    ciphertext = encryptor.update(plaintext.encode()) + encryptor.finalize()
    encrypted_message = base64.b64encode(iv + ciphertext + encryptor.tag).decode('utf-8')
    # print(f"Encrypted IV: {iv.hex()}, Ciphertext: {base64.b64encode(ciphertext).decode()}, Tag: {encryptor.tag.hex()}")
    return encrypted_message

def decrypt_message(key, iv, ciphertext, tag):
    try:
        decryptor = Cipher(algorithms.AES(key), modes.GCM(iv, tag), backend=default_backend()).decryptor()
        decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()
        # print(f"Decrypted data: {decrypted_data.decode()}")
        return decrypted_data
    except Exception as e:
        print(f"Decryption error: {e}")
        return None
def parse_encrypted_message(encrypted_message):
    decoded_message = base64.b64decode(encrypted_message)
    iv = decoded_message[:12]
    tag = decoded_message[-16:]
    ciphertext = decoded_message[12:-16]
    return iv, ciphertext, tag