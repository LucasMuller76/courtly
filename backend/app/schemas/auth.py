import re
from pydantic import BaseModel, EmailStr, field_validator


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    club_name: str
    club_slug: str

    @field_validator("name")
    @classmethod
    def name_min_length(cls, v: str) -> str:
        if len(v.strip()) < 2:
            raise ValueError("Nome deve ter pelo menos 2 caracteres.")
        return v.strip()

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Senha deve ter pelo menos 8 caracteres.")
        return v

    @field_validator("club_slug")
    @classmethod
    def slug_format(cls, v: str) -> str:
        v = v.strip().lower()
        if len(v) < 3:
            raise ValueError("Endereço deve ter pelo menos 3 caracteres.")
        if not re.match(r"^[a-z0-9-]+$", v):
            raise ValueError("Use apenas letras minúsculas, números e hífens.")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: str
    name: str
    email: str

    model_config = {"from_attributes": True}


class ClubOut(BaseModel):
    id: str
    name: str
    slug: str
    phone: str | None = None
    timezone: str
    is_active: bool

    model_config = {"from_attributes": True}


class MeResponse(BaseModel):
    user: UserOut
    club: ClubOut | None = None