from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://postgres:postgres@localhost:5432/dentibot"

    # Security
    secret_key: str = "your-secret-key-change-in-production"
    access_token_expire_minutes: int = 30

    # Admin
    admin_username: str = "admin"
    admin_password: str = "admin123"

    # CORS
    cors_origins: str = "http://localhost:3000,http://localhost:5173"

    # Bot Service
    bot_service_url: str = "http://bot:8001"

    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def cors_origins_list(self) -> list:
        return [origin.strip() for origin in self.cors_origins.split(",")]


@lru_cache()
def get_settings() -> Settings:
    return Settings()
