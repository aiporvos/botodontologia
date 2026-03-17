# AgentBot - Sistema de Agentes Especializados

## Configuración de Agentes para Dental Studio Pro

Este documento define los agentes especializados que pueden usar las skills del proyecto AgentBot.

---

## Agentes Disponibles

### 1. 🏗️ Arquitecto de Producto

**Nombre:** `dental-architect`
**Skill principal:** `dental-product-architect`

**Uso:**
```
Usar @dental-architect cuando necesites:
- Diseñar la arquitectura de un nuevo módulo
- Planificar la estructura de datos
- Definir flujos de negocio
- Crear documentación técnica
- Reorganizar funcionalidades existentes
```

**Ejemplo:**
```
@dental-architect Necesito diseñar el módulo de facturación electrónica con integración a AFIP
```

---

### 2. 🎨 Diseñador UI/UX

**Nombre:** `dental-designer`
**Skill principal:** `dental-react-ui`

**Uso:**
```
Usar @dental-designer cuando necesites:
- Crear una nueva pantalla
- Diseñar un dashboard
- Implementar componentes React
- Definir la experiencia de usuario
- Mejorar la interfaz existente
```

**Ejemplo:**
```
@dental-designer Crea una pantalla de dashboard para el módulo de pagos con KPIs de cobranzas
```

---

### 3. 💻 Desarrollador Backend

**Nombre:** `dental-backend`
**Skills:** `dental-admin-crud`, `dental-scheduling`, `dental-security-audit`

**Uso:**
```
Usar @dental-backend cuando necesites:
- Crear endpoints API
- Implementar modelos de datos
- Desarrollar lógica de negocio
- Configurar permisos y seguridad
- Crear servicios backend
```

**Ejemplo:**
```
@dental-backend Necesito un endpoint para reprogramar turnos con validación de disponibilidad
```

---

### 4. 📅 Especialista en Agenda

**Nombre:** `dental-scheduler`
**Skill principal:** `dental-scheduling`

**Uso:**
```
Usar @dental-scheduler cuando necesites:
- Implementar lógica de turnos
- Calcular disponibilidad
- Gestionar calendarios
- Manejar estados de turnos
- Crear vistas de agenda
```

**Ejemplo:**
```
@dental-scheduler Implementa la lógica para evitar solapamiento de turnos considerando buffers
```

---

### 5. 💬 Especialista en Mensajería

**Nombre:** `dental-messenger`
**Skills:** `dental-messaging-hub`, `dental-chat-assistant`, `dental-intent-classifier`

**Uso:**
```
Usar @dental-messenger cuando necesites:
- Configurar integración WhatsApp/Telegram
- Crear flujos conversacionales
- Implementar clasificación de intenciones
- Diseñar inbox de mensajes
- Automatizar respuestas
```

**Ejemplo:**
```
@dental-messenger Crea un flujo conversacional para pacientes que quieren cancelar turnos
```

---

### 6. 🔒 Especialista en Seguridad

**Nombre:** `dental-security`
**Skill principal:** `dental-security-audit`

**Uso:**
```
Usar @dental-security cuando necesites:
- Definir roles y permisos
- Implementar auditoría
- Configurar RBAC
- Revisar seguridad de endpoints
- Crear políticas de acceso
```

**Ejemplo:**
```
@dental-security Define los permisos para que solo los admin puedan eliminar pagos
```

---

### 7. 🤖 Especialista en IA/Chatbot

**Nombre:** `dental-ai`
**Skills:** `dental-intent-classifier`, `dental-chat-assistant`

**Uso:**
```
Usar @dental-ai cuando necesites:
- Entrenar modelos de clasificación
- Mejorar el bot conversacional
- Implementar NLP
- Crear respuestas automáticas
- Optimizar flujos de IA
```

**Ejemplo:**
```
@dental-ai Mejora el clasificador de intenciones para detectar mejor las urgencias
```

---

### 8. 🚀 DevOps/Deploy

**Nombre:** `dental-devops`
**Skill:** Conocimiento de infraestructura

**Uso:**
```
Usar @dental-devops cuando necesites:
- Configurar Docker
- Deployar en producción
- Configurar CI/CD
- Escalar servicios
- Monitorear el sistema
```

**Ejemplo:**
```
@dental-devops Configura Docker Compose para producción con PostgreSQL y Redis
```

---

## Uso Combinado

Los agentes pueden trabajar juntos:

```
@dental-architect Diseña el módulo de presupuestos
@dental-designer Crea la interfaz para crear presupuestos
@dental-backend Implementa la API de presupuestos con CRUD completo
@dental-security Define permisos para que solo profesionales puedan crear presupuestos
```

---

## Comandos Rápidos

### Crear un módulo completo:
```
@dental-architect + @dental-designer + @dental-backend 
Necesito el módulo completo de [NOMBRE_DEL_MODULO]
```

### Agregar funcionalidad al bot:
```
@dental-messenger + @dental-ai
Agrega la funcionalidad de [DESCRIPCION] al bot conversacional
```

### Implementar seguridad:
```
@dental-security
Audita y aplica seguridad al módulo de [NOMBRE]
```

---

## Convenciones

1. **Siempre menciona el agente al inicio** del mensaje
2. **Sé específico** en lo que necesitas
3. **Proporciona contexto** del negocio cuando sea relevante
4. **Puedes pedir múltiples cosas** al mismo agente
5. **Los agentes pueden pedir ayuda** a otros agentes automáticamente

---

## Ejemplos Avanzados

### Crear un módulo de estadísticas:
```
@dental-architect 
Diseña un módulo de estadísticas operativas que muestre:
- Turnos por día/semana/mes
- Ingresos proyectados
- Tasa de cancelaciones
- Profesionales más solicitados
- Tratamientos más comunes

@dental-designer
Crea el dashboard con gráficos y filtros por fecha

@dental-backend
Implementa los endpoints para calcular estas métricas desde la base de datos

@dental-security
Asegúrate de que solo admins y recepción puedan ver estas estadísticas
```

### Mejorar el bot con IA:
```
@dental-ai
Entrena un clasificador mejorado que detecte:
- Urgencias dentales
- Pacientes nuevos vs recurrentes
- Intención de reprogramar
- Consultas sobre precios

@dental-messenger
Integra este clasificador en el flujo conversacional y crea respuestas automáticas para cada caso
```

---

## Notas Importantes

- **Los agentes son especialistas:** Cada uno domina su área
- **Pueden colaborar:** Un agente puede invocar a otro cuando es necesario
- **Mantienen contexto:** Recuerdan conversaciones anteriores
- **Siguen las skills:** Cada agente aplica las reglas de su skill correspondiente
- **Priorizan calidad:** Buscan soluciones profesionales, no hacks rápidos

---

## Lista de Skills Disponibles

1. `dental-product-architect` - Arquitectura de producto
2. `dental-react-ui` - Interfaces React
3. `dental-admin-crud` - CRUDs administrativos
4. `dental-scheduling` - Agenda y turnos
5. `dental-messaging-hub` - Mensajería omnicanal
6. `dental-security-audit` - Seguridad y auditoría
7. `dental-intent-classifier` - Clasificación de intenciones
8. `dental-chat-assistant` - Asistente conversacional

---

**¿Listo para empezar?** Menciona un agente y comienza a construir AgentBot.
