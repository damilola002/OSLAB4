from pathlib import Path
from encryption import encrypt_file, decrypt_file

original = Path("client/test.txt")
original.write_text("This is my secret assignment file!")

encrypted = encrypt_file(original)

print("Encrypted data:", encrypted.hex()[:80], "...")

decrypted = decrypt_file(encrypted)

print("Decrypted data:", decrypted.decode())

assert decrypted == original.read_bytes()

print("Encryption test passed!")