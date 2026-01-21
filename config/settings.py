from pydantic_settings import BaseSettings
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "Raymond Analysis"
    VERSION: str = "1.0.0"
    
    DATABASE_URL: str = f"sqlite:///{BASE_DIR}/data/raymond_analysis.db"
    
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_URL: str = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
    
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    
    HOST: str = "0.0.0.0"
    PORT: int = 8001
    
    DATA_RETENTION_DAYS: int = 30
    
    class Config:
        env_file = BASE_DIR / ".env"

settings = Settings()
