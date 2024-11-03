from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import psycopg2
import bcrypt
import os
import random
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir cualquier origen
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permitir todas las cabeceras
)

# Conexión a la base de datos de Supabase
def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("HOST"),
        port=os.getenv("DBPORT"),
        dbname=os.getenv("DBNAME"),
        user=os.getenv("USER"),
        password=os.getenv("PASSWORD")
    )

# Crea la tabla al inicio
#en la variable de create_table_sql el rol siempre sera por predeterminado usuario y el is actived siempre sera predeterminado True
def create_table():
    connection = get_db_connection()
    cursor = connection.cursor()
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS usuarios (
        id SERIAL PRIMARY KEY,
        full_name TEXT NOT NULL,
        email varchar(250),
        password text,
        dni text,
        numero_cuenta text, 
        rol text, 
        is_actived boolean,
        cantidad_dinero int,
        created_at TIMESTAMPTZ DEFAULT NOW()
    );
    """
    cursor.execute(create_table_sql)
    connection.commit()
    cursor.close()
    connection.close()
    print("Tabla creada con éxito")

create_table()

class User(BaseModel):
    fullname: str
    email: str
    dni: str
    password: str
    confirm_password: str

class login(BaseModel):
    dni: str
    password: str

class transferencias(BaseModel):
    numero_cuenta: str
    cantidad_dinero: int

# Validar si la contraseña es la misma que la confirmación de la contraseña
@app.post("/register")
async def register_user(user: User):
    if user.password != user.confirm_password:
        raise HTTPException(status_code=400, detail="Las contraseñas no coinciden.")
    
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT email FROM usuarios WHERE email = %s", (user.email,))
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="El correo ya está registrado.")

    cursor.execute("SELECT dni FROM usuarios WHERE dni = %s", (user.dni,))
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="El DNI ya está registrado.")

    # Genera el número de cuenta aquí
    serie_fija = "009"  # Serie fija de 3 dígitos
    digitos_aleatorios = ''.join([str(random.randint(0, 9)) for _ in range(6)])  # 6 dígitos aleatorios
    numero_cuenta = serie_fija + digitos_aleatorios

    # Luego verifica si el número de cuenta ya existe
    cursor.execute("SELECT numero_cuenta FROM usuarios WHERE numero_cuenta = %s", (numero_cuenta,))
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="El número de cuenta ya está registrado.")

    insert_sql = """
    INSERT INTO usuarios (full_name, email, password, dni, numero_cuenta, rol, is_actived, cantidad_dinero) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;
    """
    
    try:
        cursor.execute(insert_sql, (user.fullname, user.email, hashed_password.decode('utf-8'), user.dni, numero_cuenta, "usuario", True, 0,))
        user_id = cursor.fetchone()[0]
        connection.commit()
        return {"id": user_id, "status": "Usuario registrado exitosamente", "numero_cuenta": numero_cuenta}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        connection.close()

@app.post("/login")
async def login_user(login: login):
    connection = get_db_connection()
    cursor = connection.cursor()

    # Selecciona tanto el id como la contraseña
    cursor.execute("SELECT id, password FROM usuarios WHERE dni = %s", (login.dni,))
    user_data = cursor.fetchone()

    if not user_data:
        raise HTTPException(status_code=400, detail="DNI o contraseña incorrectos.")

    user_id, stored_hashed_password = user_data

    if not bcrypt.checkpw(login.password.encode('utf-8'), stored_hashed_password.encode('utf-8')):
        raise HTTPException(status_code=400, detail="DNI o contraseña incorrectos.")

    return {"status": "Login exitoso", "user_id": user_id}

@app.post("/transferencias")
async def transfer_funds(transferencias: transferencias):
    connection = get_db_connection()
    cursor = connection.cursor()
    
    try:
        cursor.execute("SELECT id, numero_cuenta FROM usuarios WHERE numero_cuenta = %s", (transferencias.numero_cuenta,))
        user_data = cursor.fetchone()

        if not user_data:
            raise HTTPException(status_code=400, detail="Número de cuenta incorrecto.")

        # Actualiza la cantidad de dinero (ejemplo: sumando la cantidad transferida)
        cursor.execute("UPDATE usuarios SET cantidad_dinero = cantidad_dinero + %s WHERE numero_cuenta = %s", (transferencias.cantidad_dinero, transferencias.numero_cuenta,))
        connection.commit()

        return {"status": "Transferencia exitosa", "numero_cuenta": transferencias.numero_cuenta}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        connection.close()

import uvicorn
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT"))) 