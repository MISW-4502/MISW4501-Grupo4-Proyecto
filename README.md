# MISW4501-Grupo4-Proyecto

Este repositorio contiene el backend de un sistema distribuido basado en microservicios para la gestión de autenticación, inventario, ventas, camiones, imágenes y fabricantes. 

## 🧱 Arquitectura de Microservicios

El proyecto sigue una arquitectura de microservicios desacoplados que se comunican entre sí usando colas RabbitMQ o llamadas HTTP. Se utilizan bases de datos PostgreSQL individuales por servicio y un gateway API como punto de entrada común.

### 📦 Microservicios incluidos

| Servicio              | Descripción                                                                 |
|-----------------------|-----------------------------------------------------------------------------|
| `auth-service`        | Gestión de usuarios, autenticación con JWT, recuperación de contraseña.    |
| `truck-service`       | Registro, listado y gestión de camiones.                                   |
| `manufacturer-service`| Administración de fabricantes, incluye creación y edición.                 |
| `inventary-service`   | Carga masiva de productos desde Excel/CSV, gestión del inventario.         |
| `sales-service`       | Gestión de pedidos y detalles del pedido.                                  |
| `images-service`      | Recepción de imágenes base64 y envío a cola.                               |
| `process-images-worker`| Procesamiento de imágenes y sugerencias de productos.                    |
| `product-worker`      | Crea productos a partir de los mensajes en la cola.                        |
| `order-worker`        | Consume pedidos de RabbitMQ y los guarda en base de datos.                 |
| `api-gateway`         | Proxy de acceso centralizado, enruta hacia los servicios internos.         |

## ⚙️ Tecnologías utilizadas

- **Python 3.9** + Flask
- **Node.js** (API Gateway)
- **PostgreSQL**
- **RabbitMQ**
- **Redis** (para bloqueo de IP)
- **Docker & Docker Compose**
- **GitHub Actions** para CI/CD

## 📁 Estructura del proyecto

```bash
server_backend/
├── auth/
├── truck/
├── manufacturer/
├── inventary/
├── sales/
├── images-service/
├── product-worker/
├── order-worker/
├── api-gateway/
└── docker-compose.yml
```

## 🚀 Despliegue en Google Cloud Platform (GCP)

Se utiliza una VM en GCP con Docker instalado. Para desplegar:

```bash
git clone https://github.com/usuario/proyecto.git
cd server_backend
docker-compose up --build -d
```

Asegúrate de tener configuradas las variables de entorno en cada servicio dentro del `docker-compose.yml`.

## 🧪 Pruebas

Cada microservicio cuenta con pruebas unitarias implementadas con `pytest`. Las pruebas se ejecutan automáticamente vía GitHub Actions en cada push al branch `test_branch`.

Para correr localmente:

```bash
cd server_backend/auth
pytest
```

## 🔐 Seguridad

- Tokens JWT firmados con secreto compartido (`JWT_SECRET`)
- Bloqueo de IP en `auth-service` vía Redis tras múltiples intentos fallidos
- Validación de token vía `auth-service` desde otros microservicios (como `sales`, `inventary`, etc.)

## 📦 Endpoints destacados por servicio

### auth-service
- `POST /auth/login`
- `POST /auth/register`
- `POST /auth/validate`
- `POST /auth/password/reset/request`

### sales-service
- `POST /sales`: crea pedido
- `PATCH /sales/<id>`: edita estado
- `PATCH /sales/<id>/items`: agregar/quitar ítems

### inventary-service
- `POST /inventary/upload-products`: carga Excel/CSV
- `POST /inventary/products/<id>/reserve`: aparta cantidad
- `POST /inventary/products/<id>/release`: libera stock

### truck-service
- `POST /trucks`: crea camión
- `GET /trucks`: lista camiones

## 🧰 Troubleshooting

- 🔄 **RabbitMQ sin conexión**: Verifica puertos 5672 y variables `RABBITMQ_HOST`
- 🐘 **PostgreSQL rechaza conexión**: Asegúrate que `pg_hba.conf` permita IP de la VM
- 🔑 **Token inválido**: Verifica que se esté enviando en `Authorization: Bearer <token>`

## 📌 Requisitos mínimos para ejecutar

- Python 3.9+
- Docker y Docker Compose
- PostgreSQL 12+
- Node.js 18+ (solo para `api-gateway` y ngrok local dev)

## ✨ Mejoras futuras

- Integración con Cloud SQL y Secret Manager
- Pruebas E2E
- Métricas con Prometheus + Grafana
- Balanceo de carga con Traefik o NGINX

## 📧 Contacto

Grupo 4 - MISW4501
