from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

class KeyManager:
    def __init__(self):
        self.private_key, self.public_key = self.generate_rsa_keypair()
        self.other_public_keys = {}  # Opslag voor publieke sleutels van anderen

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
        # van string naar bytes
        public_key_bytes = public_key_pem.encode('utf-8')
        public_key = serialization.load_pem_public_key(public_key_bytes, backend=default_backend())
        # Sla de publieke sleutel op van een andere client
        self.other_public_keys[client_id] = public_key
        print(f"Stored public key of {client_id}")

    def get_public_key(self, client_id):
        return self.other_public_keys.get(client_id, None)

