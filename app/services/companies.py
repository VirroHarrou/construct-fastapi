from uuid import UUID
from app.models.company import Company
from app.schemas.companies import CompanyCreate, CompanyResponse
from sqlalchemy.ext.asyncio import AsyncSession

class CompanyService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_company(self, data: CompanyCreate) -> CompanyResponse:
        company = Company(**data.model_dump())
        self.session.add(company)
        await self.session.commit()
        await self.session.refresh(company)
        return CompanyResponse.model_validate(company)
