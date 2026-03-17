"""
AI Agent para Dental Studio Pro
Procesa mensajes de pacientes usando LangChain y OpenAI
"""

import json
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.tools import tool

from config import settings
from app.database import SessionLocal
from app.models import (
    Patient,
    Professional,
    Availability,
    Appointment,
    TreatmentPrice,
    ChatSession,
)
from app.services.evolution import evolution_service
from app.services.email import email_service
from app.utils.classify import classify_reason, get_treatment_details


# --- PROMPT DEL SISTEMA ---
SYSTEM_PROMPT = """# Rol e Identidad
Eres **DentiBot**, el asistente inteligente de **Dental Studio Pro**.
Tu objetivo es ayudar a los pacientes de forma profesional, cálida y eficiente.

# Instructivo Crítico para Agendar, Consultar, Cancelar o Reprogramar Turnos

## 1. Agendar un turno nuevo:
1. **Identificar Necesidad:** Pregunta el motivo (¿Limpieza? ¿Dolor? ¿Brackets?).
2. **Consultar Agenda Temprana:** Usa `check_availability` enviándole el motivo.
3. **Ofrecer Opciones:** Dale las opciones al paciente.
4. **Recolección de Datos:** Pide Nombre, DNI, OS y Teléfono.
5. **Agendar:** Usa `book_appointment` con la fecha en formato ISO (YYYY-MM-DDTHH:MM:SS).

## 2. Consultar mis turnos:
Si el paciente te pide ver sus turnos, pídele su número de teléfono y usa la herramienta `get_my_appointments`. Esta te devolverá los IDs de sus próximos turnos.

## 3. Cancelar un turno:
1. Usa `get_my_appointments` para buscar el ID del turno si el paciente no lo brindó.
2. Usa `cancel_appointment(appt_id)` para cancelarlo. Confírmaselo al paciente.

## 4. Reprogramar un turno:
1. Usa `get_my_appointments` para obtener el ID si es necesario.
2. Usa `check_availability` para ver los nuevos horarios disponibles.
3. Usa la herramienta `reschedule_appointment` con el ID del turno y la nueva fecha en formato ISO (YYYY-MM-DDTHH:MM:SS).

# Asignaciones Internas (Para tu contexto)
- **Dr. Silvestro:** Extracciones, Implantes, Prótesis (30 min), Limpiezas (15 min).
- **Dra. Murad:** Ortodoncia (30 min), Conductos / Endodoncia (60 min).
- **Cualquiera:** Consulta inicial 1ra/2da vez (15 min).

# Reglas de ORO
1. NO INVENTES HORARIOS. Solo ofrece los que devuelva `check_availability`.
2. Ocasionalmente, recuérdale al paciente que el sistema es un bot y que los mensajes de texto son preferibles.
3. Sé profesional y resolutivo. Si hay urgencia, derívalo de inmediato.
4. La fecha y hora actual del servidor es: {now}
5. IMPORTANTE: En `book_appointment` y `reschedule_appointment`, debes usar la fecha EXACTA en formato ISO (YYYY-MM-DDTHH:MM:SS).
"""


# --- HERRAMIENTAS (TOOLS) ---


@tool
def search_prices(query: str) -> str:
    """Busca precios de tratamientos en el catálogo dental."""
    db = SessionLocal()
    try:
        prices = (
            db.query(TreatmentPrice)
            .filter(
                or_(
                    TreatmentPrice.name.ilike(f"%{query}%"),
                    TreatmentPrice.code.ilike(f"%{query}%"),
                    TreatmentPrice.description.ilike(f"%{query}%"),
                ),
                TreatmentPrice.is_active == True,
            )
            .all()
        )
        if not prices:
            return (
                "No encontré precios para ese tratamiento. ¿Podrías ser más específico?"
            )

        res = "Catálogo de Precios:\n"
        for p in prices:
            res += f"- {p.name} ({p.code}): ${p.price}\n"
        return res
    finally:
        db.close()


@tool
def manage_contacts(
    action: str,
    phone: str,
    name: str = None,
    dni: str = None,
    email: str = None,
    obra_social: str = None,
) -> str:
    """Gestiona la info de pacientes en la BD. Acciones validas: search, create."""
    db = SessionLocal()
    try:
        if action == "search":
            p = db.query(Patient).filter(Patient.phone.contains(phone)).first()
            if p:
                return f"Paciente encontrado: {p.first_name} {p.last_name}, DNI: {p.dni}, OS: {p.obra_social}"
            return "No encontré al paciente."

        elif action == "create":
            first = name.split()[0] if name else "Paciente"
            last = " ".join(name.split()[1:]) if name and " " in name else "Nuevo"
            p = Patient(
                first_name=first,
                last_name=last,
                phone=phone,
                dni=dni,
                email=email,
                obra_social=obra_social,
            )
            db.add(p)
            db.commit()
            return f"Paciente {name} guardado en el sistema."

        return "Acción no reconocida."
    finally:
        db.close()


@tool
def check_availability(reason: str) -> str:
    """Busca días y horarios disponibles según el motivo de consulta ingresado usando el sistema real."""
    db = SessionLocal()
    try:
        from app.services.availability import AvailabilityService

        availability_service = AvailabilityService(db)
        result = availability_service.find_available_slots(
            reason, days_ahead=14, max_options=6
        )

        if not result["success"]:
            return f"Lo siento, no pude encontrar disponibilidad: {result.get('error', 'Error desconocido')}"

        professional = result["professional"]
        treatment = result["treatment"]
        slots = result["slots"]

        if not slots:
            return (
                f"Lo siento, no hay horarios disponibles para {reason} en los próximos días. "
                f"Te sugiero llamar al consultorio para coordinar."
            )

        res = f"📅 *Consulta para: {reason}*\n"
        res += f"⏱️ Duración: {treatment['duration']} minutos\n"
        res += f"👨‍⚕️ Profesional asignado: {professional['name']} ({professional['specialty']})\n\n"
        res += "*Horarios disponibles:*\n"

        for i, slot in enumerate(slots, 1):
            res += f"{i}. {slot['date']} a las {slot['time']}\n"

        res += "\n¿Cuál opción prefieres? Indícame el número (1, 2, 3...)"

        return res
    finally:
        db.close()


@tool
def book_appointment(
    phone: str, name: str, dni: str, obra_social: str, date_iso: str, reason: str
) -> str:
    """Crea o actualiza al paciente y agenda su turno final en la base de datos.

    Args:
        phone: Número de teléfono del paciente
        name: Nombre completo del paciente
        dni: DNI del paciente
        obra_social: Obra social o "Particular" si no tiene
        date_iso: Fecha y hora en formato ISO (YYYY-MM-DDTHH:MM:SS)
        reason: Motivo de la consulta

    Returns:
        Mensaje de confirmación o error
    """
    db = SessionLocal()
    try:
        # Validar parámetros
        if not phone or not name or not date_iso:
            return "Error: Faltan datos obligatorios (teléfono, nombre o fecha)."

        # Limpiar y validar teléfono
        phone_clean = phone.replace(" ", "").replace("-", "").replace("+", "")
        if not phone_clean:
            return "Error: Teléfono inválido."

        # Buscar o crear paciente
        p = db.query(Patient).filter(Patient.phone.contains(phone_clean)).first()

        # Separar nombre y apellido
        name_parts = name.strip().split()
        first = name_parts[0] if name_parts else "Paciente"
        last = " ".join(name_parts[1:]) if len(name_parts) > 1 else "Nuevo"

        obra_social_clean = obra_social if obra_social else "Particular"
        dni_clean = dni if dni else None

        if not p:
            p = Patient(
                first_name=first,
                last_name=last,
                phone=phone_clean,
                dni=dni_clean,
                obra_social=obra_social_clean,
            )
            db.add(p)
            db.commit()
            db.refresh(p)
            print(f"✅ Nuevo paciente creado: {first} {last}")
        else:
            # Actualizamos datos faltantes
            if dni_clean and not p.dni:
                p.dni = dni_clean
            if obra_social_clean and not p.obra_social:
                p.obra_social = obra_social_clean
            db.commit()
            db.refresh(p)
            print(f"✅ Paciente existente actualizado: {p.first_name} {p.last_name}")

        # Clasificar el motivo y obtener detalles
        cat = classify_reason(reason)
        details = get_treatment_details(cat)
        duration = details.get("duration", 30)
        doc_name = details.get("doctor_name", "Cualquiera")

        # Buscar profesional
        prof = None
        if doc_name != "Cualquiera":
            prof = (
                db.query(Professional)
                .filter(Professional.full_name.contains(doc_name.split()[-1]))
                .first()
            )
        if not prof:
            prof = db.query(Professional).first()

        # Parsear fecha
        try:
            # Intentar parsear la fecha ISO
            dt = datetime.fromisoformat(
                date_iso.replace("Z", "+00:00").replace("+00:00", "")
            )
        except ValueError as e:
            return f"Error: Formato de fecha inválido. Usa el formato: YYYY-MM-DDTHH:MM:SS. Error: {str(e)}"

        # Crear el turno
        appt = Appointment(
            patient_id=p.id,
            professional_id=prof.id if prof else 1,
            start_at=dt,
            end_at=dt + timedelta(minutes=duration),
            reason=reason,
            category=cat,
            status="confirmed",
            channel="telegram",
        )
        db.add(appt)
        db.commit()

        print(f"✅ Turno creado: {dt.strftime('%d/%m/%Y %H:%M')} - {first} {last}")

        return f"✅ ¡Turno agendado exitosamente!\n\n📅 Fecha: {dt.strftime('%d/%m/%Y')}\n🕐 Hora: {dt.strftime('%H:%M')}\n👤 Paciente: {first} {last}\n👨‍⚕️ Profesional: {prof.full_name if prof else 'General'}\n📝 Motivo: {reason}\n\nTe esperamos en Dental Studio Pro. ¡Gracias por confiar en nosotros!"
    except Exception as e:
        import traceback

        error_msg = f"Error al agendar: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return f"Error al agendar el turno. Por favor, intenta nuevamente o contacta al consultorio. Error: {str(e)}"
    finally:
        db.close()


@tool
async def send_mail_tool(to: str, subject: str, body: str) -> str:
    """Envía un correo electrónico al paciente."""
    success = await email_service.send_email(to, subject, body)
    return "Correo enviado con éxito." if success else "Error al enviar el correo."


@tool
def get_my_appointments(phone: str) -> str:
    """Obtiene los turnos futuros de un paciente dado su número de teléfono."""
    db = SessionLocal()
    try:
        phone_clean = phone.replace(" ", "").replace("-", "").replace("+", "")
        p = db.query(Patient).filter(Patient.phone.contains(phone_clean)).first()
        if not p:
            return "No encontré un paciente con ese número de teléfono."
        
        now = datetime.now()
        appts = db.query(Appointment).filter(
            Appointment.patient_id == p.id,
            Appointment.start_at >= now,
            Appointment.status.in_(["confirmed", "pending"])
        ).order_by(Appointment.start_at).all()
        
        if not appts:
            return f"El paciente {p.first_name} {p.last_name} no tiene turnos próximos agendados."
            
        res = f"Turnos próximos para {p.first_name} {p.last_name}:\n"
        for a in appts:
            doc = a.professional.full_name if a.professional else "General"
            res += f"- ID {a.id}: {a.start_at.strftime('%d/%m/%Y %H:%M')} con {doc} ({a.reason})\n"
        return res
    finally:
        db.close()


@tool
def cancel_appointment(appt_id: int) -> str:
    """Cancela un turno existente dado su ID."""
    db = SessionLocal()
    try:
        a = db.query(Appointment).filter(Appointment.id == appt_id).first()
        if not a:
            return f"No encontré un turno con el ID {appt_id}."
            
        a.status = "cancelled"
        db.commit()
        return f"El turno ID {appt_id} para {a.start_at.strftime('%d/%m/%Y %H:%M')} ha sido CANCELADO exitosamente."
    finally:
        db.close()

@tool
def reschedule_appointment(appt_id: int, new_date_iso: str) -> str:
    """Reprograma un turno existente a una nueva fecha y hora. Usa check_availability primero para ver opciones!"""
    db = SessionLocal()
    try:
        a = db.query(Appointment).filter(Appointment.id == appt_id).first()
        if not a:
            return f"No encontré un turno con el ID {appt_id}."
            
        try:
            dt = datetime.fromisoformat(new_date_iso.replace("Z", "+00:00").replace("+00:00", ""))
        except ValueError as e:
            return f"Error: Formato de fecha inválido. Usa: YYYY-MM-DDTHH:MM:SS."
            
        # Asumiendo misma duración anterior
        duration = int((a.end_at - a.start_at).total_seconds() / 60) if a.end_at and a.start_at else 30
        
        a.start_at = dt
        a.end_at = dt + timedelta(minutes=duration)
        db.commit()
        return f"El turno ID {appt_id} ha sido REPROGRAMADO exitosamente para el {dt.strftime('%d/%m/%Y %H:%M')}."
    finally:
        db.close()


# Lista de herramientas disponibles
TOOLS = [
    search_prices,
    manage_contacts,
    check_availability,
    book_appointment,
    send_mail_tool,
    get_my_appointments,
    cancel_appointment,
    reschedule_appointment,
]


# --- EL AGENTE ---


class AIAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini", temperature=0.3, api_key=settings.openai_api_key
        )
        self.llm_with_tools = self.llm.bind_tools(TOOLS)
        self._memories = {}

    def get_memory(self, chat_id: str) -> List:
        """Obtiene el historial de conversación desde la base de datos"""
        db = SessionLocal()
        try:
            session = db.query(ChatSession).filter(ChatSession.chat_id == chat_id).first()
            if session and session.payload:
                memory = json.loads(session.payload)
                return memory[-10:] # Últimos 10 mensajes
            return []
        finally:
            db.close()

    def save_to_memory(self, chat_id: str, role: str, content: str):
        """Guarda un mensaje en la base de datos"""
        db = SessionLocal()
        try:
            session = db.query(ChatSession).filter(ChatSession.chat_id == chat_id).first()
            if not session:
                session = ChatSession(
                    chat_id=chat_id,
                    channel="whatsapp" if "@c.us" in chat_id else "telegram",
                    step="conversation",
                    payload="[]"
                )
                db.add(session)
            
            memory = json.loads(session.payload)
            memory.append({"role": role, "content": content})
            # Mantener límite razonable
            session.payload = json.dumps(memory[-20:])
            session.updated_at = datetime.now()
            db.commit()
        except Exception as e:
            print(f"Error saving to memory: {e}")
            db.rollback()
        finally:
            db.close()

    async def ask(self, chat_id: str, text: str) -> str:
        """Procesa un mensaje y retorna la respuesta"""
        try:
            # Obtener historial
            memory = self.get_memory(chat_id)

            # Construir mensajes
            messages = [
                SystemMessage(
                    content=SYSTEM_PROMPT.format(
                        now=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    )
                )
            ]

            # Agregar historial
            for msg in memory:
                if msg["role"] == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    messages.append(AIMessage(content=msg["content"]))

            # Agregar mensaje actual
            messages.append(HumanMessage(content=text))

            # Crear prompt
            prompt = ChatPromptTemplate.from_messages(messages)

            # Ejecutar
            chain = prompt | self.llm_with_tools
            response = await chain.ainvoke({})

            # Si hay tool calls, ejecutarlas
            if hasattr(response, "tool_calls") and response.tool_calls:
                tool_results = []
                for tool_call in response.tool_calls:
                    tool_name = tool_call["name"]
                    tool_args = tool_call["args"]

                    # Encontrar la herramienta
                    for tool in TOOLS:
                        if tool.name == tool_name:
                            try:
                                result = tool.invoke(tool_args)
                                tool_results.append(f"{tool_name}: {result}")
                            except Exception as e:
                                tool_results.append(f"{tool_name}: Error - {str(e)}")
                            break

                # Segunda llamada con los resultados
                tool_msg = "\n".join(tool_results)
                messages.append(
                    AIMessage(content=f"Resultados de herramientas: {tool_msg}")
                )
                prompt2 = ChatPromptTemplate.from_messages(messages)
                chain2 = prompt2 | self.llm
                response = await chain2.ainvoke({})

            output = response.content

            # Guardar en memoria
            self.save_to_memory(chat_id, "user", text)
            self.save_to_memory(chat_id, "assistant", output)

            return output

        except Exception as e:
            print(f"Agent Error: {e}")
            import traceback

            traceback.print_exc()
            return "Lo siento, tuve un pequeño problema procesando eso. ¿Podrías repetirlo?"


# Instancia global
ai_agent = AIAgent()
