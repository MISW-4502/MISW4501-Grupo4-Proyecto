from flask import Flask
from src.routes.auth_routes import auth_bp
from src.routes.ipblock_routes import ipblock_bp


app = Flask(__name__)
app.register_blueprint(auth_bp)
app.register_blueprint(ipblock_bp)

if __name__ == '__main__':

    app.run(host='0.0.0.0', port=3200)
