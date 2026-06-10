import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import model_validator, ConfigDict


class Settings(BaseSettings):
    # Bot
    telegram_bot_token: str = ""
    bot_secret: str = ""
    openai_api_key: str = ""

    # Database
    db_host: str = "postgres"
    db_port: int = 5432
    db_user: str = "clinic"
    db_password: str = "clinicpass"
    db_name: str = "clinic"
    database_url: Optional[str] = None

    # Cal.com
    calcom_url: str = "https://odontologia.aiporvos.com"
    calcom_api_key: str = ""

    # Evolution API (WhatsApp)
    evolution_url: str = "http://localhost:8080"
    evolution_api_key: str = ""
    evolution_instance_name: str = "clinic"
    evolution_instance_token: str = ""

    # App
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    debug: bool = True

    # Recordatorios
    reminder_hours: int = 24
    admin_notification_numbers: str = ""  # Ejemplo: "549111234567,549111234568"
    public_url: str = "http://localhost:8000"

    # Admin
    admin_username: str = "admin"
    admin_password: str = "admin123"

    @model_validator(mode='before')
    @classmethod
    def check_legacy_env_vars(cls, data: any) -> any:
        if not isinstance(data, dict):
            try:
                data = dict(data)
            except:
                data = {}

        # Mapeo de variables de entorno alternativas
        db_url = data.get("database_url") or os.environ.get("DATABASE_URL")
        if db_url:
            data["database_url"] = db_url

        evo_url = data.get("evolution_url") or os.environ.get("EVOLUTION_URL") or os.environ.get("EVOLUTION_API_URL")
        if evo_url:
            data["evolution_url"] = evo_url

        evo_inst = data.get("evolution_instance_name") or os.environ.get("EVOLUTION_INSTANCE_NAME") or os.environ.get("EVOLUTION_INSTANCE_ID")
        if evo_inst:
            data["evolution_instance_name"] = evo_inst

        return data

    @model_validator(mode='after')
    def set_default_database_url(self) -> 'Settings':
        if not self.database_url:
            self.database_url = f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
        return self

    model_config = ConfigDict(env_file=".env", extra="allow")


settings = Settings()

