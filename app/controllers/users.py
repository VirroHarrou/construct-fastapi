from uuid import UUID
from fastapi import APIRouter, Depends, Path, status
from app.dependencies.auth import get_current_user
from app.services.users import UserService
from app.schemas.users import UserCreate, UserResponse, UserUpdate
from app.dependencies.database import AsyncSession, get_db

router = APIRouter(tags=["users"])

def get_user_service(session: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(session)

@router.post("/users/", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    service: UserService = Depends(get_user_service),
):
    return await service.create_user(user_data)

@router.get("/users/", response_model=UserResponse)
async def get_user(
    user_id: UUID = Path(..., description="User ID"),
    service: UserService = Depends(get_user_service),
):
    return await service.get_user(user_id)

@router.put("/users/", response_model=UserResponse)
async def update_user(
    user_data: UserUpdate,
    user: UserResponse = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    return await service.update_user(user.id, user_data)

@router.delete("/users/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user: UserResponse = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    await service.delete_user(user.id)