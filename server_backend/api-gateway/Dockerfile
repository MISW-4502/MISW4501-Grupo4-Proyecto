# Imagen base de Python
FROM python:3.11-slim

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar todos los archivos al contenedor
COPY . .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Puerto expuesto por el API Gateway
EXPOSE 3000

# Comando para ejecutar la app
CMD ["python", "main.py"]
