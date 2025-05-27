from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from app.models.user import User
from app.schemas.users import UserCreate, UserResponse, UserUpdate
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.security import get_password_hash

class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(self, user_data: UserCreate) -> UserResponse:
        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            **user_data.model_dump(exclude={"company_id","password"}),
            company_id=user_data.company_id,
            password=hashed_password,
        )
        self.session.add(new_user)
        await self.session.commit()
        await self.session.refresh(new_user)
        return UserResponse.model_validate(new_user)
    
    async def get_user(self, user_id: UUID) -> UserResponse:
        user = await self.session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return UserResponse.model_validate(user)
    
    async def update_user(
        self,
        user_id: UUID,
        user_data: UserUpdate
    ) -> UserResponse:
        user = await self.session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Обновляем только переданные поля
        for key, value in user_data.model_dump(exclude_unset=True).items():
            if key == "password" and value:
                # В реальном проекте хэшируем пароль
                setattr(user, key, value)
            elif key != "password":
                setattr(user, key, value)
        
        await self.session.commit()
        await self.session.refresh(user)
        return UserResponse.model_validate(user)
    
    async def delete_user(self, user_id: UUID) -> None:
        user = await self.session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        await self.session.delete(user)
        await self.session.commit()