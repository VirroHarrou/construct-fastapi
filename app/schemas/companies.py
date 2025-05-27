from pydantic import UUID4, BaseModel, ConfigDict, Field

class CompanyBase(BaseModel):
    name: str = Field(..., max_length=255)

class CompanyCreate(CompanyBase):
    user_id: str

class CompanyResponse(CompanyBase):
    id: UUID4

    model_config = ConfigDict(from_attributes=True)