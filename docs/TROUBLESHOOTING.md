# Solución de Problemas

## Errores Comunes

### Error: "Could not locate a bind"

**Síntoma:**
```
sqlalchemy.exc.UnboundExecutionError: Could not locate a bind configured on mapper
```

**Causa:** Ciclo de importación entre `database.py` y `models.py`

**Solución:**
1. Asegúrate de que `Base` esté definido en un archivo separado (`app/models/__init__.py`)
2. No importar `Base` desde `database.py` en los modelos

---

### Error: "MODULE_NOT_FOUND: app.models.base"

**Síntoma:**
```
ModuleNotFoundError: No module named 'app.models.base'
```

**Causa:** El archivo `app/models.py` no se convirtió en paquete

**Solución:**
1. Renombrar `app/models.py` a `app/models/__init__.py`
2. Crear directorio `app/models/`

---

### Error: Bad Gateway (404)

**Síntoma:** Al acceder al dominio muestra 404

**Causas y soluciones:**

1. **Puerto incorrecto**
   - Verifica que el puerto sea `8000` (no 80)

2. **DNS no propagado**
   - Espera unos minutos o verifica el DNS

3. **App no inici**
   - Revisa los logs en Dokploy

---

### Error: "no space left on device"

**Síntoma:**
```
failed to register layer: write ... no space left on device
```

**Causa:** Disco del servidor lleno

**Solución (en el servidor):**
```bash
docker system prune -a --volumes
df -h
```

---

### Error: Database connection

**Síntoma:**
```
Could not parse SQLAlchemy URL from string ''
```

**Causa:** Variable `DATABASE_URL` vacía

**Solución:**
1. Configurar `DB_PASSWORD` en Environment de Dokploy
2. O configurar `DATABASE_URL` completa

---

### Error: ENOTFOUND (DNS)

**Síntoma:**
```
queryA ENOTFOUND tudominio.com
```

**Causa:** El dominio no existe o no apunta al servidor

**Solución:**
1. Verificar que el dominio esté registrado
2. Configurar DNS para que apunte a la IP del servidor
3. Esperar propagación DNS (puede tomar horas)

---

### Error: sqladmin "model" parameter

**Síntoma:**
```
No parameter named "model"
```

**Causa:** Versión incompatible de sqladmin

**Solución:**
- Usar sqladmin >= 0.20.0 con la sintaxis:
```python
class PatientAdmin(ModelView, model=Patient):
```

---

### Error: column_filters

**Síntoma:**
```
AttributeError: ... has an attribute 'parameter_name'
```

**Causa:** Los filtros no son compatibles con la versión

**Solución:**
- Quitar `column_filters` de las clases ModelView en `admin.py`

---

## Ver Logs

### Dokploy
1. Ir a la aplicación
2. Pestaña **Logs**

### Docker Local
```bash
docker-compose logs -f clinic-app
docker-compose logs -f postgres
```

---

## Regenerar Base de Datos

Si necesitas empezar de cero:

1. Eliminar contenedor y volumen de PostgreSQL:
```bash
docker-compose down -v
```

2. Volver a iniciar:
```bash
docker-compose up -d
```

---

## Verificar Variables de Entorno

En la aplicación:
```python
from config import settings
print(settings.database_url)
```

---

## Reconstruir Imagen Docker

```bash
docker-compose build --no-cache
docker-compose up -d
```

---

## Contacto

Si el problema persiste, revisa:
1. Logs de la aplicación
2. Variables de entorno
3. Conexión a Internet
4. Estado de los servicios externos (Telegram, WhatsApp)
