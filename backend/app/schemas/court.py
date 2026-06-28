import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator


class CourtCreate(BaseModel):
    name: str
    price_per_hour: Optional[int] = None  # em centavos

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Nome da quadra é obrigatório.")
        return v

    @field_validator("price_per_hour")
    @classmethod
    def price_non_negative(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v < 0:
            raise ValueError("Preço deve ser maior que zero.")
        return v


class CourtUpdate(BaseModel):
    name: Optional[str] = None
    price_per_hour: Optional[int] = None
    is_active: Optional[bool] = None


class CourtOut(BaseModel):
    id: uuid.UUID
    club_id: uuid.UUID
    name: str
    price_per_hour: Optional[int] = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}