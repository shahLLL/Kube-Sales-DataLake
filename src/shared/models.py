from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, Literal

# Allowed vehicle types.
VehicleType = Literal["coupe", "convertible", "sedan", "suv"]

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