from flask import Flask
from src.routes.auth_routes import auth_bp
from src.routes.ipblock_routes import ipblock_bp
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(ipblock_bp)

if __name__ == '__main__':

    app.run(host='0.0.0.0', port=3200)
