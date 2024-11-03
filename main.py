from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import psycopg2
import bcrypt
import os
import random

load_dotenv()

app = FastAPI()

# Conexión a la base de datos de Supabase
def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("host"),
        port=os.getenv("port"),
        dbname=os.getenv("dbname"),
        user=os.getenv("user"),
        password=os.getenv("password")
    )
connection = get_db_connection()
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

class UserResponse(BaseModel):
    id: int
    status: str
    numero_cuenta: str

#Validar si la contraseña es la misma que la confirmación de la contraseña
@app.post("/register")
async def register_user(user: user):
    if user.password != user.confirm_password:
        raise HTTPException(status_code=400, detail="Las contraseñas no coinciden.")
    
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    
    connection = get_db_connection()
    cursor = connection.cursor()

    serie_fija = "123"  # Serie fija de 3 dígitos
    digitos_aleatorios = ''.join([str(random.randint(0, 9)) for _ in range(6)])  # 6 dígitos aleatorios
    numero_cuenta = serie_fija + digitos_aleatorios

    insert_sql = """
    INSERT INTO usuarios (full_name, email, password, dni, numero_cuenta) VALUES (%s, %s, %s, %s, %s)
    RETURNING id;
    """
    
    try:
        cursor.execute(insert_sql, (user.fullname, user.email,hashed_password, user.password, user.dni, numero_cuenta)) 
        user_id = cursor.fetchone()[0]
        connection.commit()
        return {"id": user_id, "status": "Usuario registrado exitosamente", "numero_cuenta": numero_cuenta}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        connection.close()
