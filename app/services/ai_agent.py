import json
import asyncio
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import StructuredTool
from langchain.memory import ConversationBufferWindowMemory
from sqlalchemy.orm import Session
from sqlalchemy import or_

from config import settings
from app.database import SessionLocal
from app.models import Patient, Professional, Availability, Appointment, TreatmentPrice, ChatSession
from app.services.evolution import evolution_service
from app.services.email import email_service
from app.services.cal_com import calcom_service
from app.utils.classify import classify_reason, get_treatment_details

# --- PROMPT DEL SISTEMA ---
SYSTEM_PROMPT = """# Rol e Identidad
Eres **DentiBot**, el asistente inteligente de **Dental Studio Pro**. 
Tu objetivo es ayudar a los pacientes de forma profesional, cálida y eficiente.

# Instructivo Crítico para Agendar Turnos (¡Sigue ESTE ORDEN siempre!)
1. **Identificar Necesidad:** Si el paciente quiere un turno pero NO te dice para qué, pregúntale el motivo (¿Limpieza? ¿Dolor? ¿Brackets?). Si dice que es su primera vez recomiéndale una consulta general.
2. **Consultar Agenda Temprana:** Una vez que sepas el motivo, USA LA HERRAMIENTA `ConsultarDisponibilidad` enviándole el motivo. Esta herramienta te dirá las opciones de fecha, doctor y duración.
3. **Ofrecer Opciones:** Dile al paciente los horarios que arrojó la herramienta para su tratamiento y pregúntale cuál prefiere.
4. **Recolección de Datos (Obligatorios):** Cuando el paciente elija el horario, dile: "Para agendar tu turno necesito registrarte en el sistema. Por favor, pásame estos 4 datos: Nombre y Apellido, DNI, Obra Social (o Particular si no tienes) y Teléfono."
5. **Llamado a Agendar:** Una vez tengas su DNI, Nombre y Teléfono, USA LA HERRAMIENTA `AgendarTurno` para guardarlo en la base de datos.

# Asignaciones Internas (Para tu contexto)
- **Dr. Silvestro:** Extracciones, Implantes, Prótesis (30 min), Limpiezas (15 min).
- **Dra. Murad:** Ortodoncia (30 min), Conductos / Endodoncia (60 min).
- **Cualquiera:** Consulta inicial 1ra/2da vez (15 min).

# Reglas de ORO
1. NO INVENTES HORARIOS. Solo ofrece los que devuelva la herramienta `ConsultarDisponibilidad`.
2. Ocasionalmente, recuérdale al paciente que el sistema es un bot y que los mensajes de texto son preferibles.
3. Sé profesional y resolutivo. Si un paciente sufre dolor o pide extracción, asócialo directo a Silvestro o Murad según corresponda en la búsqueda.
4. La fecha y hora actual del servidor es: {now}
"""

# --- HERRAMIENTAS (TOOLS) ---

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def search_prices(query: str) -> str:
    """Busca precios de tratamientos en el catálogo dental."""
    db = SessionLocal()
    try:
        prices = db.query(TreatmentPrice).filter(
            or_(
                TreatmentPrice.name.ilike(f"%{query}%"),
                TreatmentPrice.code.ilike(f"%{query}%"),
                TreatmentPrice.description.ilike(f"%{query}%")
            ),
            TreatmentPrice.is_active == True
        ).all()
        if not prices:
            return "No encontré precios para ese tratamiento. ¿Podrías ser más específico?"
        
        res = "Catálogo de Precios:\n"
        for p in prices:
            res += f"- {p.name} ({p.code}): ${p.price}\n"
        return res
    finally:
        db.close()

def manage_contacts(action: str, phone: str, name: str = None, dni: str = None, email: str = None, obra_social: str = None) -> str:
    """Gestiona la info de pacientes en la BD. Acciones validas: search, create."""
    db = SessionLocal()
    try:
        if action == "search":
            p = db.query(Patient).filter(Patient.phone.contains(phone)).first()
            if p: return f"Paciente encontrado: {p.first_name} {p.last_name}, DNI: {p.dni}, OS: {p.obra_social}"
            return "No encontré al paciente."
        
        elif action == "create":
            first = name.split()[0] if name else "Paciente"
            last = " ".join(name.split()[1:]) if name and " " in name else "Nuevo"
            p = Patient(first_name=first, last_name=last, phone=phone, dni=dni, email=email, obra_social=obra_social)
            db.add(p)
            db.commit()
            return f"Paciente {name} guardado en el sistema."
            
        return "Acción no reconocida."
    finally:
        db.close()

def check_availability(reason: str) -> str:
    """Busca días y horarios disponibles según el motivo de consulta ingresado (asigna experto y duración)."""
    db = SessionLocal()
    try:
        cat = classify_reason(reason)
        details = get_treatment_details(cat)
        duration = details["duration"]
        doctor_name = details["doctor_name"]
        
        prof = None
        if doctor_name != "Cualquiera":
            prof = db.query(Professional).filter(Professional.full_name.contains(doctor_name.split()[-1])).first()
        if not prof:
            prof = db.query(Professional).first() # Default fallback

        # Logica: en un entorno real cruzamos las tablas de Availability y Appointment.
        # Aquí vamos a generar slots virtuales de demostración próximos a la fecha actual para que el Agente pueda usar.
        now = datetime.now()
        base_day = now.replace(hour=10, minute=0, second=0, microsecond=0)
        if now.hour >= 16: base_day += timedelta(days=1)
        if base_day.weekday() > 4: base_day += timedelta(days=7 - base_day.weekday()) # Saltar al lunes

        res = f"Búsqueda para {cat.upper()} (Duración estimada: {duration} mins). Profesional asignado: {prof.full_name if prof else 'Indistinto'}.\n"
        res += "Dile al paciente alguna de estas opciones y pregúntale cuál prefiere:\n"
        
        slots = []
        for d in range(3):
            day = base_day + timedelta(days=d)
            if day.weekday() > 4: continue # Sin fines de semana en demo
            slots.append(f"- Opcion {d*2 + 1}: {day.strftime('%A %d/%m a las %H:%M')}")
            slots.append(f"- Opcion {d*2 + 2}: {(day + timedelta(hours=3)).strftime('%A %d/%m a las %H:%M')}")

        for s in slots[:3]:
            res += f"{s}\n"
            
        return res
    finally:
        db.close()

def book_appointment(phone: str, name: str, dni: str, obra_social: str, date_iso: str, reason: str) -> str:
    """Crea o actualiza al paciente y agenda su turno final en la base de datos."""
    db = SessionLocal()
    try:
        # Guardado / Busqueda de Paciente (Garantizar que tenemos todos los datos)
        p = db.query(Patient).filter(Patient.phone.contains(phone)).first()
        first = name.split()[0] if name else "Paciente"
        last = " ".join(name.split()[1:]) if name and " " in name else "..."
        if not p:
            p = Patient(first_name=first, last_name=last, phone=phone, dni=dni, obra_social=obra_social)
            db.add(p)
            db.commit()
            db.refresh(p)
        else:
            # Actualizamos datos faltantes
            if dni and p.dni != dni: p.dni = dni
            if obra_social and p.obra_social != obra_social: p.obra_social = obra_social
            db.commit()
            db.refresh(p)

        cat = classify_reason(reason)
        details = get_treatment_details(cat)
        duration = details.get("duration", 30)
        doc_name = details.get("doctor_name", "Cualquiera")
        
        prof = None
        if doc_name != "Cualquiera":
            prof = db.query(Professional).filter(Professional.full_name.contains(doc_name.split()[-1])).first()
        if not prof:
            prof = db.query(Professional).first()

        try:
            dt = datetime.fromisoformat(date_iso)
        except ValueError:
            return "Error: Formato de fecha invalido (debe ser ISO). Pidele al modelo de IA corregir la fecha."
        
        appt = Appointment(
            patient_id=p.id,
            professional_id=prof.id if prof else 1,
            start_at=dt,
            end_at=dt + timedelta(minutes=duration),
            reason=reason,
            category=cat,
            status="confirmed",
            channel="whatsapp"
        )
        db.add(appt)
        db.commit()
        return f"ÉXITO: Turno agendado el {dt.strftime('%d/%m a las %H:%M')} para el Dr/Dra {prof.full_name if prof else 'General'}. \nInstrucción a IA: Responde amablemente confirmando estos detalles y agradeciendo al paciente."
    finally:
        db.close()

async def send_mail_tool(to: str, subject: str, body: str) -> str:
    """Envía un correo electrónico al paciente."""
    success = await email_service.send_email(to, subject, body)
    return "Correo enviado con éxito." if success else "Error al enviar el correo."

# DEFINICIÓN DE TOOLS PARA LANGCHAIN
tools = [
    StructuredTool.from_function(func=search_prices, name="ConsultarPrecios", description="Busca precios de tratamientos dentales en el catálogo"),
    StructuredTool.from_function(func=manage_contacts, name="GestionarContactos", description="Busca o crea pacientes en la base de datos"),
    StructuredTool.from_function(func=check_availability, name="ConsultarDisponibilidad", description="DEBES USARLA ANTES DE AGENDAR. Busca horarios disponibles, duraciones y DOCTORES en la clinica enviando el 'motivo' de consulta."),
    StructuredTool.from_function(func=book_appointment, name="AgendarTurno", description="Crea una cita dental en el sistema. Requiere celular, nombre, DNI, OS, fecha ISO y motivo."),
    StructuredTool.from_function(func=send_mail_tool, name="EnviarEmail", description="Envía un correo electrónico profesional")
]

# --- EL AGENTE ---

class AIAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3, openai_api_key=settings.openai_api_key)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT.format(now=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        self.agent = create_openai_functions_agent(self.llm, tools, self.prompt)
        self.executor = AgentExecutor(agent=self.agent, tools=tools, verbose=True)
        self._memories = {}

    def get_memory(self, chat_id: str):
        if chat_id not in self._memories:
            self._memories[chat_id] = ConversationBufferWindowMemory(k=5, return_messages=True, memory_key="chat_history")
        return self._memories[chat_id]

    async def ask(self, chat_id: str, text: str) -> str:
        memory = self.get_memory(chat_id)
        try:
            response = await self.executor.ainvoke({
                "input": text,
                "chat_history": memory.load_memory_variables({})["chat_history"]
            })
            output = response["output"]
            memory.save_context({"input": text}, {"output": output})
            return output
        except Exception as e:
            print(f"Agent Error: {e}")
            return "Lo siento, tuve un pequeño problema procesando eso. ¿Podrías repetirlo?"

ai_agent = AIAgent()
