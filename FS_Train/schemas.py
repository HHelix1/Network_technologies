from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from typing import List, Optional, Dict, Any
from datetime import date, datetime
from enum import Enum as PyEnum
import re

class AccessRights(str, PyEnum):
    ADMIN = "admin"
    HR = "hr"
    MANAGER = "manager"
    EMPLOYEE = "employee"

class TrainingStatus(str, PyEnum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

def validate_phone_number(value: str) -> str:
    if not re.match(r'^\+?[1-9]\d{1,14}$', value):
        raise ValueError("Некорректный формат номера телефона")
    return value

class EducationalProgramBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, description="Название программы")
    protocol_number: int = Field(..., gt=0, description="Номер протокола (натуральное число)")
    description: Optional[str] = Field(None, max_length=500)

class EducationalProgramCreate(EducationalProgramBase):
    @field_validator('protocol_number')
    def validate_protocol_number(cls, v):
        if v <= 0:
            raise ValueError("Номер протокола должен быть натуральным числом")
        return v

class EducationalProgramUpdate(EducationalProgramBase):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    protocol_number: Optional[int] = Field(None, gt=0)

class EducationalProgramResponse(EducationalProgramBase):
    id: int
    created_at: date
    is_active: bool
    model_config = ConfigDict(from_attributes=True)

class EmployeeBase(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    position: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone_number: str = Field(..., description="Номер телефона")
    birth_date: date
    hire_date: date = Field(default_factory=date.today)

class EmployeeCreate(EmployeeBase):
    @field_validator('phone_number')
    def validate_phone(cls, v):
        return validate_phone_number(v)

    @field_validator('birth_date')
    def validate_age(cls, v):
        age = (date.today() - v).days // 365
        if age < 18:
            raise ValueError("Возраст сотрудника должен быть не менее 18 лет")
        return v

class EmployeeUpdate(EmployeeBase):
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    position: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    birth_date: Optional[date] = None
    hire_date: Optional[date] = None

    @field_validator('phone_number')
    def validate_phone(cls, v):
        if v is not None:
            return validate_phone_number(v)
        return v

class EmployeeResponse(EmployeeBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class TrainingAssignmentBase(BaseModel):
    employee_id: int
    education_id: int
    start_date: date
    end_date: date
    status: TrainingStatus = TrainingStatus.PLANNED

class TrainingAssignmentCreate(TrainingAssignmentBase):
    @field_validator('end_date')
    def validate_dates(cls, v, info):
        if 'start_date' in info.data and v < info.data['start_date']:
            raise ValueError("Дата окончания не может быть раньше даты начала")
        return v

class TrainingAssignmentUpdate(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[TrainingStatus] = None
    updated_at: date = Field(default_factory=date.today)

    @field_validator('end_date')
    def validate_dates(cls, v, info):
        if 'start_date' in info.data and v and info.data['start_date'] and v < info.data['start_date']:
            raise ValueError("Дата окончания не может быть раньше даты начала")
        return v

class TrainingAssignmentResponse(TrainingAssignmentBase):
    id: int
    updated_at: date
    model_config = ConfigDict(from_attributes=True)

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    access_rights: AccessRights = AccessRights.EMPLOYEE
    employee_id: Optional[int] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="Пароль должен содержать минимум 8 символов")
    confirm_password: str

    @field_validator('confirm_password')
    def passwords_match(cls, v, info):
        if 'password' in info.data and v != info.data['password']:
            raise ValueError("Пароли не совпадают")
        return v

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    access_rights: Optional[AccessRights] = None
    employee_id: Optional[int] = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

"""@app.get("/health")
def health_check():
    from datetime import datetime
    return {"status": "healthy", "timestamp": datetime.now()}"""