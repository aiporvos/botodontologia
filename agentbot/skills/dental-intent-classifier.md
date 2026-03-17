---
name: dental-intent-classifier
description: Detecta automáticamente el tipo de consulta odontológica a partir de mensajes de pacientes y asigna el profesional adecuado.
---

# Dental Intent Classifier

Usa esta skill para clasificar consultas odontológicas automáticamente mediante análisis de intenciones.

## Objetivo

Detectar el tipo de consulta odontológica en mensajes de pacientes y sugerir profesional adecuado.

## Tipos de consulta

- extraccion
- implante
- ortodoncia
- endodoncia/conducto
- caries
- limpieza
- consulta_general
- urgencia

## Reglas de clasificación

### Por keywords

```
extraccion: ["extracción", "muela", "dolor", "arrancar", "sacar", "empuje"]
implante: ["implante", "falta diente", "perdí", "prótesis"]
ortodoncia: ["ortodoncia", "brackets", "frenillos", "alinear", "aparato"]
endodoncia: ["conducto", "endodoncia", "vital", "matar nervio"]
caries: ["caries", "agujero", "empaste", "tapar"]
limpieza: ["limpieza", "sarro", "tártaro", "blanqueamiento"]
consulta_general: ["consulta", "chequeo", "revisión", "primera vez"]
urgencia: ["urgencia", "emergencia", "mucho dolor", "sangrado"]
```

### Asignación de profesional

```
ReglaAsignacion {
  keywords: string[]
  profesional_id: string
  especialidad: string
}
```

- extraccion → Dr. Silvestro
- implante → Dr. Silvestro
- ortodoncia → Dra. Murad
- endodoncia → Dra. Murad
- Default → Primer profesional disponible

## Output esperado

```json
{
  "tipo": "ortodoncia",
  "profesional_sugerido": {
    "id": "uuid",
    "nombre": "Dra. Murad",
    "especialidad": "Ortodoncia"
  },
  "confianza": 0.87,
  "keywords_detectados": ["brackets", "alinear"]
}
```

## Implementación

### Método classify_intent(text: string):

1. Normalizar texto (minúsculas, sin tildes)
2. Buscar coincidencias de keywords
3. Calcular score por categoría
4. Seleccionar categoría con mayor score
5. Asignar profesional según reglas
6. Retornar resultado con confianza

## Consideraciones

- Permitir múltiples keywords
- Score mínimo de confianza: 0.6
- Fallback a consulta_general si no hay coincidencia clara
- Registras clasificación para mejora continua
