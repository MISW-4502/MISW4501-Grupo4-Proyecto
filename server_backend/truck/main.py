from flask import Flask
from src.routes.truck_routes import trucks_bp



app = Flask(__name__)
app.register_blueprint(trucks_bp)

if __name__ == '__main__':

    app.run(host='0.0.0.0', port=3300)
