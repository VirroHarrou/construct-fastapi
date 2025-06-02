from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from app.dependencies.auth import get_refresh_token
from app.models.token import RefreshToken
from app.models.user import User
from app.dependencies.database import AsyncSession, get_db
from app.services.auth import AuthService
from app.schemas.auth import Token
from app.utils.security import verify_password

router = APIRouter(tags=["auth"])

def get_auth_service(session: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(session)

@router.post("/auth/token", response_model=Token)
async def login(
    phone: str,
    password: str,
    service: AuthService = Depends(get_auth_service),
):
    user = await service.session.execute(select(User).where(User.phone == phone))
    user = user.scalar()
    
    if not user or not verify_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect phonenumber or password",
        )
    
    token = await service.create_tokens(user.id)
    return token

@router.post("/auth/refresh", response_model=Token, responses={
        401: {"description": "Invalid refresh token"},
        400: {"description": "Missing refresh token header"}
    },
    summary="Refresh access token",)
async def refresh_token(
    refresh_token: str = Depends(get_refresh_token),
    service: AuthService = Depends(get_auth_service),
):
    return await service.refresh_access_token(refresh_token)

@router.post("/auth/logout")
async def logout(
    refresh_token: str = Depends(get_refresh_token),
    service: AuthService = Depends(get_auth_service),
):
    result = await service.session.execute(
        update(RefreshToken)
        .where(RefreshToken.token == refresh_token)
        .values(revoked=True)
    )
    await service.session.commit()
    return {"status": "logged out"}