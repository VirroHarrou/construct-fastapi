from datetime import datetime, timedelta, timezone
from pathlib import Path
from fastapi import HTTPException, status
from jose import JWTError, jwt
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from sqlalchemy import UUID, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import settings
from app.models.token import RefreshToken
from app.utils.security import credentials_exception
from app.schemas.auth import Token, TokenData

class AuthService:    
    def __init__(self, session: AsyncSession):
        self.algorithm = settings.jwt_algorithm
        self.private_key, self.public_key = self._load_keys()
        self.access_expire = settings.jwt_access_expire
        self.refresh_expire = settings.refresh_expire
        self.refresh_secret = settings.jwt_refresh_secret
        self.session = session

    def _load_keys(self):
        """Загружает или генерирует ключи при необходимости"""
        keys_dir = Path("keys")
        private_key_file = keys_dir / "jwt_private.pem"
        public_key_file = keys_dir / "jwt_public.pem"
        
        if settings.jwt_private_key and settings.jwt_public_key:
            private_key = serialization.load_pem_private_key(
                settings.jwt_private_key.encode(),
                password=None,
                backend=default_backend()
            )
            public_key = serialization.load_pem_public_key(
                settings.jwt_public_key.encode(),
                backend=default_backend()
            )
            print(settings.jwt_public_key)
            return private_key, public_key
        
        keys_dir.mkdir(exist_ok=True)
        if not private_key_file.exists() or not public_key_file.exists():
            raise FileExistsError("")
        else:
            with open(private_key_file, "rb") as f:
                private_key = serialization.load_pem_private_key(
                    f.read(),
                    password=None,
                    backend=default_backend()
                )
            with open(public_key_file, "rb") as f:
                public_key = serialization.load_pem_public_key(
                    f.read(),
                    backend=default_backend()
                )
        
        settings.jwt_private_key = private_key
        settings.jwt_public_key = public_key
        
        return private_key, public_key
        
    async def create_tokens(self, user_id: UUID) -> dict:
        access_token = self._create_access_token({"sub":str(user_id)})
        refresh_token = await self._create_refresh_token(user_id)
        return {"access_token":access_token, "refresh_token": refresh_token, "token_type":"bearer"}

    def _create_access_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(seconds=self.access_expire)
        to_encode.update({"exp": expire})
        return jwt.encode(
            to_encode,
            self.private_key,
            algorithm=self.algorithm
        )
        
    async def _create_refresh_token(self, user_id: UUID) -> str:
        expire = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(seconds=settings.refresh_expire)
        refresh_token = jwt.encode(
            {"sub": str(user_id), "exp": expire},
            self.private_key,
            algorithm=self.algorithm
        )
        
        db_token = RefreshToken(
            user_id=user_id,
            token=refresh_token,
            expires_at=expire
        )
        self.session.add(db_token)
        await self.session.commit()
        
        return refresh_token

    def verify_token(self, token: str) -> TokenData:
        try:
            payload = jwt.decode(
                token,
                self.public_key,
                algorithms=[self.algorithm]
            )
            user_id = payload.get("sub")
            return TokenData(user_id=user_id)
        except JWTError as e:
            raise credentials_exception from e
    
    async def refresh_access_token(self, refresh_token: str) -> dict:
        try:
            payload = jwt.decode(
                refresh_token,
                self.public_key,
                algorithms=[self.algorithm]
            )
            user_id = payload.get("sub")
        except (JWTError, ValueError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        db_token = await self.session.execute(
            select(RefreshToken).filter(
                RefreshToken.token == refresh_token,
                RefreshToken.user_id == user_id
            )
        )
        db_token = db_token.scalar()
        
        if not db_token or not db_token.is_active():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token revoked or expired"
            )

        # Инвалидация старого токена
        db_token.revoked = True
        await self.session.commit()

        # Генерация новой пары токенов
        return await self.create_tokens(user_id)