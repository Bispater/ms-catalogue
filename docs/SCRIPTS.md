# Scripts Disponibles

## 🚀 Scripts de Producción

### `quick-deploy.sh` - Deploy Rápido

**Propósito**: Desplegar cambios de código en producción

**Uso**:
```bash
# Deploy normal (rápido)
./quick-deploy.sh

# Deploy con rebuild completo
./quick-deploy.sh --rebuild
```

**Hace**:
1. `git pull origin develop`
2. `docker compose down`
3. `docker compose build`
4. `docker compose up -d`
5. Espera 30 segundos
6. Muestra estado

**Cuándo usar**:
- ✅ Cambios de código normales
- ✅ Actualizaciones de templates
- ✅ Cambios en .env.prod
- ✅ Despliegues diarios

**Tiempo**: 2-3 minutos

---

### `setup-nginx-host.sh` - Configurar Nginx

**Propósito**: Instalar y configurar Nginx en el host

**Uso**:
```bash
sudo ./setup-nginx-host.sh
```

**Hace**:
1. Instala Nginx (si no está)
2. Copia configuración
3. Crea symlinks
4. Crea directorios
5. Genera certificados SSL
6. Verifica y recarga

**Cuándo usar**:
- ✅ Primera vez desplegando
- ✅ Cambios en nginx-host.conf
- ✅ Reinstalar Nginx

**Tiempo**: 2-3 minutos

**Nota**: Solo se ejecuta UNA VEZ o cuando cambies la configuración de Nginx

---

## 📂 Scripts en `./scripts/`

### `start-prod.sh` - Deploy Interactivo

**Propósito**: Deploy completo con opciones interactivas

**Uso**:
```bash
./scripts/start-prod.sh
```

**Características**:
- Actualiza código (git pull)
- Verifica Docker
- Verifica .env.prod
- Pregunta si hacer backup
- Pregunta si hacer rebuild
- Aplica migraciones
- Colecta estáticos
- Muestra logs (opcional)

**Cuándo usar**:
- Primera vez desplegando
- Cuando quieres control total
- Cuando necesitas hacer backup

**Tiempo**: 5-15 minutos (según opciones)

---

## 🔄 Flujo de Trabajo Recomendado

### Primera Vez

```bash
# 1. Configurar Nginx (solo una vez)
sudo ./setup-nginx-host.sh

# 2. Deploy inicial
./scripts/start-prod.sh
```

### Despliegues Normales

```bash
# Un solo comando
./quick-deploy.sh
```

### Cambios Importantes

```bash
# Con rebuild completo
./quick-deploy.sh --rebuild
```

---

## 📋 Comparación

| Script | Interactivo | Git Pull | Rebuild | Backup | Tiempo |
|--------|-------------|----------|---------|--------|--------|
| `quick-deploy.sh` | No | ✅ | Opcional | No | 2-3 min |
| `quick-deploy.sh --rebuild` | No | ✅ | ✅ | No | 5-10 min |
| `start-prod.sh` | ✅ | ✅ | Pregunta | Pregunta | 5-15 min |
| `setup-nginx-host.sh` | Mínimo | No | N/A | No | 2-3 min |

---

## 🛠️ Desarrollo Local

Para desarrollo local, usa los scripts en la raíz:

```bash
./start   # Levantar entorno local
./stop    # Detener entorno local
./reset   # Reset completo
./logs    # Ver logs
```

---

## 📝 Crear Nuevos Scripts

Si necesitas crear un nuevo script:

1. Hazlo ejecutable: `chmod +x script.sh`
2. Agrega shebang: `#!/bin/bash`
3. Usa `set -e` para detener en errores
4. Documenta en este archivo

---

## 🔍 Troubleshooting

### Script no ejecuta

```bash
# Hacer ejecutable
chmod +x nombre-script.sh

# Verificar sintaxis
bash -n nombre-script.sh
```

### Git pull falla

```bash
# Ver estado
git status

# Descartar cambios locales
git reset --hard origin/develop
```

### Docker no responde

```bash
# Reiniciar Docker
sudo systemctl restart docker

# Ver logs
docker compose -f docker-compose.prod.yml logs
```

---

## 📚 Más Información

- [Guía de Despliegue](docs/DEPLOYMENT_GUIDE.md)
- [Setup Nginx Host](docs/SETUP_NGINX_HOST.md)
- [Configuraciones Nginx](NGINX_CONFIG.md)
