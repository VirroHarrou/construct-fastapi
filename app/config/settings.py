from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field, PostgresDsn

class Settings(BaseSettings):
    PROJECT_NAME: str = "Construct"
    PROJECT_VERSION: str = "0.1.0"

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "construct"
    
    jwt_algorithm: str = Field(default="ES256")
    jwt_access_expire: int = Field(default=3600)
    jwt_public_key: str = Field(default="")
    jwt_private_key: str = Field(default="")
    
    refresh_expire: int = Field(default=604800)
    jwt_refresh_secret: str = Field(default="")
    
    @property
    def DATABASE_URL(self) -> PostgresDsn:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@" \
               f"{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        if not self.jwt_private_key.startswith('-----'):
            with open("keys/jwt_private.pem") as f:
                self.jwt_private_key = f.read()
                
        if not self.jwt_public_key.startswith('-----'):
            with open("keys/jwt_public.pem") as f:
                self.jwt_public_key = f.read()

settings = Settings()