# encryption.py

# Dit bestand verzorgd de symmetrische versleuteling van de boodschappen

# Importeren van benodigde modules van de cryptography library
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import os

def encrypt_message(message, key):
    # Genereren van een willekeurige initialisatievector (IV) voor de versleuteling
    iv = os.urandom(16)  # 16 bytes voor AES

    # Het toepassen van padding op de boodschap, zodat de lengte voldoet aan de eisen van de blokversleuteling
    padder = padding.PKCS7(128).padder()  # PKCS7-padding voor 128-bit blokgrootte
    padded_data = padder.update(message.encode()) + padder.finalize()

    # Instellen van de AES cipher in CFB modus met de gegenereerde sleutel en Initialisatievector (IV)
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())

    # Creëren van een encryptor object en versleutelen van de opgevulde (padded) boodschap
    encryptor = cipher.encryptor()
    ct = encryptor.update(padded_data) + encryptor.finalize()

    # Teruggave van IV en versleutelde tekst (cipher text)
    return iv, ct

def decrypt_message(iv, ct, key):
    # Instellen van de AES cipher in CFB modus met de opgegeven sleutel en IV
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())

    # Creëren van een decryptor object en ontsleutelen van de versleutelde tekst
    decryptor = cipher.decryptor()
    padded_data = decryptor.update(ct) + decryptor.finalize()

    # Verwijderen van de padding van de ontsleutelde boodschap
    unpadder = padding.PKCS7(128).unpadder()
    pt = unpadder.update(padded_data) + unpadder.finalize()

    # Teruggave van de ontsleutelde boodschap
    return pt.decode()
