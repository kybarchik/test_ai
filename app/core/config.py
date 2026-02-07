from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    database_url: str
    secret_key: str
    environment: str

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)


settings = Settings()
