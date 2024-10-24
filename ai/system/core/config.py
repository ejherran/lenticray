from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    QUEUE_NAME: str
    BASE_PATH: str

    SEED: int

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()