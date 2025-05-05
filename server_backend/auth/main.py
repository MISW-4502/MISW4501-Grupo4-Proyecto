from flask import Flask
from src.routes.auth_routes import auth_bp
from src.routes.ipblock_routes import ipblock_bp
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=["http://localhost:4200", "https://proyecto-grupo-4-73827233792.us-central1.run.app"])
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(ipblock_bp)

if __name__ == '__main__':

    app.run(host='0.0.0.0', port=3200)
