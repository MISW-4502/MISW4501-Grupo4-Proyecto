from src.utils.publisher import publish_login_event

def process_login(username, password):
    event = {
        "event": "user_login",
        "username": username,
        "password": password
    }
    publish_login_event(event)
