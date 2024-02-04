from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

class KeyManager:
    def __init__(self):
        self.private_key, self.public_key = self.generate_rsa_keypair()
        self.other_public_keys = {}  # Storage for public keys of other clients

    def generate_rsa_keypair(self):
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        return private_key, private_key.public_key()

    def get_public_key_pem(self):
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

    def store_public_key(self, client_id, public_key_pem):
        public_key_bytes = public_key_pem.encode('utf-8')
        public_key = serialization.load_pem_public_key(public_key_bytes, backend=default_backend())
        self.other_public_keys[client_id] = public_key
  
    def get_public_key(self, client_id):
        if client_id not in self.other_public_keys:
            print(f"No public key found for {client_id}")
            return None
        return self.other_public_keys[client_id]
