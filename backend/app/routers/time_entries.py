from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import SessionLocal
from app import models
from app.auth import get_current_user

router = APIRouter(prefix="/time", tags=["time"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/clock-in")
def clock_in(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    now = datetime.utcnow()

    entry = models.TimeEntry(
        user_id=current_user.id,
        clock_in=now,
        date=now.date()
    )

    db.add(entry)
    db.commit()
    db.refresh(entry)

    return {
        "message": "Clocked in",
        "time_entry_id": entry.id,
        "clock_in": entry.clock_in
    }


@router.post("/clock-out")
def clock_out(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    entry = (
        db.query(models.TimeEntry)
        .filter(
            models.TimeEntry.user_id == current_user.id,
            models.TimeEntry.clock_out == None
        )
        .order_by(models.TimeEntry.clock_in.desc())
        .first()
    )

    if not entry:
        raise HTTPException(status_code=400, detail="No active clock-in found")

    now = datetime.utcnow()
    entry.clock_out = now

    duration = now - entry.clock_in
    entry.total_hours = str(round(duration.total_seconds() / 3600, 2))

    db.commit()
    db.refresh(entry)

    return {
        "message": "Clocked out",
        "clock_out": entry.clock_out,
        "total_hours": entry.total_hours
    }


@router.patch("/edit-entry")
def admin_time_entry(
    entry_id: str,
    update_data: schemas.TimeEntryUpdate,
    db: Session = Depends(get_db)
    admin: models.User = Depends(check_admin)):

    entry = db.query(model.TimeEntry).filter(models.TimeEntry.id == entry_id).first
    if not entry:
        raise HTTPException(status_code=404, detail="entry not found")

    if update_data.clock_in:
        entry.clock_in = update_data.clock_in
    if update_data.clock_out:
        entry.clock_out = update_data.clock_out

    if entry.clock_out or entry.clock_in:
        duration = entry.clock_out - entry.clock_in
        entry.total_hours = round(duration.total_seconds() / 3600, 2)

    db.commit()
    db.refresh(entry)
    return entry
