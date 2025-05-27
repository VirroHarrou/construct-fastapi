from fastapi import Depends, Header
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError

from app.utils.security import credentials_exception
from app.models.user import User
from app.schemas.users import UserResponse
from app.services.auth import AuthService
from app.dependencies.database import AsyncSession, get_db

security_scheme = HTTPBearer(
    bearerFormat="JWT",
    description="Введите токен в формате: Bearer <ваш_токен>"
)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    auth_service = AuthService(db)
    try:
        token_data = auth_service.verify_token(credentials.credentials)
        user = await db.get(User, token_data.user_id)
        if not user:
            raise credentials_exception
        return UserResponse.model_validate(user)
    except JWTError:
        raise credentials_exception
    
async def get_refresh_token(
    refresh_token: str = Header(..., alias="Refresh-Token")
) -> str:
    return refresh_token