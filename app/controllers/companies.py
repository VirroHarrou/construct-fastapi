from fastapi import APIRouter, Depends
from app.services.companies import CompanyService
from app.schemas.companies import CompanyCreate, CompanyResponse
from app.dependencies.database import AsyncSession, get_db

router = APIRouter(tags=["companies"])

@router.post("/companies/", response_model=CompanyResponse)
async def create_company(
    company_data: CompanyCreate,
    session: AsyncSession = Depends(get_db),
):
    service = CompanyService(session)
    return await service.create_company(company_data)