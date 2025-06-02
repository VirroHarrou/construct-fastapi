from typing import Optional
from pydantic import UUID4, BaseModel, ConfigDict, Field, field_validator, validator

from app.schemas.companies import CompanyResponse

class UserBase(BaseModel):
    fio: str = Field(..., max_length=255)
    phone: str = Field(..., min_length=5, max_length=20)
    address: str = Field(..., max_length=255)
    inn: str = Field(..., min_length=12, max_length=12)
    company_id: Optional[str] = None
    image_url: Optional[str] = Field(None, max_length=511)
    
    @field_validator('inn')
    def validate_inn(cls, v):
        if not v.isdigit():
            raise ValueError("ИНН должен содержать только цифры")
        if len(v) != 12:
            raise ValueError("ИНН физлица должен содержать 12 цифр")
        return v

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=255)
    
class UserUpdate(BaseModel):
    fio: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, min_length=5, max_length=20)
    address: Optional[str] = Field(None, max_length=255)
    password: Optional[str] = Field(None, min_length=6, max_length=255)
    image_url: Optional[str] = Field(None, max_length=511)
    
    @field_validator('inn', check_fields=False)
    def validate_inn_on_update(cls, v):
        if v is not None:
            if not v.isdigit():
                raise ValueError("ИНН должен содержать только цифры")
            if len(v) != 12:
                raise ValueError("ИНН физлица должен содержать 12 цифр")
        return v

class UserResponse(UserBase):
    id: UUID4
    company: Optional[CompanyResponse] = None 

    model_config = ConfigDict(from_attributes=True)

