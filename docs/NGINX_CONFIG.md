# Configuraciones de Nginx

## Archivos Disponibles

### 1. `nginx.conf` - Desarrollo Local

**Uso**: Desarrollo local con Docker Compose

**Ubicación**: Se monta automáticamente en `docker-compose.yml`

**Características**:
- Solo HTTP (puerto 80)
- Sin SSL
- Proxy a Django en `web:8000`
- Para desarrollo local

**Comando**:
```bash
./start  # Usa nginx.conf automáticamente
```

---

### 2. `nginx-host.conf` - Producción (Host)

**Uso**: Producción con Nginx instalado en el host

**Ubicación**: Se copia a `/etc/nginx/sites-available/catalogue.favric.cl`

**Características**:
- HTTP y HTTPS (puertos 80 y 443)
- SSL con Let's Encrypt
- Proxy a Django en `127.0.0.1:8000`
- Headers de seguridad
- HSTS habilitado

**Instalación**:
```bash
# Automática
sudo ./setup-nginx-host.sh

# Manual
sudo cp nginx-host.conf /etc/nginx/sites-available/catalogue.favric.cl
sudo ln -s /etc/nginx/sites-available/catalogue.favric.cl /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## Arquitecturas

### Desarrollo Local

```
Navegador → Nginx (Docker:80) → Django (Docker:8000)
```

Archivo: `nginx.conf`

---

### Producción

```
Internet → Nginx (Host:443) → Django (Docker:8000)
           ↓ SSL
```

Archivo: `nginx-host.conf`

---

## Cuál Usar

| Entorno | Archivo | Dónde |
|---------|---------|-------|
| Desarrollo Local | `nginx.conf` | Docker Compose |
| Producción | `nginx-host.conf` | Host (`/etc/nginx/`) |

---

## Modificar Configuración

### Desarrollo

1. Editar `nginx.conf`
2. Reiniciar: `docker compose restart nginx`

### Producción

1. Editar `nginx-host.conf`
2. Copiar al servidor:
   ```bash
   scp nginx-host.conf root@srv702740:/var/ms-catalogue/
   ```
3. En el servidor:
   ```bash
   sudo cp nginx-host.conf /etc/nginx/sites-available/catalogue.favric.cl
   sudo nginx -t
   sudo systemctl reload nginx
   ```

---

## Troubleshooting

### Desarrollo - Nginx no inicia

```bash
# Ver logs
docker compose logs nginx

# Verificar sintaxis
docker compose exec nginx nginx -t

# Reiniciar
docker compose restart nginx
```

### Producción - Nginx no inicia

```bash
# Ver logs
sudo tail -f /var/log/nginx/error.log

# Verificar sintaxis
sudo nginx -t

# Reiniciar
sudo systemctl restart nginx
```

---

## Notas

- **NO** usar `nginx.conf` en producción (no tiene SSL)
- **NO** usar `nginx-host.conf` en desarrollo (requiere certificados)
- Los certificados SSL se generan automáticamente con `setup-nginx-host.sh`
- Nginx en producción corre en el HOST, no en Docker
