from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
import mercado_cuevas_api.documentdb.schemas as models
from pydantic_extra_types.phone_numbers import PhoneNumber


class ConsumidorModelChecker(BaseModel):
    #TODO cambiar campos
    Nombre: str
    ApellidoPaterno: str
    ApellidoMaterno: str
    Email: EmailStr
    UrlImagen: str
    PerfilPublico: bool
    Guia: bool
    Telefono: PhoneNumber
    Bitacoras: Optional[List[str]]

class EmpleadoModelChecker(BaseModel):
    #TODO cambiar campos
    Nombre: str
    ApellidoPaterno: str
    ApellidoMaterno: str
    Email: EmailStr
    UrlImagen: str
    PerfilPublico: bool
    Guia: bool
    Telefono: PhoneNumber
    Bitacoras: Optional[List[str]]

class ConsumidorModel(ConsumidorModelChecker):
    id: Optional[str] = Field(alias="_id")

class EmpleadoModel(EmpleadoModelChecker):
    id: Optional[str] = Field(alias="_id")

