# 🚀 Despliegue en Producción - catalogue.favric.cl

> **Guía de despliegue para el servidor de producción**  
> **Dominio**: https://catalogue.favric.cl/  
> **Fecha**: 2026-01-20

---

## 📋 **Pre-requisitos**

### **En el Servidor**
- Docker y Docker Compose instalados
- Certificados SSL para `catalogue.favric.cl`
- Acceso SSH al servidor
- Puertos 80 y 443 abiertos

### **Archivos Necesarios**
- `.env.prod` configurado
- `docker-compose.prod.yml`
- `nginx.prod.conf`
- Certificados SSL en directorio `ssl/`

---

## 🔐 **Paso 1: Configurar Variables de Entorno**

### **Editar `.env.prod`**

```bash
nano .env.prod
```

### **Variables CRÍTICAS a Cambiar**:

#### **1. SECRET_KEY**
```bash
# Generar nueva clave
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Copiar el resultado en .env.prod
SECRET_KEY=tu-clave-generada-aqui
```

#### **2. Contraseña de Base de Datos**
```bash
DB_PASSWORD=TuContraseñaSegura123!@#
POSTGRES_PASSWORD=TuContraseñaSegura123!@#  # Debe ser la misma
```

#### **3. Contraseña de Redis**
```bash
REDIS_PASSWORD=TuContraseñaRedisSegura456!@#
```

#### **4. Email (Opcional)**
```bash
EMAIL_HOST_USER=noreply@favric.cl
EMAIL_HOST_PASSWORD=tu-contraseña-email
```

---

## 🔒 **Paso 2: Configurar Certificados SSL**

### **Opción A: Usar Certbot (Let's Encrypt)**

```bash
# Instalar certbot
sudo apt-get update
sudo apt-get install certbot

# Obtener certificados
sudo certbot certonly --standalone -d catalogue.favric.cl

# Copiar certificados al proyecto
mkdir -p ssl
sudo cp /etc/letsencrypt/live/catalogue.favric.cl/fullchain.pem ssl/catalogue.favric.cl.crt
sudo cp /etc/letsencrypt/live/catalogue.favric.cl/privkey.pem ssl/catalogue.favric.cl.key
sudo chmod 644 ssl/catalogue.favric.cl.crt
sudo chmod 600 ssl/catalogue.favric.cl.key
```

### **Opción B: Certificados Existentes**

```bash
# Crear directorio SSL
mkdir -p ssl

# Copiar tus certificados
cp /ruta/a/tu/certificado.crt ssl/catalogue.favric.cl.crt
cp /ruta/a/tu/clave.key ssl/catalogue.favric.cl.key

# Permisos correctos
chmod 644 ssl/catalogue.favric.cl.crt
chmod 600 ssl/catalogue.favric.cl.key
```

---

## 📦 **Paso 3: Preparar Directorios**

```bash
# Crear directorios necesarios
mkdir -p logs/nginx
mkdir -p backups
mkdir -p media
mkdir -p ssl

# Permisos
chmod 755 logs
chmod 755 backups
chmod 755 media
```

---

## 🐳 **Paso 4: Desplegar con Docker**

### **Primera vez (Build y Deploy)**

```bash
# Build de la imagen
docker compose -f docker-compose.prod.yml build

# Iniciar servicios
docker compose -f docker-compose.prod.yml up -d

# Ver logs
docker compose -f docker-compose.prod.yml logs -f
```

### **Crear Superusuario**

```bash
docker compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

### **Verificar Estado**

```bash
# Ver servicios
docker compose -f docker-compose.prod.yml ps

# Ver logs
docker compose -f docker-compose.prod.yml logs web
docker compose -f docker-compose.prod.yml logs nginx
docker compose -f docker-compose.prod.yml logs db
```

---

## ✅ **Paso 5: Verificar Despliegue**

### **1. Health Check**
```bash
curl https://catalogue.favric.cl/health/
# Debe responder: healthy
```

### **2. Admin de Django**
```
https://catalogue.favric.cl/admin/
```

### **3. API**
```bash
curl https://catalogue.favric.cl/api/products/
```

### **4. CORS desde Angular Local**
```bash
# Desde tu app Angular local (http://localhost:4200)
# Debe poder hacer peticiones sin errores CORS
```

---

## 🔄 **Actualizaciones Posteriores**

### **Actualizar Código**

```bash
# Pull del código nuevo
git pull origin main

# Rebuild y restart
docker compose -f docker-compose.prod.yml build web
docker compose -f docker-compose.prod.yml up -d

# Aplicar migraciones si hay
docker compose -f docker-compose.prod.yml exec web python manage.py migrate

# Colectar estáticos
docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
```

### **Restart Rápido**

```bash
# Solo reiniciar servicios
docker compose -f docker-compose.prod.yml restart web
docker compose -f docker-compose.prod.yml restart nginx
```

---

## 🗄️ **Backups Automáticos**

Los backups se crean automáticamente cada 24 horas en el directorio `backups/`.

### **Backup Manual**

```bash
# Crear backup ahora
docker compose -f docker-compose.prod.yml exec db pg_dump -U catalogue_user catalogue_favric_prod > backups/manual_backup_$(date +%Y%m%d_%H%M%S).sql
```

### **Restaurar Backup**

```bash
# Restaurar desde backup
docker compose -f docker-compose.prod.yml exec -T db psql -U catalogue_user catalogue_favric_prod < backups/backup_20260120_120000.sql
```

---

## 🔍 **Monitoreo y Logs**

### **Ver Logs en Tiempo Real**

```bash
# Todos los servicios
docker compose -f docker-compose.prod.yml logs -f

# Solo web
docker compose -f docker-compose.prod.yml logs -f web

# Solo nginx
docker compose -f docker-compose.prod.yml logs -f nginx

# Últimas 100 líneas
docker compose -f docker-compose.prod.yml logs --tail=100 web
```

### **Logs de Nginx**

```bash
# Access log
tail -f logs/nginx/catalogue.favric.cl.access.log

# Error log
tail -f logs/nginx/catalogue.favric.cl.error.log
```

---

## 🛠️ **Comandos Útiles**

### **Django Management**

```bash
# Shell de Django
docker compose -f docker-compose.prod.yml exec web python manage.py shell

# Crear catálogo
docker compose -f docker-compose.prod.yml exec web python manage.py shell
>>> from api.models import Organization, Catalogue
>>> org = Organization.objects.first()
>>> Catalogue.objects.create(name="Catálogo Principal", slug="catalogo-principal", organization=org)

# Importar productos
docker compose -f docker-compose.prod.yml exec web python scripts/transform_client_excel.py /path/to/excel.xlsx catalogo-principal
```

### **Base de Datos**

```bash
# Acceder a PostgreSQL
docker compose -f docker-compose.prod.yml exec db psql -U catalogue_user catalogue_favric_prod

# Ver tablas
\dt

# Salir
\q
```

---

## 🔧 **Troubleshooting**

### **Problema: CORS no funciona**

```bash
# Verificar configuración CORS en .env.prod
grep CORS .env.prod

# Debe incluir:
CORS_ALLOWED_ORIGINS=https://catalogue.favric.cl,http://localhost:4200,http://localhost:4201

# Reiniciar nginx
docker compose -f docker-compose.prod.yml restart nginx
```

### **Problema: 502 Bad Gateway**

```bash
# Ver logs de web
docker compose -f docker-compose.prod.yml logs web

# Verificar que web está corriendo
docker compose -f docker-compose.prod.yml ps web

# Reiniciar web
docker compose -f docker-compose.prod.yml restart web
```

### **Problema: Certificado SSL inválido**

```bash
# Verificar certificados
ls -la ssl/

# Verificar permisos
chmod 644 ssl/catalogue.favric.cl.crt
chmod 600 ssl/catalogue.favric.cl.key

# Reiniciar nginx
docker compose -f docker-compose.prod.yml restart nginx
```

### **Problema: Base de datos no conecta**

```bash
# Ver logs de db
docker compose -f docker-compose.prod.yml logs db

# Verificar variables
docker compose -f docker-compose.prod.yml exec web env | grep DB_

# Reiniciar db
docker compose -f docker-compose.prod.yml restart db
```

---

## 📊 **Configuración CORS Actual**

### **Orígenes Permitidos**:
- ✅ `https://catalogue.favric.cl` (Producción)
- ✅ `https://favric.cl` (Dominio principal)
- ✅ `http://localhost:4200` (Angular local)
- ✅ `http://localhost:4201` (Angular local alternativo)
- ✅ `http://127.0.0.1:4200` (Angular local IP)
- ✅ `http://127.0.0.1:4201` (Angular local IP alternativo)

### **Métodos Permitidos**:
- GET, POST, PUT, PATCH, DELETE, OPTIONS

### **Headers Permitidos**:
- Accept, Authorization, Content-Type, X-CSRFToken, etc.

---

## 🔐 **Seguridad**

### **Configuraciones Activas**:
- ✅ HTTPS forzado (redirect HTTP → HTTPS)
- ✅ HSTS habilitado (1 año)
- ✅ Cookies seguras (Secure, HttpOnly, SameSite)
- ✅ CSRF protection
- ✅ XSS protection
- ✅ Clickjacking protection
- ✅ SSL/TLS moderno (TLS 1.2+)

---

## 📞 **Soporte**

### **Archivos de Configuración**:
- `.env.prod` - Variables de entorno
- `docker-compose.prod.yml` - Orquestación Docker
- `nginx.prod.conf` - Configuración Nginx
- `Dockerfile` - Imagen Docker

### **Documentación**:
- [PRODUCTION_README.md](PRODUCTION_README.md)
- [DOCKER_README.md](DOCKER_README.md)
- [FINAL_SUMMARY.md](FINAL_SUMMARY.md)

---

## ✅ **Checklist de Despliegue**

- [ ] Variables de entorno configuradas en `.env.prod`
- [ ] SECRET_KEY generada y configurada
- [ ] Contraseñas de DB y Redis configuradas
- [ ] Certificados SSL en directorio `ssl/`
- [ ] Directorios creados (logs, backups, media)
- [ ] Docker Compose ejecutado
- [ ] Servicios corriendo (web, db, nginx)
- [ ] Superusuario creado
- [ ] Health check funcionando
- [ ] Admin accesible
- [ ] API funcionando
- [ ] CORS probado desde Angular local
- [ ] Backups automáticos configurados

---

**Dominio**: https://catalogue.favric.cl/  
**Estado**: ✅ Configurado y listo para desplegar  
**CORS**: ✅ Habilitado para localhost Angular

---

**Fin del documento**
