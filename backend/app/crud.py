from sqlalchemy.orm import Session
from . import models, schemas, auth

def get_admin_user(db: Session):
    return db.query(models.User).filter(models.User.role == "admin").first()

def create_admin(db: Session, user_data: schemas.UserCreate):
    hashed_pw = auth.hash_password(user_data.password)
    admin = models.User(
        username=user_data.username,
        password_hash=hashed_pw,
        role="admin"
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin
