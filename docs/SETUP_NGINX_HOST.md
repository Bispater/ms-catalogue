# Configuración de Nginx en el Host (Arquitectura Simplificada)

## Arquitectura

```
Internet
   ↓
Nginx (Host - Puerto 80/443)
   ↓ SSL/HTTPS
   ↓ Proxy a http://127.0.0.1:8000
   ↓
Django (Docker - Puerto 8000)
   ↓
PostgreSQL (Docker - Puerto 5432)
```

## Beneficios

- ✅ Nginx en el host maneja SSL/HTTPS
- ✅ Django solo HTTP interno (más simple)
- ✅ Sin complejidad de certificados en Docker
- ✅ Más fácil de mantener y debuggear
- ✅ Nginx puede servir múltiples aplicaciones

## Instalación

### Paso 1: Configurar Nginx en el Host

```bash
# En el servidor
cd /var/ms-catalogue

# Ejecutar script de setup (como root)
sudo ./setup-nginx-host.sh
```

El script hace automáticamente:
1. Instala Nginx (si no está)
2. Copia configuración a /etc/nginx/sites-available/
3. Crea symlink en /etc/nginx/sites-enabled/
4. Elimina configuración default
5. Crea directorios para static/media
6. Genera certificados SSL con Certbot
7. Verifica sintaxis
8. Recarga Nginx

### Paso 2: Desplegar Django

```bash
# En el servidor
cd /var/ms-catalogue
./quick-deploy.sh
```

### Paso 3: Verificar

```bash
# Ver estado de Nginx
sudo systemctl status nginx

# Ver logs de Nginx
sudo tail -f /var/log/nginx/catalogue.favric.cl.error.log

# Ver logs de Django
docker compose -f docker-compose.prod.yml logs -f web

# Acceder
https://catalogue.favric.cl/admin/
```

## Configuración Manual (Opcional)

Si prefieres configurar manualmente:

### 1. Instalar Nginx

```bash
sudo apt update
sudo apt install -y nginx certbot python3-certbot-nginx
```

### 2. Copiar Configuración

```bash
sudo cp nginx-host.conf /etc/nginx/sites-available/catalogue.favric.cl
sudo ln -s /etc/nginx/sites-available/catalogue.favric.cl /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
```

### 3. Crear Directorios

```bash
sudo mkdir -p /var/ms-catalogue/staticfiles
sudo mkdir -p /var/ms-catalogue/media
sudo chown -R www-data:www-data /var/ms-catalogue/staticfiles
sudo chown -R www-data:www-data /var/ms-catalogue/media
```

### 4. Generar Certificados SSL

```bash
sudo certbot --nginx -d catalogue.favric.cl
```

### 5. Verificar y Recargar

```bash
sudo nginx -t
sudo systemctl reload nginx
sudo systemctl enable nginx
```

## Archivos Estáticos

Django colecta archivos estáticos en el contenedor, pero Nginx los sirve desde el host:

```bash
# Colectar estáticos (desde Django)
docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput

# Los archivos se guardan en el volumen que Nginx puede leer
# /var/ms-catalogue/staticfiles/
```

## Comandos Útiles

### Nginx

```bash
# Estado
sudo systemctl status nginx

# Recargar configuración
sudo systemctl reload nginx

# Reiniciar
sudo systemctl restart nginx

# Verificar sintaxis
sudo nginx -t

# Ver logs
sudo tail -f /var/log/nginx/catalogue.favric.cl.access.log
sudo tail -f /var/log/nginx/catalogue.favric.cl.error.log
```

### Certificados SSL

```bash
# Renovar certificados
sudo certbot renew

# Ver certificados
sudo certbot certificates

# Renovación automática (ya configurada)
sudo systemctl status certbot.timer
```

### Django

```bash
# Ver logs
docker compose -f docker-compose.prod.yml logs -f web

# Colectar estáticos
docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput

# Acceder a shell
docker compose -f docker-compose.prod.yml exec web python manage.py shell
```

## Solución de Problemas

### Nginx no inicia

```bash
# Ver error
sudo nginx -t
sudo systemctl status nginx
sudo tail -f /var/log/nginx/error.log
```

### Puerto 8000 no responde

```bash
# Verificar que Django está corriendo
docker compose -f docker-compose.prod.yml ps web

# Probar directamente
curl http://127.0.0.1:8000/admin/
```

### Archivos estáticos no cargan

```bash
# Verificar permisos
ls -la /var/ms-catalogue/staticfiles/

# Colectar de nuevo
docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput

# Verificar que Nginx puede leer
sudo -u www-data ls /var/ms-catalogue/staticfiles/
```

### Certificados SSL

```bash
# Verificar certificados
sudo certbot certificates

# Renovar manualmente
sudo certbot renew --dry-run
```

## Actualización de Código

```bash
# Método rápido
cd /var/ms-catalogue
./quick-deploy.sh

# Django se reinicia automáticamente
# Nginx NO necesita reiniciarse (solo si cambias nginx-host.conf)
```

## Configuración de Firewall

```bash
# Permitir HTTP y HTTPS
sudo ufw allow 'Nginx Full'

# O manualmente
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Verificar
sudo ufw status
```

## Resumen

Esta arquitectura es más simple y robusta:
- Nginx en el host maneja SSL y proxy
- Django en Docker solo HTTP
- Fácil de mantener y debuggear
- Estándar de la industria
