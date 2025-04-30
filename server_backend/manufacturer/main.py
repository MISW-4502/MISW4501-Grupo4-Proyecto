from flask import Flask
from flask_cors import CORS
from src.routes.manufacturer_routes import manufacturer_bp

app = Flask(__name__)
CORS(app, origins=["http://localhost:4200", "https://proyecto-grupo-4-73827233792.us-central1.run.app"])
app.register_blueprint(manufacturer_bp, url_prefix="/manufacturer")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3404)
