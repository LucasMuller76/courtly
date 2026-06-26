from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 24
    ENVIRONMENT: str = "development"

    WHATSAPP_API_URL: str = ""
    WHATSAPP_API_KEY: str = ""
    RESEND_API_KEY: str = ""

    @field_validator("DATABASE_URL")
    @classmethod
    def fix_postgres_url(cls, v: str) -> str:
        # Railway usa postgres:// mas SQLAlchemy precisa de postgresql://
        if v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql://", 1)
        return v

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()