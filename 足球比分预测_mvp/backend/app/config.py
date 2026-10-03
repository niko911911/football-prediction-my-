from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/app -> backend -> 项目根
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent.parent


class Settings(BaseSettings):
    port: int = 8000
    use_mock_data: bool = True
    database_url: str = "sqlite:///./app.db"
    cors_origins: str = "http://localhost:8000"

    model_config = SettingsConfigDict(
        env_file=[str(BASE_DIR / ".env"), str(PROJECT_ROOT / ".env")],
        extra="ignore",
    )


settings = Settings()
