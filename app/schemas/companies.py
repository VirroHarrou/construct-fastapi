from pydantic import UUID4, BaseModel, ConfigDict, Field, field_validator

class CompanyBase(BaseModel):
    name: str = Field(..., max_length=255)
    inn: str = Field(..., min_length=10, max_length=10)
    
    @field_validator('inn')
    def validate_inn(cls, v):
        if not v.isdigit():
            raise ValueError("ИНН компании должен содержать только цифры")
        if len(v) != 10:
            raise ValueError("ИНН компании должен содержать 10 цифр")
        return v

class CompanyCreate(CompanyBase):
    pass

class CompanyResponse(CompanyBase):
    id: UUID4
    model_config = ConfigDict(from_attributes=True)