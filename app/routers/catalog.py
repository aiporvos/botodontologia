from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import Professional, TreatmentPrice, AdminUser
from app.auth import get_current_active_user

router = APIRouter(prefix="/api", tags=["catalog"])

@router.get("/professionals")
async def list_professionals(
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_active_user),
):
    profs = db.query(Professional).filter(Professional.is_active == True).all()
    return [
        {"id": p.id, "full_name": p.full_name, "specialty": p.specialty} for p in profs
    ]

@router.get("/prices")
async def list_prices(
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_active_user),
):
    prices = db.query(TreatmentPrice).filter(TreatmentPrice.is_active == True).all()
    return [
        {"id": p.id, "code": p.code, "name": p.name, "price": p.price} for p in prices
    ]
