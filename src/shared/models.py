from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, Literal
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Float, DateTime

# Allowed vehicle types.
VehicleType = Literal["coupe", "convertible", "sedan", "suv"]

class Base(DeclarativeBase):
    pass

class CarSaleORM(Base):
    __tablename__ = "car_sales"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    make: Mapped[str] = mapped_column(String)
    model: Mapped[str] = mapped_column(String)
    year: Mapped[int] = mapped_column()
    vehicle_type: Mapped[str] = mapped_column(String)
    color: Mapped[str] = mapped_column(String)
    msrp: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class CarSale(BaseModel):
    id: Optional[str] = None
    make: str = Field(..., min_length=1)
    model: str = Field(..., min_length=1)
    year: int = Field(..., ge=1900, le=2100)
    vehicle_type: VehicleType = Field(..., alias="type")
    color: str = Field(..., min_length=1)
    msrp: float = Field(..., gt=0)
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        populate_by_name = True