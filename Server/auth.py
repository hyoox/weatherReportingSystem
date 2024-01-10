# auth.py
import json

USERS_FILE = 'users.json'

def load_users():
    try:
        with open(USERS_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_users(users):
    with open(USERS_FILE, 'w') as file:
        json.dump(users, file)

def authenticate(username, password):
    users = load_users()
    return users.get(username) == password

def is_admin(username):
    return username == "admin"

def change_password(username, new_password):
    users = load_users()
    users[username] = new_password
    save_users(users)
