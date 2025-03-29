from pydantic_settings import BaseSettings
from typing import Optional, List
from pydantic import AnyHttpUrl, validator
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    APP_NAME: str = os.getenv("APP_NAME", "Trading System")
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "Trading System")
    DEBUG: bool = os.getenv("DEBUG", True)
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-super-secret-key-here")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    
    # API settings
    API_V1_STR: str = "/api/v1"
    
    # Server settings
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8000))
    
    # WebSocket settings
    WS_HOST: str = os.getenv("WS_HOST", "0.0.0.0")
    WS_PORT: int = int(os.getenv("WS_PORT", 8001))

    # 数据库配置
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5532/postgres")
    
    # CORS配置
    CORS_ORIGINS: List[str] = ["*"]
    
    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str]:
        if isinstance(v, str):
            if v.startswith("["):
                # 处理JSON字符串格式的列表
                import json
                try:
                    return json.loads(v)
                except json.JSONDecodeError:
                    return [v]
            else:
                # 处理逗号分隔的字符串
                return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        return [str(v)]
    
    # 日志配置
    LOG_LEVEL: str = "DEBUG"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE: str = "logs/app.log"

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings() 