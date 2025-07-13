# Prueba Técnica - Desarrollo de API busqueda de restaurantes

## Tecnologías utilizadas
- **Python**: Lenguaje principal del desarrollo.
- **Django**: Framework principal para el desarrollo de la API.
- **Django REST Framework**: Para simplificar la creación de los endpoints de la API.
- **PostgreSQL**: Base de datos utilizada, aunque puede configurarse con cualquier base de datos SQL.
- **Docker**: Para contenerización y despliegue local del proyecto.
- **Drf-spectacular**: Herramienta para generar un esquema/documentacion de la API automaticamente.

## Endpoints
1. **``POST`` /api/register/**: Registro de usuarios
2. **``POST`` /api/token/**: Login de usuarios
3. **``POST`` /api/token/refresh/**: Refrescar token de autenticación
4. **``POST`` /api/token/logout/**: Invalida token de refresco
5. **``GET`` /api/docs/**: Documentación de la API en swagger
6. **``GET`` /api/actions/**: Lista el historial de transacciones del usuario
7. **``GET`` /restaurants/nearby/**: Busca restaurantes cerca a la ubicacion proveida

## Requisitos
- Docker
- Docker Compose

## Instalación y configuración
### 1. Clonar proyecto desde GitHub
```bash
git clone https://github.com/OnofreB22/prueba-tecnica.git
cd PruebaT
```

### 2. Crear .env
Crear archivo en prueba-tecnica/app/.env siguiendo la siguiente estructura:
```
DB_HOST=
DB_NAME=
DB_USER=
DB_PASS=

POSTGRES_DB=
POSTGRES_USER=
POSTGRES_PASSWORD=

DJANGO_SECRET_KEY=
DJANGO_DEBUG=
DJANGO_ALLOWED_HOSTS=

GOOGLE_MAPS_API_KEY=
```

### 3. Ejecutar el proyecto
```bash
docker-compose build
docker-compose up
```

### 4. Realizar migraciones de la base de datos (Opcional)
```bash
docker-compose run --rm app sh -c "python manage.py makemigrations"
docker-compose run --rm app sh -c "python manage.py migrate"
```

### 5. Ejecucion de las pruebas unitarias (Opcional)
```bash
docker-compose run --rm app sh -c "python manage.py test"
```

## Uso del API

### Crear nuevo usuario
- **Endpoint**: ``POST`` /api/register/
- **Body**:
```json
{
  "username": "nombre_usuario",
  "email": "correo@ejemplo.com",
  "password": "contraseña_segura"
}
```
- **Respuesta esperada** (`201 Created`)

### Login de usuario
- **Endpoint**: ``POST`` /api/token/
- **Body**:
```json
{
  "email": "correo@ejemplo.com",
  "password": "contraseña_segura"
}
```
- **Respuesta esperada** (`200 OK`):
```json
{
  "access": "token_de_acceso",
  "refresh": "token_de_refresco"
}
```

### Refrescar token
- **Endpoint**: ``POST`` /api/token/refresh/
- **Body**:
```json
{
  "refresh": "token_de_refresco"
}
```
- **Respuesta esperada** (`200 OK`):
```json
{
  "access": "nuevo_token_de_acceso"
}
```

### Logout
- **Endpoint**: ``POST`` /api/logout/
- **Headers**:
```http
Authorization: Bearer <token_de_acceso>
Content-Type: application/json
```
- **Body**:
```json
{
  "refresh": "token_de_refresco"
}
```
- **Respuesta esperada** (`205 Reset Content`)

### Documentación Swagger
- **Endpoint**: ``GET`` /api/docs/
- **Descripción**: Muestra una interfaz interactiva para explorar la API.

### Historial de acciones del usuario
- **Endpoint**: ``GET`` /api/actions/
- **Headers**:
```http
Authorization: Bearer <token_de_acceso>
```
- **Respuesta esperada** (`200 OK`):
```json
[
  {
    "action": "tipo_de_accion",
    "timestamp": "fecha_hora_ISO"
  }
]
```

### Buscar restaurantes cercanos
- **Endpoint**: ``GET`` /restaurants/nearby/
- **Headers**:
```http
Authorization: Bearer <token_de_acceso>
```
- **Parámetros de query**:

1. **Por ciudad**:
```
?city=nombre_ciudad
```
  - `city`: Nombre de la ciudad a consultar (ejemplo: `medellin`)

2. **Por coordenadas**:
```
?lat=6.25184&lng=-75.56359
```
  - `lat`: Latitud de la ubicación actual.
  - `lng`: Longitud de la ubicación actual.

- **Respuesta esperada** (`200 OK`):
```json
{
  "restaurants": [
    {
      "name": "Restaurante Mango Maduro",
      "address": "Ecuador #5430",
      "rating": 4
    },
    {
      "name": "Mi Hotel Sandiego",
      "address": "Calle 31 #43 - 90",
      "rating": 4.5
    },
    {
      "name": "Qbano Avenida Oriental",
      "address": "Carrera 46 #52- 47",
      "rating": 4.1
    },
    {
      "name": "Presto",
      "address": "Carrera 47 #No. 52 - 86 Interior 442",
      "rating": 4.2
    },
    {
      "name": "Reposteria Astor - Junin",
      "address": "Carrera 49 #5284",
      "rating": 4.7
    }
    // ... otros restaurantes
  ]
}
```
