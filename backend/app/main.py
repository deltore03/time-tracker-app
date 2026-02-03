from fastapi import FastAPI
from .database import engine
from . import models 

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


@app.get("/")

def read_root():
	return  {"message" : "Time Tracker API is running !!!"}
