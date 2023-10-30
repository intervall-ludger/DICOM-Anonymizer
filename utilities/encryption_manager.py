import base64
import os

import pydicom
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def generate_key(password: str, salt: bytes) -> bytes:
    """
    Generate a key using the given password and salt.

    Args:
        password (str): The password.
        salt (bytes): The salt.

    Returns:
        bytes: The derived key.
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend(),
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key


def encrypt(data: str, password: str) -> str:
    """
    Encrypt the given data using a password.

    Args:
        data (str): The data to encrypt.
        password (str): The password to use for encryption.

    Returns:
        str: The encrypted data.
    """
    salt = os.urandom(16)
    key = generate_key(password, salt)
    cipher_suite = Fernet(key)
    encrypted_data = cipher_suite.encrypt(data.encode())
    return "xx80xx80" + (salt + encrypted_data).hex()


def decrypt(data: str, password: str) -> str:
    """
    Decrypt the given data using a password.

    Args:
        data (str): The encrypted data.
        password (str): The password used for encryption.

    Returns:
        str: The decrypted data.
    """
    decoded_data = bytes.fromhex(data[8:])
    salt, encrypted_data = decoded_data[:16], decoded_data[16:]
    key = generate_key(password, salt)
    cipher_suite = Fernet(key)
    decrypted_data = cipher_suite.decrypt(encrypted_data)
    return decrypted_data.decode()


def detect_if_encrypted(ds: pydicom.Dataset) -> bool:
    """
    Detect if the given dataset is encrypted.

    This is a simple metric which check if (0x0019, 0x0101) exist

    Args:
        data (str): The data to check.

    Returns:
        bool: True if data is likely encrypted, otherwise False.
    """
    try:
        ds[(0x0019, 0x0101)]
    except KeyError:
        return False
    return True
