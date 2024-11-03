from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
import psycopg2
import os

load_dotenv()

app = FastAPI()

# Conexión a la base de datos de Supabase
connection = psycopg2.connect(
    host=os.getenv("host"),
    port=os.getenv("port"),
    dbname=os.getenv("dbname"),
    user=os.getenv("user"),
    password=os.getenv("password")
)
cursor = connection.cursor()

# Comando SQL para crear la tabla
create_table_sql = """
CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    full_name TEXT NOT NULL,
    email varchar(250),
    password text,
    dni text,
    numero_cuenta text,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
"""
cursor.execute(create_table_sql)
connection.commit()

print("Tabla creada con éxito")

# Cierra la conexión
cursor.close()
connection.close()

@app.get("/")
class user(BaseModel):
    fullname: str
    email: str
    dni: str
    password: str
    confirm_password: str