from fastapi import FastAPI
import requests
from pydantic import BaseModel

app = FastAPI()

@app.get("/")
class user(BaseModel):
    fullname: str
    email: str
    dni: str
    password: str
    confirm_password: str

