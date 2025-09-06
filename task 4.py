from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
import os
import getpass

def get_key(password, salt):
    return PBKDF2(password, salt, dkLen=32, count=1000000)

def encrypt_file(file_path, password):
    salt = get_random_bytes(16)
    key = get_key(password.encode(), salt)
    cipher = AES.new(key, AES.MODE_GCM)
    nonce = cipher.nonce

    with open(file_path, 'rb') as f:
        data = f.read()

    ciphertext, tag = cipher.encrypt_and_digest(data)

    with open(file_path + ".enc", 'wb') as f:
        f.write(salt + nonce + tag + ciphertext)

    print(f"✅ File '{file_path}' encrypted successfully as '{file_path}.enc'")

def decrypt_file(file_path, password):
    with open(file_path, 'rb') as f:
        salt = f.read(16)
        nonce = f.read(16)
        tag = f.read(16)
        ciphertext = f.read()

    key = get_key(password.encode(), salt)
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)

    try:
        plaintext = cipher.decrypt_and_verify(ciphertext, tag)
        output_file = file_path.replace(".enc", ".dec")

        with open(output_file, 'wb') as f:
            f.write(plaintext)

        print(f"✅ File '{file_path}' decrypted successfully as '{output_file}'")
    except ValueError:
        print("❌ Incorrect password or corrupted file.")

# ==== Command-Line Interface ====
if _name_ == "_main_":
    print("🔐 Advanced Encryption Tool")