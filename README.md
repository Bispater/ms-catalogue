# MS Catalogue

Servicio de catálogo de productos desarrollado con Django REST Framework y PostgreSQL, contenerizado con Docker.

## 📋 Características

- API RESTful para gestión de productos
- Panel de administración de Django
- Base de datos PostgreSQL
- Configuración para desarrollo y producción
- Manejo de archivos estáticos y multimedia
- Autenticación JWT (por implementar)

## 🚀 Tecnologías

- Python 3.9
- Django 4.2
- Django REST Framework
- PostgreSQL 13
- Docker y Docker Compose
- Gunicorn (producción)
- Nginx (producción)

## 🏗️ Estructura del Proyecto

```
ms-catalogue/
├── api/                 # Aplicación de la API
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations/
│   ├── models.py
│   ├── serializers.py
│   ├── tests.py
│   └── views.py
├── core/                # Configuración principal del proyecto (antes ms_catalogue)
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── static/              # Archivos estáticos (CSS, JS, imágenes)
├── staticfiles/         # Archivos estáticos recolectados (generado)
├── media/               # Archivos multimedia subidos por usuarios
├── .env                # Variables de entorno
├── .dockerignore
├── docker-compose.yml
├── Dockerfile
├── manage.py
└── requirements.txt
```

## 🔧 Configuración

### Variables de Entorno (.env)

Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:

```env
# Django
SECRET_KEY=tu_clave_secreta_aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
POSTGRES_DB=ms_catalogue
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Docker
DOCKER_ENV=True
```

## 🚀 Despliegue Local

### Requisitos Previos

- Docker y Docker Compose instalados
- Python 3.9+ (solo para desarrollo local sin Docker)

### Desarrollo con Docker (Recomendado)

1. Clona el repositorio:
   ```bash
   git clone <repo-url>
   cd ms-catalogue
   ```

2. Crea el archivo `.env` basado en el ejemplo anterior

3. Construye y ejecuta los contenedores:
   ```bash
   docker compose up --build
   ```

4. Accede a la aplicación:
   - API: http://localhost:8050/api/
   - Admin: http://localhost:8050/admin/

5. Crea un superusuario (en otra terminal):
   ```bash
   docker compose exec web python manage.py createsuperuser
   ```

### Desarrollo sin Docker

1. Crea un entorno virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

2. Instala dependencias:
   ```bash
   pip install -r requirements.txt
   ```

3. Configura la base de datos PostgreSQL local

4. Ejecuta las migraciones:
   ```bash
   python manage.py migrate
   ```

5. Crea un superusuario:
   ```bash
   python manage.py createsuperuser
   ```

6. Inicia el servidor de desarrollo:
   ```bash
   python manage.py runserver
   ```

## 🏭 Producción

### Configuración

1. Establece `DEBUG=False` en `.env`
2. Configura `ALLOWED_HOSTS` con tu dominio
3. Asegúrate de tener un servicio SMTP configurado para correos
4. Configura SSL/TLS (recomendado usar Let's Encrypt)

### Despliegue con Docker

1. Construye la imagen para producción:
   ```bash
   docker compose -f docker-compose.prod.yml build
   ```

2. Inicia los servicios:
   ```bash
   docker compose -f docker-compose.prod.yml up -d
   ```

3. Recolecta archivos estáticos:
   ```bash
   docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
   ```

## 🔒 Seguridad

- No expongas el panel de administración públicamente
- Usa HTTPS en producción
- Mantén las dependencias actualizadas
- Usa variables de entorno para secretos
- Implementa rate limiting

## 🛠️ Comandos Útiles

- **Ver logs**: `docker compose logs -f`
- **Abrir shell en el contenedor**: `docker compose exec web bash`
- **Ejecutar pruebas**: `docker compose exec web python manage.py test`
- **Crear migraciones**: `docker compose exec web python manage.py makemigrations`
- **Aplicar migraciones**: `docker compose exec web python manage.py migrate`

## 📊 Estructura de la Base de Datos

### Modelo Actual: Producto

- `name`: Nombre del producto (CharField)
- `description`: Descripción del producto (TextField)
- `price`: Precio (DecimalField)
- `created_at`: Fecha de creación (DateTimeField)
- `updated_at`: Fecha de actualización (DateTimeField)

## 🤝 Contribuir

1. Haz un fork del proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Haz commit de tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Haz push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 🚀 Despliegue en Producción

Sigue estos pasos para desplegar la aplicación en un entorno de producción seguro y escalable:

### 1. Configuración del Servidor

- **Requisitos del Servidor**:
  - Linux (Ubuntu 20.04/22.04 LTS recomendado)
  - Docker y Docker Compose instalados
  - 2+ vCPUs, 4GB+ RAM, 20GB+ almacenamiento
  - Dominio configurado con registros DNS

- **Actualizar el sistema**:
  ```bash
  sudo apt update && sudo apt upgrade -y
  ```

### 2. Configuración de Variables de Entorno

Crea un archivo `.env.prod` en el servidor con las siguientes variables:

```env
# Django
DEBUG=False
SECRET_KEY=tu_clave_secreta_muy_larga_y_compleja
ALLOWED_HOSTS=.tudominio.com,localhost,127.0.0.1

# Base de datos
DB_NAME=nombre_bd
DB_USER=usuario_bd
DB_PASSWORD=contraseña_fuerte
DB_HOST=db
DB_PORT=5433

# Email
EMAIL_HOST=smtp.tuservidor.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu@email.com
EMAIL_HOST_PASSWORD=tu_contraseña
DEFAULT_FROM_EMAIL=no-reply@tudominio.com

# Seguridad
CSRF_TRUSTED_ORIGINS=https://*.tudominio.com,https://tudominio.com
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_BROWSER_XSS_FILTER=True
SECURE_CONTENT_TYPE_NOSNIFF=True
X_FRAME_OPTIONS=DENY

# CKEditor
AWS_ACCESS_KEY_ID=tu_access_key
AWS_SECRET_ACCESS_KEY=tu_secret_key
AWS_STORAGE_BUCKET_NAME=tu-bucket-s3
AWS_S3_CUSTOM_DOMAIN=f{tu-bucket-s3}.s3.amazonaws.com
AWS_DEFAULT_ACL=None
```

### 3. Configuración de Docker en Producción

Crea un archivo `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  web:
    build: .
    command: gunicorn core.wsgi:application --bind 0.0.0.0:8000
    env_file: .env.prod
    restart: always
    depends_on:
      - db
      - redis
    ports:
      - "8000:8000"
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    networks:
      - app_network

  db:
    image: postgres:13
    env_file: .env.prod
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    networks:
      - app_network
    restart: always

  redis:
    image: redis:6
    command: redis-server --requirepass ${REDIS_PASSWORD:-tupassword}
    volumes:
      - redis_data:/data
    networks:
      - app_network
    restart: always

  celery_worker:
    build: .
    command: celery -A core worker -l info
    env_file: .env.prod
    depends_on:
      - redis
      - db
    volumes:
      - .:/app
    networks:
      - app_network
    restart: always

  celery_beat:
    build: .
    command: celery -A core beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
    env_file: .env.prod
    depends_on:
      - redis
      - db
      - celery_worker
    volumes:
      - .:/app
    networks:
      - app_network
    restart: always

networks:
  app_network:
    driver: bridge

volumes:
  postgres_data:
  redis_data:
  static_volume:
  media_volume:
```

### 4. Configuración de Nginx como Proxy Inverso

Crea un archivo de configuración para Nginx (`/etc/nginx/sites-available/tudominio.com`):

```nginx
upstream app_server {
    server web:8000;
}

server {
    listen 80;
    server_name tudominio.com www.tudominio.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name tudominio.com www.tudominio.com;

    ssl_certificate /etc/letsencrypt/live/tudominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/tudominio.com/privkey.pem;
    
    # Configuración SSL mejorada
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256';
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_stapling on;
    ssl_stapling_verify on;

    # Configuración de seguridad
    add_header X-Frame-Options "SAMEORIGIN";
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Referrer-Policy "strict-origin-when-cross-origin";

    # Archivos estáticos y media
    location /static/ {
        alias /app/staticfiles/;
        expires 30d;
        access_log off;
        add_header Cache-Control "public";
    }

    location /media/ {
        alias /app/media/;
        expires 30d;
        access_log off;
        add_header Cache-Control "public";
    }

    # Configuración de WebSocket para canales
    location /ws/ {
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_redirect off;
        proxy_pass http://app_server;
    }

    # Configuración principal
    location / {
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_pass http://app_server;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
}
```

### 5. Configuración de Certificado SSL

Instala Certbot y obtén un certificado SSL gratuito de Let's Encrypt:

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d tudominio.com -d www.tudominio.com
```

### 6. Configuración de Tareas Programadas

Configura un cron job para renovar automáticamente los certificados SSL:

```bash
sudo crontab -e
```

Agrega la siguiente línea:
```
0 12 * * * /usr/bin/certbot renew --quiet
```

### 7. Monitoreo y Mantenimiento

- **Logs**: Configura logrotate para los logs de la aplicación
- **Monitoreo**: Configura un servicio como Prometheus + Grafana
- **Backups**: Configura backups automáticos de la base de datos
- **Actualizaciones**: Programa ventanas de mantenimiento para actualizaciones

### 8. Despliegue Continuo (Opcional)

Configura un pipeline de CI/CD usando GitHub Actions o GitLab CI para despliegues automáticos.

## 📄 Licencia

Distribuido bajo la licencia MIT. Ver `LICENSE` para más información.

## ✉️ Contacto

Tu Nombre - [@tu_twitter](https://twitter.com/tu_twitter)

Enlace del Proyecto: [https://github.com/tu_usuario/ms-catalogue](https://github.com/tu_usuario/ms-catalogue)

---

<div align="center">
  <sub>Hecho con ❤️ por Tu Nombre</sub>
</div>
