from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Base de datos
    database_url: str
    db_pool_size: int = 5
    db_max_overflow: int = 10

    # Aplicación
    app_name: str = "Gestión de Solicitudes"
    app_version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"

    # Servidor
    host: str = "0.0.0.0"
    port: int = 8000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()
