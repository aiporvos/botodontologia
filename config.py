import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Bot
    telegram_bot_token: str = ""
    bot_secret: str = ""

    # Database
    db_host: str = "postgres"
    db_port: int = 5432
    db_user: str = "clinic"
    db_password: str = "clinicpass"
    db_name: str = "clinic"

    @property
    def database_url(self) -> str:
        if hasattr(self, "_database_url") and self._database_url:
            return self._database_url
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

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

    # Admin
    admin_username: str = "admin"
    admin_password: str = "admin123"

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
