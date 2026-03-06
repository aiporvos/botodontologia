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
from app.utils.classify import classify_reason

# --- PROMPT DEL SISTEMA ---
SYSTEM_PROMPT = """# Rol e Identidad
Eres **DentiBot**, el asistente inteligente de **Dental Studio Pro**. 
Tu objetivo es ayudar a los pacientes de forma profesional, amigable y eficiente.

# Capacidades
- Gestión de Turnos (Agendar, cancelar, consultar)
- Información de Precios y Tratamientos
- Gestión de Pacientes (Contactos)
- Envío de correos electrónicos
- Consultas legales básicas odontológicas (ej. consentimientos)

# Límites Temáticos
- Solo respondes temas odontológicos y de gestión de la clínica.
- Si te preguntan algo fuera de lugar (política, fútbol, etc.), di amablemente que eres un asistente dental.

# Reglas de Oro
1. **SIEMPRE** consulta la base de datos antes de responder sobre precios o turnos.
2. Si un paciente quiere un turno, verifica si ya existe como contacto por su teléfono.
3. El tono debe ser cálido pero profesional.
4. Si falta información (ej. fecha para un turno), pídela con amabilidad.

# Calendario / Turnos
- La fecha y hora actual es: {now}
- Los turnos duran 30 minutos por defecto.
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

def manage_contacts(action: str, phone: str, name: str = None, email: str = None, obra_social: str = None) -> str:
    """Gestiona la información de los pacientes (Buscar, Crear, Actualizar)."""
    db = SessionLocal()
    try:
        if action == "search":
            p = db.query(Patient).filter(Patient.phone.contains(phone)).first()
            if p: return f"Paciente encontrado: {p.first_name} {p.last_name}, Obra Social: {p.obra_social}, Email: {p.email}"
            return "No encontré al paciente."
        
        elif action == "create":
            first = name.split()[0] if name else "Paciente"
            last = " ".join(name.split()[1:]) if name and " " in name else "Nuevo"
            p = Patient(first_name=first, last_name=last, phone=phone, email=email, obra_social=obra_social)
            db.add(p)
            db.commit()
            return f"Paciente {name} creado con éxito."
            
        return "Acción no reconocida."
    finally:
        db.close()

def list_appointments(phone: str) -> str:
    """Lista los turnos confirmados de un paciente por su teléfono."""
    db = SessionLocal()
    try:
        p = db.query(Patient).filter(Patient.phone.contains(phone)).first()
        if not p: return "No encontré un paciente con ese teléfono."
        
        appts = db.query(Appointment).filter(
            Appointment.patient_id == p.id,
            Appointment.status == "confirmed",
            Appointment.start_at >= datetime.now()
        ).all()
        
        if not appts: return "No tienes turnos próximos."
        
        res = "Tus turnos:\n"
        for a in appts:
            res += f"- {a.start_at.strftime('%d/%m a las %H:%M')} (Motivo: {a.reason})\n"
        return res
    finally:
        db.close()

def book_appointment(phone: str, date_iso: str, reason: str) -> str:
    """Reserva un turno para un paciente. La fecha debe estar en formato ISO (YYYY-MM-DDTHH:MM:SS)."""
    db = SessionLocal()
    try:
        p = db.query(Patient).filter(Patient.phone.contains(phone)).first()
        if not p: return "Primero necesito registrar tus datos. ¿Me podrías dar tu nombre completo?"
        
        dt = datetime.fromisoformat(date_iso)
        
        # Verificar superposición básica
        overlap = db.query(Appointment).filter(
            Appointment.start_at == dt,
            Appointment.status == "confirmed"
        ).first()
        if overlap:
            return "Lo siento, ese horario ya está ocupado. ¿Probamos otro?"

        appt = Appointment(
            patient_id=p.id,
            professional_id=1, # Default
            start_at=dt,
            end_at=dt + timedelta(minutes=30),
            reason=reason,
            category=classify_reason(reason),
            status="confirmed",
            channel="whatsapp"
        )
        db.add(appt)
        db.commit()
        return f"¡Listo! Turno agendado para el {dt.strftime('%d/%m a las %H:%M')}. ¡Te esperamos!"
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
    StructuredTool.from_function(func=list_appointments, name="ListarTurnos", description="Busca los turnos futuros de un paciente"),
    StructuredTool.from_function(func=book_appointment, name="AgendarTurno", description="Crea una nueva cita dental en el sistema"),
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
