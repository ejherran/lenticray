from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Lenticray API"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    SQLALCHEMY_DATABASE_URI: str
    USER_DATA: str

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
