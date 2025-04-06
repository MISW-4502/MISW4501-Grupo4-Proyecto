from flask import Flask
from src.routes.product_routes import inventary_bp



app = Flask(__name__)
app.register_blueprint(inventary_bp, url_prefix="/inventary")

if __name__ == '__main__':

    app.run(host='0.0.0.0', port=3400)
