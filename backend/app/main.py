from fastapi import FastAPI
from .database import engine
from . import models 
from .routers import auth, time_entries
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], # Allow your React app
    allow_credentials=True,
    allow_methods=["*"], # Allow GET, POST, PATCH, DELETE, etc.
    allow_headers=["*"], # Allow Authorization headers
)

models.Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(time_entries.router)


@app.get("/")

def read_root():
	return  {"message" : "Time Tracker API is running !!!"}
