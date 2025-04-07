from flask import Flask
from flask_cors import CORS
from src.routes.login_routes import login_route

app = Flask(__name__)
CORS(app)
app.register_blueprint(login_route)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3100)
