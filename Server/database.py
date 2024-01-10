import json
from cryptography.fernet import Fernet

key = b'_DcpngSUGkmH70zr3idflMTCGkM696D13Y7OxtdvIW0='
cipher_suite = Fernet(key)

DB_FILE = "encrypted_weather_data.json"

def encrypt_data(data):
    if isinstance(data, bytes):
        return cipher_suite.encrypt(data)
    return cipher_suite.encrypt(data.encode())

def decrypt_data(data):
    return cipher_suite.decrypt(data).decode()

def initialize_encrypted_file():
    """ Initialize the encrypted file with an empty dictionary if it's empty or doesn't exist. """
    try:
        with open(DB_FILE, "rb") as file:
            if not file.read():  # Check if file is empty
                raise FileNotFoundError
    except (FileNotFoundError, json.JSONDecodeError):
        with open(DB_FILE, "wb") as file:
            encrypted_data = encrypt_data(json.dumps({}))
            file.write(encrypted_data)

def save_weather_data(city, weather_data):
    initialize_encrypted_file()
    
    with open(DB_FILE, "rb") as file:
        encrypted_data = file.read()
        data = json.loads(decrypt_data(encrypted_data))

    data[city] = data.get(city, []) + [weather_data]

    with open(DB_FILE, "wb") as file:
        encrypted_data = encrypt_data(json.dumps(data))
        file.write(encrypted_data)

def get_weather_data(city):
    initialize_encrypted_file()

    with open(DB_FILE, "rb") as file:
        encrypted_data = file.read()
        data = json.loads(decrypt_data(encrypted_data))
        return data.get(city, [])
