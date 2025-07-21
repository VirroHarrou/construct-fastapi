from uuid import UUID
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.company import Company
from app.models.user import User
from app.schemas.companies import CompanyCreate, CompanyResponse

class CompanyService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_company(
        self, 
        company_data: CompanyCreate, 
        user_id: UUID
    ) -> CompanyResponse:
        user = await self.session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if user.company:
            raise HTTPException(
                status_code=400, 
                detail="User already has a company"
            )
        
        existing_company = await self.session.execute(
            select(Company).where(Company.inn == company_data.inn)
        )
        if existing_company.scalars().first():
            raise HTTPException(
                status_code=400,
                detail="Company with this INN already exists"
            )
        
        new_company = Company(**company_data.model_dump())
        new_company.user = user
        self.session.add(new_company)
        await self.session.commit()
        await self.session.refresh(new_company)
        
        return CompanyResponse.model_validate(new_company)

    async def update_company(
        self,
        company_id: UUID,
        company_data: CompanyCreate,
        user_id: UUID
    ) -> CompanyResponse:
        company = await self.session.get(Company, company_id)
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        
        if company.user.id != user_id:
            raise HTTPException(
                status_code=403, 
                detail="Not the owner of the company"
            )
        
        # Обновляем данные
        for field, value in company_data.model_dump().items():
            setattr(company, field, value)
        
        await self.session.commit()
        await self.session.refresh(company)
        return CompanyResponse.model_validate(company)