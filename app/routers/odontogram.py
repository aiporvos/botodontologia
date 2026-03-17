from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from typing import List

from app.database import get_db
from app.models import DentalRecord, AdminUser
from app.auth import get_current_active_user

router = APIRouter(prefix="/api", tags=["odontogram"])

@router.get("/patients/{patient_id}/odontogram")
async def get_odontogram(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_active_user),
):
    records = db.query(DentalRecord).filter(DentalRecord.patient_id == patient_id).all()

    teeth = {}
    surface_reverse_map = {
        "M": "left",
        "D": "right",
        "O": "center",
        "V": "top",
        "P": "bottom",
        "L": "bottom",
    }

    for r in records:
        tooth_num = str(r.tooth)
        if tooth_num not in teeth:
            teeth[tooth_num] = {}

        if not r.face:
            teeth[tooth_num]["_whole"] = r.procedure_name
        else:
            surface = surface_reverse_map.get(r.face, r.face.lower())
            teeth[tooth_num][surface] = r.procedure_name

    return {
        "teeth": teeth,
        "records": [
            {
                "id": r.id,
                "tooth": r.tooth,
                "face": r.face,
                "procedure_name": r.procedure_name,
                "record_status": r.record_status,
                "record_date": r.record_date.isoformat() if r.record_date else None,
            }
            for r in records
        ],
    }

@router.post("/patients/{patient_id}/odontogram")
async def save_patient_odontogram(
    patient_id: int,
    data: dict,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_active_user),
):
    teeth = data.get("teeth", {})
    try:
        db.query(DentalRecord).filter(DentalRecord.patient_id == patient_id).delete()

        for tooth_number_str, tooth_data in teeth.items():
            tooth_num = int(tooth_number_str)

            if isinstance(tooth_data, dict) and tooth_data.get("_whole"):
                record = DentalRecord(
                    patient_id=patient_id,
                    tooth=str(tooth_num),
                    procedure_name=tooth_data["_whole"],
                    record_status="completed",
                    record_date=date.today(),
                )
                db.add(record)
            elif isinstance(tooth_data, dict):
                for surface, treatment in tooth_data.items():
                    if surface.startswith("_"):
                        continue
                    surface_map = {
                        "top": "V" if tooth_num < 40 else "L",
                        "bottom": "P" if tooth_num < 40 else "V",
                        "left": "M",
                        "right": "D",
                        "center": "O",
                    }
                    record = DentalRecord(
                        patient_id=patient_id,
                        tooth=str(tooth_num),
                        face=surface_map.get(surface, surface),
                        procedure_name=treatment,
                        record_status="completed",
                        record_date=date.today(),
                    )
                    db.add(record)
            elif isinstance(tooth_data, str):
                record = DentalRecord(
                    patient_id=patient_id,
                    tooth=str(tooth_num),
                    procedure_name=tooth_data,
                    record_status="completed",
                    record_date=date.today(),
                )
                db.add(record)

        db.commit()
        return {"status": "ok"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/odontogram")
async def save_odontogram_entry(
    data: dict,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_active_user),
):
    try:
        record = DentalRecord(
            patient_id=data["patient_id"],
            tooth=data["tooth"],
            face=data.get("face"),
            procedure_name=data.get("procedure_name", ""),
            record_status=data.get("status", "planned"),
            record_date=date.today(),
        )
        db.add(record)
        db.commit()
        return {"status": "ok", "id": record.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/odontogram/{record_id}")
async def delete_odontogram_entry(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_active_user),
):
    r = db.query(DentalRecord).filter(DentalRecord.id == record_id).first()
    if r:
        db.delete(r)
        db.commit()
    return {"status": "ok"}
