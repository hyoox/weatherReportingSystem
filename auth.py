users = {
    "admin": "admin",
    "user":"user",
    "user1":"user1",
}

def authenticate(username, password):
    return users.get(username) == password

def is_admin(username):
    return username == "admin"
