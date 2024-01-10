import json

# The file where user data is stored
USERS_FILE = 'users.json'

# Function to load users from the users file
def load_users():
    try:
        # Try to open the users file and load the JSON data
        with open(USERS_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        # If the file does not exist, return an empty dictionary
        return {}

# Function to save users to the users file
def save_users(users):
    # Open the users file and dump the users dictionary as JSON
    with open(USERS_FILE, 'w') as file:
        json.dump(users, file)

# Function to authenticate a user
def authenticate(username, password):
    # Load the users
    users = load_users()
    # Return True if the username exists and the password matches, False otherwise
    return users.get(username) == password

# Function to check if a user is an admin
def is_admin(username):
    # Return True if the username is "admin", False otherwise
    return username == "admin"

# Function to change a user's password
def change_password(username, new_password):
    # Load the users
    users = load_users()
    # Change the user's password
    users[username] = new_password
    # Save the users
    save_users(users)