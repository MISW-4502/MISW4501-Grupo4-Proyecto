from src.utils.publisher import publish_login_event

def process_login(username, password):
    event = {
        "event": "hacer algo"
    }
    publish_login_event(event)
