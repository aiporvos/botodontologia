# AgentBot - Sistema Odontológico Profesional

Sistema de gestión odontológica moderno, escalable y listo para producción.

## 🏗️ Arquitectura

```
agentbot/
├── backend/      # FastAPI Backend
├── frontend/     # React Frontend
├── bot/          # Telegram/WhatsApp Bot (LangChain)
├── database/     # PostgreSQL + Alembic
└── docker-compose.yml  # Producción completa
```

## 🚀 Inicio Rápido

### Con Docker (Recomendado)

```bash
# 1. Clonar y entrar
cd agentbot

# 2. Copiar variables de entorno
cp .env.example .env

# 3. Iniciar servicios
docker-compose up -d

# 4. Acceder
# Frontend: http://localhost:3000
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

### Desarrollo Local

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm start
```

## 📚 Documentación

- [Skills](./skills/) - Guías especializadas
- [Backend](./backend/) - API FastAPI
- [Frontend](./frontend/) - React SPA
- [Bot](./bot/) - Asistente conversacional

## 🔧 Variables de Entorno

| Variable | Descripción | Default |
|----------|-------------|---------|
| DATABASE_URL | URL de PostgreSQL | postgresql://... |
| SECRET_KEY | Clave JWT | change-me |
| ADMIN_PASSWORD | Password admin | admin123 |
| CORS_ORIGINS | Orígenes permitidos | localhost |
| TELEGRAM_BOT_TOKEN | Token bot Telegram | - |
| OPENAI_API_KEY | API Key OpenAI | - |

## 🛠️ Tecnologías

- **Backend:** FastAPI, SQLAlchemy, PostgreSQL, JWT
- **Frontend:** React, TypeScript, Tailwind CSS
- **Bot:** LangChain, OpenAI, python-telegram-bot
- **DevOps:** Docker, Docker Compose

## 📝 Licencia

MIT
