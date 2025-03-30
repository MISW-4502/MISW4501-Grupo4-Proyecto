from flask import Flask
from src.routes.auth_routes import auth_bp
from src.consumers.login_consumer import consume
import threading

app = Flask(__name__)
app.register_blueprint(auth_bp)

if __name__ == '__main__':
    # Ejecutar el consumidor RabbitMQ en un hilo aparte
    threading.Thread(target=consume, daemon=True).start()
    # Iniciar el servidor Flask
    app.run(host='0.0.0.0', port=3200)
