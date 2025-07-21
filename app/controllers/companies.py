from uuid import UUID
from fastapi import APIRouter, Depends, status
from app.dependencies.auth import get_current_user
from app.schemas.users import UserResponse
from app.schemas.companies import CompanyCreate, CompanyResponse
from app.services.companies import CompanyService
from app.dependencies.database import AsyncSession, get_db

router = APIRouter(tags=["companies"])

def get_company_service(session: AsyncSession = Depends(get_db)) -> CompanyService:
    return CompanyService(session)

@router.post(
    "/companies/",
    response_model=CompanyResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_company(
    company_data: CompanyCreate,
    current_user: UserResponse = Depends(get_current_user),
    service: CompanyService = Depends(get_company_service),
):
    return await service.create_company(company_data, current_user.id)

@router.put("/companies/{company_id}", response_model=CompanyResponse)
async def update_company(
    company_id: UUID,
    company_data: CompanyCreate,
    current_user: UserResponse = Depends(get_current_user),
    service: CompanyService = Depends(get_company_service),
):
    return await service.update_company(company_id, company_data, current_user.id)