# models.py
from pydantic import BaseModel

class User(BaseModel):
    fullname: str
    email: str
    dni: str
    password: str
    confirm_password: str

class Login(BaseModel):
    dni: str
    password: str

class Transferencias(BaseModel):
    numero_cuenta: str
    cantidad_dinero: int
