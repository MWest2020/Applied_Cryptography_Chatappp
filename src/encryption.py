from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import os
import base64 # voor het omzetten van bytes naar een string. Nodig voor het serializeren van de versleutelde boodschap

def encrypt_message(key, message):
    # Zorg ervoor dat de sleutel de juiste lengte heeft (AES256 vereist een 32-byte sleutel)
    if len(key) != 32:
        raise ValueError("De sleutel moet 32 bytes lang zijn voor AES256.")

    iv = os.urandom(16) # 16 bytes = 128 bits

    # Configureer de cipher
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    # Pad de boodschap
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(message.encode()) + padder.finalize()
    # Versleutel de boodschap
    encrypted = encryptor.update(padded_data) + encryptor.finalize()
    
    return base64.b64encode(iv + encrypted).decode('utf-8')


def decrypt_message(key, encrypted_message):
    
    print(f"encrypted_message: {encrypted_message}")
    if len(key) != 32:
        raise ValueError("De sleutel moet 32 bytes lang zijn voor AES256.")

    # Base64 decodeer de versleutelde boodschap
    encrypted_message = base64.b64decode(encrypted_message)
    print(f"encrypted_message Na base64: {encrypted_message}")
    # De IV is de eerste 16 bytes van de versleutelde boodschap
    iv = encrypted_message[:16]
    encrypted_message = encrypted_message[16:]
    print(f"encrypted_message Na iv: {encrypted_message}")
    # Configureer de cipher voor ontsleuteling
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    print(f"cipher: {cipher}")
    decryptor = cipher.decryptor()
    print(f"decryptor: {decryptor}")#hier gaat het nog goed, daarna niet meer
    # Ontsleutel en depad de boodschap 
    unpadder = padding.PKCS7(128).unpadder()
    decrypted =  unpadder.update(decryptor.update(encrypted_message) + decryptor.finalize()).decode('utf-8')
    print(f"decrypted: {decrypted}")
    return decrypted