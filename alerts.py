from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.services.alert_service import AlertService

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


class AlertCreate(BaseModel):
    title: str
    message: str
    alert_type: str = "date"
    trigger_date: Optional[datetime] = None
    note_id: Optional[int] = None


@router.post("/")
def create_alert(body: AlertCreate, db: Session = Depends(get_db)):
    return AlertService(db).create_alert(**body.model_dump())


@router.get("/")
def list_alerts(active_only: bool = False, db: Session = Depends(get_db)):
    return AlertService(db).get_alerts(active_only=active_only)


@router.put("/{alert_id}/trigger")
def trigger_alert(alert_id: int, db: Session = Depends(get_db)):
    return AlertService(db).trigger_alert(alert_id)


@router.delete("/{alert_id}")
def delete_alert(alert_id: int, db: Session = Depends(get_db)):
    return {"deleted": AlertService(db).delete_alert(alert_id)}


@router.post("/check-inactivity/")
def check_inactivity(days: int = 7, db: Session = Depends(get_db)):
    return AlertService(db).check_inactivity_alerts(days=days)
