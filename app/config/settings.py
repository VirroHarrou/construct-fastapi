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
    
    JWT_ALGORITHM: str = Field(default="ES256")
    JWT_ACCESS_EXPIRE: int = Field(default=3600)
    JWT_PUBLIC_KEY: str = Field(default="")
    JWT_PRIVATE_KEY: str = Field(default="")
    
    REFRESH_EXPIRE: int = Field(default=604800)
    JWT_REFRESH_SECRET: str = Field(default="")
    
    IMAGE_STORAGE: Path = Path("/app/storage")  # Docker volume
    IMAGE_BASE_URL: str = "/storage/images"
    ALLOWED_EXTENSIONS: set = {".jpg", ".jpeg", ".png", ".webp"}
    MAX_FILE_SIZE: int = 10 * 1024 * 1024 # 10MB
    
    @property
    def DATABASE_URL(self) -> PostgresDsn:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@" \
               f"{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def DATABASE_SYNC_URL(self) -> PostgresDsn:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@" \
               f"{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._load_key_files()
        
    def _load_key_files(self):
        """Загружает ключи из файлов только если они не заданы в environment"""
        keys_dir = Path("keys")
        keys_dir.mkdir(exist_ok=True)
        
        # Для приватного ключа
        if not self.JWT_PRIVATE_KEY:
            private_key_file = keys_dir / "jwt_private.pem"
            if private_key_file.exists():
                with open(private_key_file) as f:
                    self.JWT_PRIVATE_KEY = f.read()
        
        # Для публичного ключа
        if not self.JWT_PUBLIC_KEY:
            public_key_file = keys_dir / "jwt_public.pem"
            if public_key_file.exists():
                with open(public_key_file) as f:
                    self.JWT_PUBLIC_KEY = f.read()

settings = Settings()
