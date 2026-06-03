from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import SessionLocal
from app import models, schemas
from app.auth import get_current_user, check_admin

router = APIRouter(prefix="/time", tags=["time"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.patch("/edit-entry/{entry_id}")
def admin_time_entry(
    entry_id: int,
    update_data: schemas.TimeEntryUpdate,
    db: Session = Depends(get_db),
    admin: models.User = Depends(check_admin)):

    entry = db.query(models.TimeEntry).filter(models.TimeEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="entry not found")

    if update_data.clock_in:
        entry.clock_in = update_data.clock_in
    if update_data.clock_out:
        entry.clock_out = update_data.clock_out

    # Meticulous Logic: Only calculate hours if BOTH times are present
    if entry.clock_in and entry.clock_out:
        if entry.clock_out < entry.clock_in:
            raise HTTPException(
                status_code=400, 
                detail="Error: Clock-out cannot be earlier than clock-in"
            )
        duration = entry.clock_out - entry.clock_in
        entry.total_hours = round(duration.total_seconds() / 3600, 2)
        # Sync the 'date' field in case the admin moved the entry to a different day
        entry.date = entry.clock_in.date()
    else:
        # If one is missing, it's an active session or incomplete; total_hours must be reset
        entry.total_hours = None

    db.commit()
    db.refresh(entry)
    return {
        "message": "Entry updated successfully by admin",
        "entry": entry}

@router.delete("/delete-entry/{entry_id}")
def admin_delete_time_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    admin: models.User = Depends(check_admin)
):
    entry = db.query(models.TimeEntry).filter(models.TimeEntry.id == entry_id).first()

    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail = "Time entry not found"
        )
    
    db.delete(entry)
    db.commit()

    return{
        "message": f"Entry {entry_id} has been permanently deleted by admin {admin.username}"}

@router.get("/admin/user-entries/{username}")
def get_user_entries_for_admin(
    username: str,
    db: Session = Depends(get_db),
    admin: models.User = Depends(check_admin)
):
    user = db.query(models.User).filter(models.User.username == username).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return db.query(models.TimeEntry).filter(models.TimeEntry.user_id == user.id).all()
