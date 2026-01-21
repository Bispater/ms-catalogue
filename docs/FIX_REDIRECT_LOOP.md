# 🔧 FIX: Loop de Redirección HTTPS (ERR_TOO_MANY_REDIRECTS)

## 📋 Problema

Al acceder a `https://catalogue.favric.cl/admin/` aparece:

```
Esta página no funciona
catalogue.favric.cl te redireccionó demasiadas veces.
ERR_TOO_MANY_REDIRECTS
```

---

## 🔍 Causa Raíz

**Doble redirección HTTPS** causada por:

1. ✅ **Nginx** redirige HTTP → HTTPS (correcto)
2. ❌ **Django** también intenta redirigir HTTP → HTTPS (incorrecto)
3. 🔄 **Loop infinito** de redirecciones

### Problemas Específicos Encontrados

1. **Archivo nginx incorrecto**: `docker-compose.prod.yml` usaba `nginx.conf` (desarrollo) en lugar de `nginx.prod.conf` (producción)

2. **Rutas SSL incorrectas**: `nginx.prod.conf` buscaba certificados en `/etc/nginx/ssl/` pero están en `/etc/letsencrypt/`

3. **Django con SECURE_SSL_REDIRECT=True**: Causaba loop cuando Nginx ya maneja HTTPS

---

## ✅ Solución Aplicada

### 1. Corregir `docker-compose.prod.yml`

**Antes**:
```yaml
volumes:
  - ./nginx.conf:/etc/nginx/conf.d/default.conf  # ❌ Archivo de desarrollo
  - /etc/letsencrypt/live/catalogue.favric.cl/fullchain.pem:/etc/letsencrypt/live/catalogue.favric.cl/fullchain.pem:ro
  - /etc/letsencrypt/live/catalogue.favric.cl/privkey.pem:/etc/letsencrypt/live/catalogue.favric.cl/privkey.pem:ro
  - ./ssl:/etc/nginx/ssl
```

**Ahora**:
```yaml
volumes:
  - ./nginx.prod.conf:/etc/nginx/conf.d/default.conf  # ✅ Archivo de producción
  - /etc/letsencrypt/live/catalogue.favric.cl:/etc/letsencrypt/live/catalogue.favric.cl:ro
```

### 2. Corregir `nginx.prod.conf`

**Antes**:
```nginx
ssl_certificate /etc/nginx/ssl/catalogue.favric.cl.crt;      # ❌ Ruta incorrecta
ssl_certificate_key /etc/nginx/ssl/catalogue.favric.cl.key;  # ❌ Ruta incorrecta
```

**Ahora**:
```nginx
ssl_certificate /etc/letsencrypt/live/catalogue.favric.cl/fullchain.pem;  # ✅ Let's Encrypt
ssl_certificate_key /etc/letsencrypt/live/catalogue.favric.cl/privkey.pem;  # ✅ Let's Encrypt
```

### 3. Configurar `.env.prod`

```bash
# Django NO debe redirigir, Nginx ya lo hace
SECURE_SSL_REDIRECT=False

# Pero las cookies deben ser seguras
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# HSTS en Nginx, no en Django
SECURE_HSTS_SECONDS=0
```

### 4. Agregar configuraciones CSRF en `settings.py`

```python
# Security settings
CSRF_TRUSTED_ORIGINS = os.getenv('CSRF_TRUSTED_ORIGINS', '').split(',') if os.getenv('CSRF_TRUSTED_ORIGINS') else []
CSRF_COOKIE_SECURE = os.getenv('CSRF_COOKIE_SECURE', 'False').lower() in ['1', 't', 'true', 'y', 'yes']
SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', 'False').lower() in ['1', 't', 'true', 'y', 'yes']
# ... más configuraciones
```

---

## 🚀 Aplicar la Solución

### Opción 1: Script Automático (Recomendado)

```bash
# En el servidor
cd /var/ms-catalogue

# Pull cambios
git pull origin develop

# Ejecutar script de fix
./fix-redirect-loop.sh
```

### Opción 2: Manual

```bash
# En el servidor
cd /var/ms-catalogue

# 1. Pull cambios
git pull origin develop

# 2. Verificar .env.prod
grep "SECURE_SSL_REDIRECT" .env.prod
# Debe mostrar: SECURE_SSL_REDIRECT=False

# 3. Detener contenedores
docker compose -f docker-compose.prod.yml down

# 4. Limpiar logs (opcional)
rm -rf ./logs/nginx/*

# 5. Levantar servicios
docker compose -f docker-compose.prod.yml up -d

# 6. Esperar 30 segundos
sleep 30

# 7. Verificar estado
docker compose -f docker-compose.prod.yml ps

# 8. Verificar configuración Django
docker compose -f docker-compose.prod.yml exec web python -c "
from django.conf import settings
print('SECURE_SSL_REDIRECT:', settings.SECURE_SSL_REDIRECT)
print('CSRF_TRUSTED_ORIGINS:', settings.CSRF_TRUSTED_ORIGINS)
"
```

---

## 🌐 Limpiar Cookies del Navegador

**IMPORTANTE**: Después de aplicar los cambios, debes limpiar las cookies.

### Chrome/Edge
1. Ir a `chrome://settings/clearBrowserData`
2. Seleccionar **"Cookies y otros datos de sitios"**
3. Rango de tiempo: **"Desde siempre"**
4. Click en **"Borrar datos"**

### Firefox
1. Ir a `about:preferences#privacy`
2. En "Cookies y datos del sitio" → **"Limpiar datos"**
3. Seleccionar **"Cookies y datos del sitio"**
4. Click en **"Limpiar"**

### O usar Modo Incógnito
- Chrome: `Ctrl+Shift+N`
- Firefox: `Ctrl+Shift+P`

---

## ✅ Verificar que Funciona

```bash
# 1. Acceder a la URL
https://catalogue.favric.cl/admin/

# 2. Deberías ver el formulario de login ✅

# 3. Verificar headers (DevTools → Network)
# Debe haber UNA redirección HTTP → HTTPS (de Nginx)
# NO debe haber múltiples redirecciones
```

---

## 📊 Arquitectura Correcta

```
┌─────────────┐
│   Usuario   │
└──────┬──────┘
       │ HTTP
       ▼
┌─────────────────────┐
│   Nginx (Puerto 80) │  ← Redirige HTTP → HTTPS (301)
└─────────────────────┘
       │ HTTPS
       ▼
┌─────────────────────┐
│  Nginx (Puerto 443) │  ← Maneja SSL/TLS
└──────┬──────────────┘
       │ HTTP (interno)
       ▼
┌─────────────────────┐
│  Django (Puerto 8000)│  ← NO redirige (SECURE_SSL_REDIRECT=False)
└─────────────────────┘
```

---

## 🔒 Configuración de Seguridad Final

### `.env.prod`
```bash
# Django NO redirige (Nginx lo hace)
SECURE_SSL_REDIRECT=False

# Cookies seguras (solo HTTPS)
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
CSRF_COOKIE_HTTPONLY=False  # Para compatibilidad con login

# CSRF dominios confiables
CSRF_TRUSTED_ORIGINS=https://catalogue.favric.cl,https://www.catalogue.favric.cl

# HSTS en Nginx (no en Django)
SECURE_HSTS_SECONDS=0
```

### `nginx.prod.conf`
```nginx
# Redirección HTTP → HTTPS (solo aquí)
server {
    listen 80;
    server_name catalogue.favric.cl;
    return 301 https://$server_name$request_uri;
}

# HTTPS con HSTS
server {
    listen 443 ssl http2;
    server_name catalogue.favric.cl;
    
    # Certificados Let's Encrypt
    ssl_certificate /etc/letsencrypt/live/catalogue.favric.cl/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/catalogue.favric.cl/privkey.pem;
    
    # HSTS (aquí, no en Django)
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    
    # Proxy a Django
    location / {
        proxy_pass http://web:8000;
        proxy_set_header X-Forwarded-Proto $scheme;
        # ...
    }
}
```

---

## 🐛 Debugging

### Ver logs de Nginx
```bash
docker compose -f docker-compose.prod.yml logs -f nginx
```

### Ver logs de Django
```bash
docker compose -f docker-compose.prod.yml logs -f web
```

### Verificar configuración de Django
```bash
docker compose -f docker-compose.prod.yml exec web python manage.py shell

# En el shell:
from django.conf import settings
print("SECURE_SSL_REDIRECT:", settings.SECURE_SSL_REDIRECT)
print("CSRF_TRUSTED_ORIGINS:", settings.CSRF_TRUSTED_ORIGINS)
print("ALLOWED_HOSTS:", settings.ALLOWED_HOSTS)
```

### Probar redirección con curl
```bash
# Debe redirigir UNA vez (301)
curl -I http://catalogue.favric.cl/admin/

# Debe responder 200 OK
curl -I https://catalogue.favric.cl/admin/
```

---

## 📝 Checklist de Verificación

- [ ] `docker-compose.prod.yml` usa `nginx.prod.conf`
- [ ] `nginx.prod.conf` tiene rutas correctas a Let's Encrypt
- [ ] `.env.prod` tiene `SECURE_SSL_REDIRECT=False`
- [ ] `.env.prod` tiene `CSRF_TRUSTED_ORIGINS` configurado
- [ ] `core/settings.py` lee las variables de seguridad
- [ ] Contenedores reiniciados después de cambios
- [ ] Cookies del navegador limpiadas
- [ ] Login funciona correctamente ✅

---

## 📚 Referencias

- [Django Security Settings](https://docs.djangoproject.com/en/4.2/ref/settings/#security)
- [Nginx SSL Configuration](https://nginx.org/en/docs/http/configuring_https_servers.html)
- [Let's Encrypt Certificates](https://letsencrypt.org/docs/)
- [CSRF Protection](https://docs.djangoproject.com/en/4.2/ref/csrf/)

---

**Última actualización**: 2026-01-20
**Estado**: ✅ Solucionado
