import json
from cryptography.fernet import Fernet

# The encryption key
key = b'_DcpngSUGkmH70zr3idflMTCGkM696D13Y7OxtdvIW0='
# The cipher suite used for encryption and decryption
cipher_suite = Fernet(key)

# The file where encrypted weather data is stored
DB_FILE = "encrypted_weather_data.json"

# Function to encrypt data
def encrypt_data(data):
    # If the data is bytes, encrypt it directly
    if isinstance(data, bytes):
        return cipher_suite.encrypt(data)
    # If the data is not bytes, encode it as bytes and then encrypt it
    return cipher_suite.encrypt(data.encode())

# Function to decrypt data
def decrypt_data(data):
    # Decrypt the data and decode it as a string
    return cipher_suite.decrypt(data).decode()

# Function to initialize the encrypted file
def initialize_encrypted_file():
    try:
        with open(DB_FILE, "rb") as file:
            # If the file is empty, raise a FileNotFoundError
            if not file.read():
                raise FileNotFoundError
    except (FileNotFoundError, json.JSONDecodeError):
        with open(DB_FILE, "wb") as file:
            # If the file does not exist or is not valid JSON, write an empty dictionary to it
            encrypted_data = encrypt_data(json.dumps({}))
            file.write(encrypted_data)

# Function to save weather data
def save_weather_data(city, weather_data):
    # Initialize the encrypted file
    initialize_encrypted_file()
    
    with open(DB_FILE, "rb") as file:
        # Read the encrypted data from the file
        encrypted_data = file.read()
        # Decrypt the data and load it as JSON
        data = json.loads(decrypt_data(encrypted_data))

    # Add the weather data to the list for the city
    data[city] = data.get(city, []) + [weather_data]

    with open(DB_FILE, "wb") as file:
        # Encrypt the data and write it to the file
        encrypted_data = encrypt_data(json.dumps(data))
        file.write(encrypted_data)

# Function to get weather data
def get_weather_data(city):
    # Initialize the encrypted file
    initialize_encrypted_file()

    with open(DB_FILE, "rb") as file:
        # Read the encrypted data from the file
        encrypted_data = file.read()
        # Decrypt the data and load it as JSON
        data = json.loads(decrypt_data(encrypted_data))
        # Return the list of weather data for the city, or an empty list if there is no data
        return data.get(city, [])