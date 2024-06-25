from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext
import mercado_cuevas_api.auth.auth_database as au_db
import mercado_cuevas_api.config as cf
import mercado_cuevas_api.constants.response_constants as rcodes
import mercado_cuevas_api.auth.models as auth_models
import mercado_cuevas_api.auth.auth_database as auth_database
import mercado_cuevas_api.auth.auth_operations as auth_operations

SECRET_KEY = cf.SECRET_KEY_AUTH
ALGORITHM = cf.AUTH_ALGORITH
ACCESS_TOKEN_EXPIRE_MINUTES = 86400

oauth2_scheme_employee = OAuth2PasswordBearer(tokenUrl="/token_empleado")
oauth2_scheme_consumer = OAuth2PasswordBearer(tokenUrl="/token_consumidor")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def get_current_consumer(token: Annotated[str, Depends(oauth2_scheme_consumer)]):
    credentials_exception = HTTPException(
        status_code=rcodes.UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, cf.SECRET_KEY_AUTH, algorithms=[cf.AUTH_ALGORITH])
        username: str = payload.get("nCelular")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = auth_database.get_consumer(username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_employee(token: Annotated[str, Depends(oauth2_scheme_employee)]):
    credentials_exception = HTTPException(
        status_code=rcodes.UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, cf.SECRET_KEY_AUTH, algorithms=[cf.AUTH_ALGORITH])
        username: str = payload.get("usuario")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = auth_database.get_employee(username)
    if user is None:
        raise credentials_exception
    return user

async def check_if_user_is_auth(user_id, token):
    try:
        user = await get_current_consumer(token)
        return user.id == user_id
    except Exception:
        return False

async def check_if_employee_is_auth(user_id, token):
    try:
        user = await get_current_employee(token)
        return user.id == user_id
    except Exception:
        return False

def check_employee_privilige(token):
    credentials_exception = HTTPException(
        status_code=rcodes.UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, cf.SECRET_KEY_AUTH, algorithms=[cf.AUTH_ALGORITH])
        cargo: str = payload.get("cargo")
        print(cargo)
        if cargo is None:
            raise credentials_exception
        else:
            return cargo
    except JWTError:
        raise credentials_exception

def verify_password(plain_password, hashed_password):
    print(plain_password)
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_consumer(phoneNumber: str, password: str):
    user = au_db.get_consumer(phoneNumber)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user

def authenticate_employee(username: str, password: str):
    user = au_db.get_employee(username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


