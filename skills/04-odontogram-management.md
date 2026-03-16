# Skill: Gestión del Odontograma

## Descripción
Sistema visual de odontograma digital para registrar tratamientos por diente y superficie.

## Estructura del Odontograma

### Dentición Permanente (Adultos)
**Arcada Superior:**
- Cuadrante 1 (Derecha): 18, 17, 16, 15, 14, 13, 12, 11
- Cuadrante 2 (Izquierda): 21, 22, 23, 24, 25, 26, 27, 28

**Arcada Inferior:**
- Cuadrante 4 (Derecha): 48, 47, 46, 45, 44, 43, 42, 41
- Cuadrante 3 (Izquierda): 31, 32, 33, 34, 35, 36, 37, 38

### Dentición Temporal (Niños)
**Arcada Superior:**
- Cuadrante 5: 55, 54, 53, 52, 51
- Cuadrante 6: 61, 62, 63, 64, 65

**Arcada Inferior:**
- Cuadrante 8: 85, 84, 83, 82, 81
- Cuadrante 7: 71, 72, 73, 74, 75

## Superficies por diente
Cada diente tiene 5 superficies:
- **Top/Vestibular** (V): Cara externa superior
- **Bottom/Palatino o Lingual** (P/L): Cara interna
- **Left/Mesial** (M): Cara hacia el centro
- **Right/Distal** (D): Cara hacia afuera
- **Center/Oclusal** (O): Parte superior masticatoria

## Tratamientos disponibles

### Por superficie:
- **Caries Azul**: Caries existente ya tratada
- **Caries Rojo**: Caries a tratar
- **Obturación Azul**: Empaste existente
- **Obturación Rojo**: Empaste a realizar
- **Conducto Azul/Rojo**: Tratamiento de conducto

### Diente completo:
- **Extracción**: X azul
- **Ausente**: X rojo
- **Corona Azul/Rojo**: Corona existente o a colocar
- **Implante**: IM
- **Ortodoncia**: Símbolo =

## Flujo de trabajo
1. Seleccionar paciente
2. Seleccionar herramienta de la barra
3. Click en superficie específica o diente completo
4. Guardar cambios
5. Visualizar historial de tratamientos

## API Endpoints
- GET /api/patients/{id}/odontogram - Obtener odontograma
- POST /api/patients/{id}/odontogram - Guardar odontograma
- GET /api/patients/{id}/treatments - Historial de tratamientos

## Estructura de datos
```json
{
  "teeth": {
    "11": {
      "top": "caries-rojo",
      "center": "obturacion-azul",
      "_whole": "extraccion"
    },
    "21": {
      "_whole": "implante"
    }
  }
}
```

## Consideraciones
- Cada paciente tiene su propio odontograma
- Se guarda historial de cambios
- Visualización diferenciada adultos/niños
- Compatible con impresión/exportación
