# Docker

## Dockerfile

El Dockerfile crea una imagen Docker para la aplicación Python:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Crear directorios necesarios
RUN mkdir -p static templates

# Exponer puerto
EXPOSE 8000

# Comando de inicio
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Explicación

| Instruccion | Descripción |
|-------------|-------------|
| FROM python:3.11-slim | Imagen base Python 3.11 slim |
| WORKDIR /app | Directorio de trabajo |
| apt-get install gcc libpq-dev | Dependencias para compilar psycopg2 |
| pip install | Instalar dependencias Python |
| COPY . . | Copiar código fuente |
| EXPOSE 8000 | Exponer puerto |
| CMD | Comando de inicio |

---

## docker-compose.yml

Define los servicios de la aplicación:

```yaml
services:
  clinic-app:
    build: .
    container_name: clinic-app
    ports:
      - "8000:8000"
    environment:
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - BOT_SECRET=${BOT_SECRET}
      - DATABASE_URL=${DATABASE_URL}
      - CALCOM_URL=${CALCOM_URL}
      - CALCOM_API_KEY=${CALCOM_API_KEY}
      - EVOLUTION_URL=${EVOLUTION_URL}
      - EVOLUTION_API_KEY=${EVOLUTION_API_KEY}
      - EVOLUTION_INSTANCE_NAME=${EVOLUTION_INSTANCE_NAME}
      - EVOLUTION_INSTANCE_TOKEN=${EVOLUTION_INSTANCE_TOKEN}
      - DEBUG=true
      - ADMIN_USERNAME=admin
      - ADMIN_PASSWORD=${ADMIN_PASSWORD}
    restart: unless-stopped
    depends_on:
      - postgres
    networks:
      - clinic-network

  postgres:
    image: postgres:16
    container_name: clinic-db
    environment:
      POSTGRES_USER: clinic
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: clinic
    volumes:
      - pgdata:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: unless-stopped
    networks:
      - clinic-network

volumes:
  pgdata:

networks:
  clinic-network:
    driver: bridge
```

### Servicios

| Servicio | Descripción | Puerto |
|----------|-------------|--------|
| clinic-app | Aplicación FastAPI | 8000 |
| postgres | Base de datos PostgreSQL | 5432 |

### Variables de Entorno

| Variable | Descripción |
|----------|-------------|
| DB_PASSWORD | Contraseña PostgreSQL |
| TELEGRAM_BOT_TOKEN | Token del bot |
| Otras vars | Ver CONFIGURACION.md |

---

## Comandos Docker

### Desarrollo Local

```bash
# Iniciar servicios
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener servicios
docker-compose down

# Reconstruir imagen
docker-compose build --no-cache
```

### Production

```bash
# Iniciar con restart automático
docker-compose up -d --restart always

# Ver estado
docker-compose ps

# Reiniciar servicio
docker-compose restart clinic-app
```

---

## Redes

Los contenedores están en la red `clinic-network`:
- Se comunican por nombre de servicio
- `clinic-app` conecta a `postgres:5432` (no localhost)

---

## Volúmenes

| Volumen | Destino | Descripción |
|---------|---------|-------------|
| pgdata | /var/lib/postgresql/data | Datos de PostgreSQL |

---

## Producción con Dokploy

Dokploy maneja Docker automáticamente. Ver DESPLIEGUE.md para detalles.
