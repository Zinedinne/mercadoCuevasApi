from datetime import datetime, time
from typing import Optional, Annotated, List
from pydantic import BaseModel, EmailStr, Field
from pydantic_extra_types.phone_numbers import PhoneNumber

class NombreCompleto(BaseModel):
    nombres: str
    apellidoPaterno: str
    apellidoMaterno: str

class Direccion(BaseModel):
    calle: str
    ciudad: str
    estado: str
    cPostal: str
    latitud: float
    longitud: float

class MetodoDePago(BaseModel):
    titular: str
    nTarjeta: str
    emisor: str
    anioVencimiento: str
    mesVencimiento: str

class Consumidor(BaseModel):
    nombreCompleto: NombreCompleto
    nCelular: PhoneNumber
    fechaNacimiento: datetime
    password: Annotated[str, Field(exclude=True)]
    direccion: Optional[List[Direccion]] = None
    metodoDePago: Optional[List[MetodoDePago]] = None

class ModConsumidor(BaseModel):
    nombreCompleto: Optional[NombreCompleto] = None
    nCelular: Optional[PhoneNumber] = None
    fechaNacimiento: Optional[datetime] = None
    password: Optional[Annotated[str, Field(exclude=True)]] = None

class Empleado(BaseModel):
    nombreCompleto: NombreCompleto 
    cargo: str
    fechaIngreso: datetime
    usuario: str
    password: str 
    sucursal: str

class ModEmpleado(BaseModel):
    nombreCompleto: Optional[NombreCompleto] = None
    cargo: Optional[str] = None
    fechaIngreso: Optional[datetime] = None
    usuario: Optional[str] = None
    password: Optional[Annotated[str, Field(exclude=True)]] = None
    sucursal: Optional[str] = None

class Cantidad(BaseModel):
    cantidad: int
    idSucursal: str

class CatalogoProductos(BaseModel):
    cBarras: str
    nombre: str 
    descripcion: str
    categoria: str 
    dirFotos: List[str]
    precio: float
    cantidad: List[Cantidad]

class CatalogoProductosMod(BaseModel):
    cBarras: Optional[str] = None
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    categoria: Optional[str] = None
    dirFotos: Optional[List[str]] = None
    precio: Optional[float] = None
    cantidad: Optional[List[Cantidad]] = None

class Incidencia(BaseModel):
    titulo: str
    descripcion: str
    dirFoto:str

class MotivoDeNoEntrega(BaseModel):
    titulo: str
    descripcion: str

class Pedido(BaseModel):
    estado: str = "En carrito"
    fechaRealizacion: datetime
    tiempoEstimado: str
    incidencia: Optional[Incidencia] = None
    motivoDeNoEntrega:  Optional[MotivoDeNoEntrega] = None
    idConsumidor: Optional[str] = None
    consumidor: Optional[dict] = None
    productos: List[dict]
    repartidor: Optional[dict] = None
    sucursal: dict

# modificacion de pedido por parte de usuario
class ModPedidoUsuario(BaseModel):
    estado: Optional[str] = None
    fechaRealizacion: Optional[datetime] = None
    productos: Optional[List[dict]] = None

# Modificacion de pedido por parte de repartidores 
class ModPedidoRepartidor(BaseModel):
    estado: Optional[str] = None
    motivoDeNoEntrega: Optional[MotivoDeNoEntrega] = None

class RepartidorPedido(BaseModel):
    id: str
    nombreCompleto: NombreCompleto
class ModPedidoEjecutivo(BaseModel):
    estado: str
    idRepartidor: str
    repartidor: RepartidorPedido 

class Horario(BaseModel):
    apertura: str 
    cierre: str 

class Sucursal(BaseModel):
    direccion: Direccion
    nombreComercial: str
    horario: Horario

class ModSucursal(BaseModel):
    direccion: Optional[Direccion] = None
    nombreComercial: Optional[str] = None
    horario: Optional[Horario] = None

class ConsumidorModelAuth(Consumidor):
    id: Optional[str] = Field(alias="_id")

class EmpleadoModelAuth(Empleado):
    id: Optional[str] = Field(alias="_id")

class SucursalModelAuth(Sucursal):
    id: Optional[str] = Field(alias="_id")
