from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables or .env file.
    Centralizes all sensitive and environment-specific configuration.
    """
    APP_NAME: str = "Course Validator MVP"
    MONGO_URI: str = "mongodb://localhost:27017/agentmarket_db" # TODO: change to the actual mongo uri
    OPENAI_API_KEY: Optional[str] = None
    EMBEDDING_PROVIDER: str = "openai"  # Default to OpenAI, can be set to 'deepseek' or others
    OPENAI_DEFAULT_MODEL: str = "gpt-3.5-turbo"  # Default model
    JWT_SECRET_KEY: Optional[str] = None
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Job Market API Settings
    ADZUNA_APP_ID: Optional[str] = None
    ADZUNA_API_KEY: Optional[str] = None
    JOB_SEARCH_COUNTRY: str = "us"  # us, gb, de, au, etc.
    MAX_JOBS_TO_ANALYZE: int = 100
    
    # YouTube API Settings
    YOUTUBE_API_KEY: Optional[str] = None


    model_config = {
        "env_file": ".env",
        "extra": "ignore"
    }

# Global settings instance
settings = Settings()
