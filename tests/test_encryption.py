import pytest 
from src.encryption import encrypt_message, decrypt_message
import os

class TestEncryption:
    def test_encrypt_decrypt(self):
        key = os.urandom(32)
        original_text = "Dit is een test."
        encrypted = encrypt_message(key, original_text)
        decrypted = decrypt_message(key, encrypted)
        assert original_text == decrypted

    def test_invalid_key_length(self):
        key = b"korte_sleutel"
        with pytest.raises(ValueError):
            encrypt_message(key, "Dit zal falen")
            
    def test_encrypt_decrypt_with_padding(self):
        key = os.urandom(32)
        original_text = "Dit is een test."
        
        # Versleutel en ontsleutel het bericht
        encrypted = encrypt_message(key, original_text)
        decrypted = decrypt_message(key, encrypted)

        # Check of het ontsleutelde bericht overeenkomt met het origineel
        assert original_text == decrypted, "De ontsleutelde tekst komt niet overeen met het origineel."