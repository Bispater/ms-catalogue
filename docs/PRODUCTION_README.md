# 🚀 Catalogue API - Guía de Despliegue a Producción

## 📋 Índice

1. [Pre-requisitos](#pre-requisitos)
2. [Configuración del Archivo .env.prod](#configuración-del-archivo-envprod)
3. [Checklist de Seguridad](#checklist-de-seguridad)
4. [Despliegue](#despliegue)
5. [Monitoreo y Mantenimiento](#monitoreo-y-mantenimiento)
6. [Troubleshooting](#troubleshooting)

---

## 📦 Pre-requisitos

### Servicios Externos Necesarios

- [ ] **Servidor de Producción** (VPS, EC2, DigitalOcean, etc.)
- [ ] **Base de Datos PostgreSQL** (RDS, Managed Database, etc.)
- [ ] **Redis** (ElastiCache, Managed Redis, etc.)
- [ ] **AWS S3** (para archivos estáticos y media)
- [ ] **Servidor SMTP** (Gmail, SendGrid, AWS SES, Mailgun, etc.)
- [ ] **Dominio** con certificado SSL/TLS
- [ ] **Sentry** (opcional, para monitoreo de errores)

### Herramientas Locales

- Docker y Docker Compose
- Git
- Editor de texto

---

## 🔧 Configuración del Archivo .env.prod

### 1. Copiar el Template

```bash
# El archivo .env.prod ya está creado con valores de ejemplo
# Edítalo con tu editor favorito
nano .env.prod
# o
code .env.prod
```

### 2. Configuraciones CRÍTICAS a Cambiar

#### 🔐 **Django Secret Key**

```bash
# Generar una nueva secret key
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Copiar el resultado y reemplazar en .env.prod:
SECRET_KEY=tu-clave-generada-aqui
```

#### 🌐 **Dominios**

```bash
# Reemplazar con tus dominios reales
ALLOWED_HOSTS=.tudominio.com,tudominio.com,www.tudominio.com
CSRF_TRUSTED_ORIGINS=https://tudominio.com,https://www.tudominio.com,https://api.tudominio.com
CORS_ALLOWED_ORIGINS=https://tudominio.com,https://www.tudominio.com
```

#### 🗄️ **Base de Datos**

```bash
DB_NAME=ms_catalogue_prod
DB_USER=catalogue_user  # NO usar 'postgres'
DB_PASSWORD=contraseña-segura-minimo-16-caracteres
DB_HOST=tu-servidor-db.rds.amazonaws.com  # o IP de tu servidor
DB_PORT=5432
```

**Generar contraseña segura:**
```bash
openssl rand -base64 32
```

#### 📧 **Email (Ejemplo con Gmail)**

```bash
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-app-password  # Usar App Password, no contraseña normal
DEFAULT_FROM_EMAIL=noreply@tudominio.com
```

**Crear App Password en Gmail:**
1. Ve a https://myaccount.google.com/security
2. Activa verificación en 2 pasos
3. Ve a "App passwords"
4. Genera una contraseña para "Mail"

#### ☁️ **AWS S3**

```bash
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_STORAGE_BUCKET_NAME=ms-catalogue-prod
AWS_S3_REGION_NAME=us-east-1
```

**Crear bucket S3:**
```bash
# Usando AWS CLI
aws s3 mb s3://ms-catalogue-prod --region us-east-1

# Configurar política pública para archivos estáticos
aws s3api put-bucket-policy --bucket ms-catalogue-prod --policy file://bucket-policy.json
```

#### 🔴 **Redis**

```bash
REDIS_URL=redis://:tu-password@tu-servidor-redis:6379/0
REDIS_PASSWORD=contraseña-segura-redis
```

#### 📊 **Sentry (Monitoreo de Errores)**

```bash
# Crear cuenta en https://sentry.io/
# Crear nuevo proyecto Django
# Copiar el DSN
SENTRY_DSN=https://examplePublicKey@o0.ingest.sentry.io/0
```

---

## 🔒 Checklist de Seguridad

### Antes de Desplegar

- [ ] `DEBUG=False` en `.env.prod`
- [ ] `SECRET_KEY` única y segura (50+ caracteres)
- [ ] `ALLOWED_HOSTS` configurado con dominios reales
- [ ] Contraseñas de DB con mínimo 16 caracteres
- [ ] Redis con contraseña configurada
- [ ] `SECURE_SSL_REDIRECT=True`
- [ ] `SESSION_COOKIE_SECURE=True`
- [ ] `CSRF_COOKIE_SECURE=True`
- [ ] Certificado SSL/TLS instalado en el servidor
- [ ] Firewall configurado (solo puertos 80, 443, 22)
- [ ] Backups automáticos configurados
- [ ] Monitoreo configurado (Sentry, CloudWatch, etc.)

### Verificación de Seguridad

```bash
# Verificar que no haya valores de ejemplo
grep -i "CAMBIAR" .env.prod
# No debe retornar nada

# Verificar DEBUG
grep "^DEBUG=" .env.prod
# Debe mostrar: DEBUG=False

# Verificar SSL
grep "SECURE_SSL_REDIRECT" .env.prod
# Debe mostrar: SECURE_SSL_REDIRECT=True
```

---

## 🚀 Despliegue

### Opción 1: Despliegue con Docker Compose

#### 1. Preparar el Servidor

```bash
# Conectar al servidor
ssh usuario@tu-servidor.com

# Instalar Docker y Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
sudo usermod -aG docker $USER

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### 2. Clonar el Repositorio

```bash
git clone https://github.com/tu-usuario/catalogue_api.git
cd catalogue_api
```

#### 3. Configurar Variables de Entorno

```bash
# Copiar .env.prod a .env
cp .env.prod .env

# Editar y configurar todas las variables
nano .env
```

#### 4. Crear docker-compose.prod.yml

```yaml
version: '3.8'

services:
  web:
    build: .
    command: >
      sh -c "python manage.py migrate &&
             python manage.py collectstatic --noinput &&
             gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4"
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - db
      - redis
    restart: always

  db:
    image: postgres:13
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: always

  redis:
    image: redis:7-alpine
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    restart: always

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    depends_on:
      - web
    restart: always

volumes:
  postgres_data:
  redis_data:
  static_volume:
  media_volume:
```

#### 5. Desplegar

```bash
# Construir y levantar
docker-compose -f docker-compose.prod.yml up -d --build

# Ver logs
docker-compose -f docker-compose.prod.yml logs -f

# Crear superusuario
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

---

### Opción 2: Despliegue Manual (sin Docker)

#### 1. Preparar el Servidor

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependencias
sudo apt install python3-pip python3-venv postgresql nginx -y
```

#### 2. Configurar PostgreSQL

```bash
sudo -u postgres psql

CREATE DATABASE ms_catalogue_prod;
CREATE USER catalogue_user WITH PASSWORD 'tu-password-segura';
ALTER ROLE catalogue_user SET client_encoding TO 'utf8';
ALTER ROLE catalogue_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE catalogue_user SET timezone TO 'America/Santiago';
GRANT ALL PRIVILEGES ON DATABASE ms_catalogue_prod TO catalogue_user;
\q
```

#### 3. Configurar la Aplicación

```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/catalogue_api.git
cd catalogue_api

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
pip install gunicorn

# Configurar .env
cp .env.prod .env
nano .env

# Ejecutar migraciones
python manage.py migrate

# Recolectar archivos estáticos
python manage.py collectstatic --noinput

# Crear superusuario
python manage.py createsuperuser
```

#### 4. Configurar Gunicorn

```bash
# Crear archivo de servicio systemd
sudo nano /etc/systemd/system/catalogue.service
```

```ini
[Unit]
Description=Catalogue API Gunicorn daemon
After=network.target

[Service]
User=tu-usuario
Group=www-data
WorkingDirectory=/home/tu-usuario/catalogue_api
Environment="PATH=/home/tu-usuario/catalogue_api/venv/bin"
ExecStart=/home/tu-usuario/catalogue_api/venv/bin/gunicorn \
          --workers 4 \
          --bind unix:/home/tu-usuario/catalogue_api/catalogue.sock \
          config.wsgi:application

[Install]
WantedBy=multi-user.target
```

```bash
# Iniciar servicio
sudo systemctl start catalogue
sudo systemctl enable catalogue
sudo systemctl status catalogue
```

#### 5. Configurar Nginx

```bash
sudo nano /etc/nginx/sites-available/catalogue
```

```nginx
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

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        alias /home/tu-usuario/catalogue_api/staticfiles/;
    }

    location /media/ {
        alias /home/tu-usuario/catalogue_api/media/;
    }

    location / {
        proxy_pass http://unix:/home/tu-usuario/catalogue_api/catalogue.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Habilitar sitio
sudo ln -s /etc/nginx/sites-available/catalogue /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 📊 Monitoreo y Mantenimiento

### Logs

```bash
# Docker
docker-compose -f docker-compose.prod.yml logs -f web

# Systemd
sudo journalctl -u catalogue -f

# Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Backups

```bash
# Backup de base de datos
docker-compose -f docker-compose.prod.yml exec db pg_dump -U catalogue_user ms_catalogue_prod > backup_$(date +%Y%m%d).sql

# Backup de archivos media
tar -czf media_backup_$(date +%Y%m%d).tar.gz media/
```

### Actualizaciones

```bash
# Actualizar código
git pull origin main

# Reconstruir y reiniciar
docker-compose -f docker-compose.prod.yml up -d --build

# Ejecutar migraciones
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate
```

---

## 🐛 Troubleshooting

### Error 500

```bash
# Ver logs de Django
docker-compose -f docker-compose.prod.yml logs web

# Verificar DEBUG=False
grep DEBUG .env

# Verificar ALLOWED_HOSTS
grep ALLOWED_HOSTS .env
```

### Base de datos no conecta

```bash
# Verificar que PostgreSQL esté corriendo
docker-compose -f docker-compose.prod.yml ps db

# Probar conexión
docker-compose -f docker-compose.prod.yml exec web python manage.py dbshell
```

### Archivos estáticos no cargan

```bash
# Recolectar archivos estáticos
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput

# Verificar permisos
ls -la staticfiles/
```

---

## 📞 Soporte

Para problemas o preguntas, contacta al equipo de desarrollo.

---

**Última actualización**: 2026-01-19
