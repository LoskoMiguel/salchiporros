from jose import JWTError, jwt
import datetime
from fastapi import  HTTPException
from dotenv import load_dotenv
import os

load_dotenv()

# Variables de entorno para el token
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

# funcion para crear el token
def create_jwt_token(user_id: int):
    payload = {
        'user_id': user_id, # ID del usuario sacado de la base de datos
        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24)  # Expiración del token
    }
    # Codificar el payload y devolver el token
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    print(token)
    return token


# funcion para decodificar el token y obtener el payload
#el payload es el contenido del token
def decode_jwt_token(token: str):
    try:
        # Decodificar el token y obtener el payload
        decoded_payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return decoded_payload
    except JWTError as e:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
