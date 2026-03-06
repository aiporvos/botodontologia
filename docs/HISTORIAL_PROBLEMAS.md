# Historial de Problemas y Soluciones

Documentación de todos los errores encontrados durante el desarrollo y despliegue del proyecto, junto con sus soluciones.

---

## 1. Error: re2==20231101 (paquete inválido)

### Error
```
ERROR: failed to build: failed to solve: process "/bin/sh -c pip install --no-cache-dir -r requirements.txt" did not complete successfully: exit code: 1
```

### Análisis
El archivo `requirements.txt` contenía una línea inválida:
```
re2==20231101
```

2` no es un paquete pip válido (es una libreríaEl paquete `re C++ de Google que requiere instalación manual desde código fuente).

### Solución
1. Eliminar la línea `re2==20231101` del `requirements.txt`
2. Verificar que no se usaba en ningún archivo del proyecto

---

## 2. Error: Conflicto de dependencias (sqladmin + sqlalchemy)

### Error
```
ERROR: Cannot install -r requirements.txt (line 17), -r requirements.txt (line 9) and sqlalchemy==2.0.25 because these package versions have conflicting dependencies.

The conflict is caused by:
    sqlalchemy==2.0.25
    alembic 1.13.1 depends on SQLAlchemy>=1.3.0
    sqladmin 0.2.0 depends on sqlalchemy<1.5 and >=1.4
```

### Análisis
- `sqladmin 0.2.0` requiere `sqlalchemy<1.5` (versión 1.4.x)
- El proyecto tenía `sqlalchemy==2.0.25` (versión 2.x)
- **Conflicto**: No hay compatibilidad entre sqladmin 0.2.0 y SQLAlchemy 2.x

### Solución
Actualizar `sqladmin` a una versión compatible:
- Cambiar `sqladmin==0.2.0` → `sqladmin==0.23.0`

---

## 3. Error: spawn ENOTDIR

### Error
```
Initializing deployment
Build dockerfile: ✅
Source Type: github: ✅
Error ❌
spawn ENOTDIR
```

### Análisis
Este error en Dokploy ocurre cuando:
1. El Build Path no coincide con la estructura del repositorio
2. El Dockerfile no se encuentra en la ruta esperada
3. Problemas con la conexión de GitHub

### Solución
En Dokploy, configurar:
- **Build Path**: `/` (raíz del repositorio)
- Asegurarse de que el Dockerfile esté en la raíz

---

## 4. Error: no space left on device

### Error
```
failed to register layer: write /usr/lib/x86_64-linux-gnu/libLLVM.so.19.1: no space left on device
```

### Análisis
El servidor de Dokploy se quedó sin espacio en disco. No es un problema del código, sino de infraestructura.

### Solución
En el servidor de Dokploy (vía SSH):
```bash
docker system prune -a --volumes
df -h
```

---

## 5. Error: DATABASE_URL vacía

### Error
```
sqlalchemy.exc.ArgumentError: Could not parse SQLAlchemy URL from string ''
```

### Análisis
La variable `DATABASE_URL` estaba vacía porque:
1. En docker-compose.yml se usaba `${DATABASE_URL}`
2. Pero no se estaba pasando correctamente desde Dokploy

### Solución
Modificar `config.py` para construir la URL automáticamente desde componentes individuales:
```python
db_host: str = "postgres"
db_port: int = 5432
db_user: str = "clinic"
db_password: str = "clinicpass"
db_name: str = "clinic"

@property
def database_url(self) -> str:
    return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
```

Y en Dokploy solo era necesario configurar `DB_PASSWORD=clinicpass`

---

## 6. Error: UnboundExecutionError (ciclo de importación)

### Error
```
sqlalchemy.exc.UnboundExecutionError: Could not locate a bind configured on mapper Mapper[AdminUser(admin_users)], SQL expression or this Session.
```

### Análisis
Había un **ciclo de importación** entre:
- `app/database.py` → importaba `Base` 
- `app/models.py` → importaba `Base` desde `app.database`

Esto causaba que los modelos no estuvieran correctamente asociados al `engine`.

### Solución
1. Crear un archivo dedicado `app/models/base.py` con el `Base`:
```python
from sqlalchemy.orm import declarative_base
Base = declarative_base()
```

2. En `app/models/__init__.py` importar desde `app.models.base`:
```python
from app.models.base import Base
```

3. En `app/database.py` importar también desde `app.models`:
```python
from app.models import Base
```

---

## 7. Error: ModuleNotFoundError: app.models.base

### Error
```
ModuleNotFoundError: No module named 'app.models.base'; 'app.models' is not a package
```

### Análisis
El archivo `app/models.py` era un archivo simple, no un paquete (directorio con `__init__.py`).

### Solución
Convertir `app/models.py` en un paquete:
1. Crear directorio `app/models/`
2. Mover `app/models.py` → `app/models/__init__.py`

---

## 8. Error: 404 en dominio (Bad Gateway)

### Error
El dominio respondía con 404 Not Found

### Análisis
Posibles causas:
1. Puerto incorrecto en la configuración de Dokploy
2. La aplicación no estaba corriendo correctamente

### Solución
En Dokploy, en la configuración del dominio:
- **Port**: 8000 (no 80)
- Verificar que la app esté corriendo

---

## 9. Error: static_dir no válido en Admin

### Error
```
TypeError: Admin.__init__() got an unexpected keyword argument 'static_dir'
```

### Análisis
Se intentó usar un parámetro que no existe en la versión de sqladmin instalada.

### Solución
Quitar el parámetro `static_dir` de la configuración del Admin:
```python
admin = Admin(
    app,
    engine,
    title="Clínica Dental - Admin",
    base_url="/admin",
)
```

---

## 10. Error: column_filters en sqladmin

### Error
```
AttributeError: Neither 'InstrumentedAttribute' object nor 'Comparator' object associated with DentalTreatment.status has an attribute 'parameter_name'
```

### Análisis
Los `column_filters` no son compatibles con la versión de sqladmin 0.23.0. El parámetro `parameter_name` fue renombrado o eliminado.

### Solución
Eliminar todos los `column_filters` de las clases ModelView en `app/admin.py`:
- PatientAdmin
- ProfessionalAdmin  
- AvailabilityAdmin
- AppointmentAdmin
- DentalRecordAdmin
- ConsentAdmin
- ChatSessionAdmin
- DentalTreatmentAdmin
- PaymentAdmin
- DebtAdmin

---

## Lecciones Aprendidas

1. **Siempre verificar versiones** de paquetes antes de usarlos en producción
2. **Evitar ciclos de importación** separando Base en su propio archivo
3. **Configuración robusta** hacer que la app funcione sin DATABASE_URL explícita
4. **Limpiar espacio** en servidores antes de deploys grandes
5. **Probar localmente** antes de subir a producción
6. **Documentar errores** para referencia futura

---

## Archivos Modificados

| Archivo | Cambio |
|---------|--------|
| `requirements.txt` | Eliminado re2, actualizado sqladmin a 0.23.0 |
| `config.py` | Agregado @property para database_url |
| `app/database.py` | Reestructurado para evitar ciclos |
| `app/models.py` → `app/models/__init__.py` | Convertido en paquete |
| `app/models/base.py` | Creado (luego eliminado) |
| `app/admin.py` | Quitados column_filters, static_dir |
| `docs/` | Creada documentación completa |

---

## Estado Final

- ✅ App desplegada en Dokploy
- ✅ Base de datos PostgreSQL funcionando
- ✅ Panel admin accesible
- ✅ Documentación completa creada
