from flask import Flask
from src.routes.login_routes import login_bp

app = Flask(__name__)
app.register_blueprint(login_bp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
