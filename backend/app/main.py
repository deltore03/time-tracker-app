from fastapi import FastAPI
from .database import engine
from . import models 
from .routers import auth, time_entries

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(time_entries.router)


@app.get("/")

def read_root():
	return  {"message" : "Time Tracker API is running !!!"}
