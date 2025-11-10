"""
Pawsonality  Configuration Management
Pydantic Settings를 사용한 환경 변수 관리
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """
    애플리케이션 설정
    .env 파일이나 환경 변수에서 자동으로 로드됩니다.
    """
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    RELOAD: bool = False
    
    # API Configuration
    API__PREFIX: str = "/api"
    PROJECT_NAME: str = "Pawsonality API"
    VERSION: str = "2.0.0"
    DESCRIPTION: str = "Dog Personality Test & AI Chatbot API"
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # React dev server (alternative)
        "http://localhost:8000",  # FastAPI (self)
    ]
    
    # OpenRouter API
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_MODEL: str = "gpt4-mini"  # claude, gpt4, gpt4-mini, llama, free
    
    # Milvus Configuration
    MILVUS_HOST: str = "localhost"
    MILVUS_PORT: int = 19530
    MILVUS_COLLECTION: str = "pawna_knowledge"
    
    # Embedding Model
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIM: int = 384  # all-MiniLM-L6-v2의 차원
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # Pydantic  설정
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"  # 추가 필드 무시
    )


# 전역 설정 인스턴스
settings = Settings()


def get_settings() -> Settings:
    """
    FastAPI Depends()에서 사용할 설정 getter
    """
    return settings

