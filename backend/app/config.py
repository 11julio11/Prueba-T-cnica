from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, model_validator


class Settings(BaseSettings):
    # Database
    database_url: str | None = Field(default=None)
    postgres_user: str | None = None
    postgres_password: str | None = None
    postgres_host: str | None = None
    postgres_db: str | None = None
    db_pool_size: int = 5
    db_max_overflow: int = 10

    # Application
    app_name: str = "Requests Management"
    app_version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @model_validator(mode="after")
    def assemble_db_url(self) -> "Settings":
        if not self.database_url:
            if self.postgres_user and self.postgres_password and self.postgres_host and self.postgres_db:
                self.database_url = f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}/{self.postgres_db}"
            else:
                raise ValueError("Either database_url or postgres_* variables must be provided")
        return self


settings = Settings()
