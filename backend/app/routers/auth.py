# app/routers/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, date
from app.auth import get_current_user

from jose import jwt

from app import models, schemas
from app.auth import pwd_context, hash_password, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, check_admin
from app.database import get_db

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

MASTER_ADMIN_KEY = "super-secret-123"

# -------------------
# Register Endpoint
# -------------------
@router.post("/register", response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(
        models.User.username == user.username
    ).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed_pw = hash_password(user.password)
    user_role = "employee"
    if user.admin_key:  # If they filled in the box...
        if user.admin_key == MASTER_ADMIN_KEY: # Match your MASTER_ADMIN_KEY
            user_role = "admin"
        else:
            # STOP! Don't create any user. Throw an error instead.
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Admin Master Key. Account creation aborted."
            )

    new_user = models.User(
        username=user.username,
        password_hash=hashed_pw,
        role = user_role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

# -------------------
# Token / Login Endpoint
# -------------------
@router.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(
        models.User.username == form_data.username
    ).first()

    if not user or not pwd_context.verify(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": user.username, "exp": expire, "role" : user.role}
    access_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/clock-in")
def clock_in(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    active_entry = db.query(models.TimeEntry).filter(
        models.TimeEntry.user_id == current_user.id,
        models.TimeEntry.clock_out == None
    ).first()

    if active_entry:
        raise HTTPException(status_code=400, detail="Already clocked in")

    now = datetime.utcnow()

    entry = models.TimeEntry(
        user_id=current_user.id,
        clock_in=now,        # datetime
        date=now.date()      # date
    )

    db.add(entry)
    db.commit()
    db.refresh(entry)

    return {"message": "Clocked in"}


@router.post("/clock-out")
def clock_out(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    entry = db.query(models.TimeEntry).filter(
        models.TimeEntry.user_id == current_user.id,
        models.TimeEntry.clock_out == None
    ).first()

    if not entry:
        raise HTTPException(status_code=400, detail="Not clocked in")

    entry.clock_out = datetime.utcnow()  

    duration = entry.clock_out - entry.clock_in
    entry.total_hours = round(duration.total_seconds() / 3600, 2)

    db.commit()
    db.refresh(entry)

    return {
        "message": "Clocked out",
        "hours": entry.total_hours
    }


@router.get("/me")
def my_entries(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return db.query(models.TimeEntry).filter(
        TimeEntry.user_id == current_user.id
    ).all()

@router.get("/status")
def clock_status(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    entry = (
        db.query(models.TimeEntry)
        .filter(
            models.TimeEntry.user_id == current_user.id,
            models.TimeEntry.clock_out == None
        )
        .first()
    )

    if entry:
        return {
            "clocked_in": True,
            "clock_in_time": entry.clock_in
        }

    return {"clocked_in": False}


@router.get("/today")
def today_summary(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    entries = (
        db.query(models.TimeEntry)
        .filter(
            models.TimeEntry.user_id == current_user.id,
            models.TimeEntry.date == date.today(),
            models.TimeEntry.total_hours != None
        )
        .all()
    )

    total = sum(e.total_hours for e in entries)

    return {
        "date": date.today(),
        "total_hours": round(total, 2),
        "entries": entries
    }

@router.get("/week")
def weekly_summary(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    today = date.today()
    start = today - timedelta(days = today.weekday())

    entries = (
        db.query(models.TimeEntry)
        .filter(
            models.TimeEntry.user_id == current_user.id,
            models.TimeEntry.date >= start,
            models.TimeEntry.total_hours != None
        )
        .all()
    )
    total = sum(e.total_hours for e in entries)

    return{
        "week_start": start,
        "total_hours": round(total, 2),
        "entries": entries
    }

@router.get("/admin/all-logs")
def get_all_logs(
    db: Session = Depends(get_db),
    admin: models.User = Depends(check_admin)
):
    # 1. We join TimeEntry and User on the 'id' field
    # 2. We select exactly which fields we want to send to React
    results = db.query(
        models.TimeEntry.id,
        models.TimeEntry.clock_in,
        models.TimeEntry.clock_out,
        models.TimeEntry.total_hours,
        models.TimeEntry.date,
        models.User.username  # <--- This is the magic join!
    ).join(models.User, models.TimeEntry.user_id == models.User.id).all()

    # 3. Convert SQLAlchemy rows into a list of dictionaries for JSON
    return [
        {
            "id": r.id,
            "username": r.username,
            "date": r.date.isoformat() if r.date else None,
            "clock_in": r.clock_in.strftime("%H:%M:%S") if r.clock_in else None,
            "clock_out": r.clock_out.strftime("%H:%M:%S") if r.clock_out else "Active",
            "total_hours": r.total_hours if r.total_hours is not None else 0
        } for r in results
    ]

