from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    
    # Database Settings
    POSTGRES_USER: str = "admin"
    POSTGRES_PASSWORD: str = "secret"
    POSTGRES_DB: str = "solicitudes_db"
    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: int = 5432

    @property
    def database_url(self) -> str:
        """Constructs the database URL from settings."""
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    model_config = ConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

# Instantiate settings to be used across the application
settings = Settings()
