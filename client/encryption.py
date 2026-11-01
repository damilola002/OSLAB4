from pathlib import Path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

KEY_PATH = Path(__file__).resolve().parent / "secret.key"


def get_key():
    if KEY_PATH.exists():
        key = KEY_PATH.read_bytes()

        if len(key) != 32:
            raise ValueError("Invalid encryption key")

        return key

    key = AESGCM.generate_key(bit_length=256)

    with open(KEY_PATH, "xb") as key_file:
        key_file.write(key)

    os.chmod(KEY_PATH, 0o600)

    return key


def encrypt_file(file_path):
    key = get_key()
    aes = AESGCM(key)

    nonce = os.urandom(12)
    data = Path(file_path).read_bytes()

    encrypted_data = aes.encrypt(nonce, data, None)

    return nonce + encrypted_data


def decrypt_file(encrypted_data):
    key = get_key()
    aes = AESGCM(key)

    if len(encrypted_data) < 28:
        raise ValueError("Invalid encrypted file")

    nonce = encrypted_data[:12]
    ciphertext = encrypted_data[12:]

    return aes.decrypt(nonce, ciphertext, None)