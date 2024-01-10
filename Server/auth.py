# Define a dictionary of users and their passwords
users = {
    "admin": "admin",
    "user": "user",
    "user1": "user1",
}

# Define a function to authenticate a user
def authenticate(username, password):
    # Check if the provided password matches the password for this user
    # If the user doesn't exist, users.get(username) will return None, so the function will return False
    return users.get(username) == password

# Define a function to check if a user is an admin
def is_admin(username):
    # Check if the username is "admin"
    return username == "admin"