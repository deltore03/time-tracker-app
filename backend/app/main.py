import os
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from fastapi import FastAPI
from .database import engine, SessionLocal, Base
from . import models, crud, schemas
from .routers import auth, time_entries
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Initialize Admin
    db = SessionLocal()
    if not crud.get_admin_user(db):
        print("Admin not found. Initializing default admin...")
        # Get from environment variables or use defaults
        admin_user = schemas.UserCreate(
            username=os.getenv("ADMIN_USERNAME", "admin"),
            password=os.getenv("ADMIN_PASSWORD", "changeme")
        )
        crud.create_admin(db, admin_user)
    db.close()
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], # Allow your React app
    allow_credentials=True,
    allow_methods=["*"], # Allow GET, POST, PATCH, DELETE, etc.
    allow_headers=["*"], # Allow Authorization headers
)

app.include_router(auth.router)
app.include_router(time_entries.router)


@app.get("/")

def read_root():
	return  {"message" : "Time Tracker API is running !!!"}
