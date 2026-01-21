# Guía de Despliegue en Producción

## Scripts Disponibles

| Script | Descripción | Cuándo Usar |
|--------|-------------|-------------|
| ./quick-deploy.sh | Despliegue rápido automático | Cambios de código normales |
| ./quick-deploy.sh --rebuild | Despliegue con rebuild completo | Cambios en Dockerfile o requirements |
| ./start-prod | Despliegue interactivo completo | Primera vez o configuración compleja |

## Despliegue Rápido

### Uso Normal

```bash
cd /var/ms-catalogue
./quick-deploy.sh
```

Hace automáticamente:
1. git pull origin develop
2. docker compose down
3. docker compose build
4. docker compose up -d
5. Espera 30 segundos
6. Muestra estado

Tiempo: 2-3 minutos

### Con Rebuild Completo

```bash
./quick-deploy.sh --rebuild
```

Usar cuando:
- Cambiaste Dockerfile
- Agregaste dependencias en requirements.txt
- Primera vez que despliegas

## Flujo de Trabajo

### Desarrollo a Producción

```bash
# En tu máquina local
git push origin develop

# En el servidor
cd /var/ms-catalogue
./quick-deploy.sh
```

## Solución de Problemas

### Nginx no inicia

```bash
./diagnose-nginx.sh
docker compose -f docker-compose.prod.yml logs nginx
```

### Loop de redirección

```bash
./fix-redirect-loop.sh
```

### Ver logs

```bash
docker compose -f docker-compose.prod.yml logs -f
```
