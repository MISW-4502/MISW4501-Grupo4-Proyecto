FROM python:3.11-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia los archivos del API Gateway al contenedor
COPY . .

# Instala las dependencias, incluyendo gunicorn
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Expone el puerto 3000 para que pueda recibir peticiones externas
EXPOSE 3000

# Ejecuta el servidor Gunicorn en modo producción
CMD ["gunicorn", "main:app", "-b", "0.0.0.0:3000", "--workers=4"]
