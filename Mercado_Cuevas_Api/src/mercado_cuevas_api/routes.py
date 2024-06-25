import json
from datetime import datetime, timedelta
from fastapi import FastAPI, File, Form, UploadFile, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from datetime import datetime
from typing import List, Annotated
from mercado_cuevas_api.constants import response_constants as rcodes
from mercado_cuevas_api.schemas.responses import (
#     HealthCheckResponse,
#     VersionResponse,
#     EquipoNecesarioResponse,
#     PuntosInteresResponse,
#     UsuariosResponse,
#     ExploracionesResponse,
    StatusResponse,
#     BestRoutesResponse,
#     UserRoutesResponse,
#     CreatedObjectResponse,
#     ComentaryResponse,
#     UsersResponse,
#     ExplorationUserResponse,
)
from mercado_cuevas_api.schemas import errors, models
import mercado_cuevas_api.config as cf
import mercado_cuevas_api.documentdb.document_operations as dop
import mercado_cuevas_api.documentdb.schemas as sh
import mercado_cuevas_api.documentdb.document as d
from pydantic import ValidationError
# from eco_explore_api.storage.google_storage import gstorage
# import eco_explore_api.grcp.proto_operations as eco_grpc
import mercado_cuevas_api.auth.models as auth_models
import mercado_cuevas_api.auth.auth_operations as auth_operations
from google.oauth2 import service_account
from google.cloud import storage

credentials = service_account.Credentials.from_service_account_file(
    './mercado_cuevas_api/cred.json'
)
client = storage.Client(credentials=credentials)
bucket = client.bucket(cf.BUCKET_NAME)

app = FastAPI()
#Endpoint Consumidores
@app.post("/token_consumidor", response_model=auth_models.Token, tags=["Consumidores"])
async def login_consumer_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = auth_operations.authenticate_consumer(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=rcodes.UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(
        minutes=auth_operations.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    access_token = auth_operations.create_access_token(
        data={"nCelular": user.nCelular}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post(
    "/consumidores",
    response_model=StatusResponse,
    tags=["Consumidores"],
)
async def sign_in_consumer(consumidor: sh.Consumidor):
    try:
        # json_data = json.load(json_data)
        if dop.create_consumer(consumidor):
            respuesta = StatusResponse(ok=True, detail="Consumidor Creado")
            return JSONResponse(
                status_code=rcodes.CREATED,
                content=jsonable_encoder(respuesta.model_dump()),
            )
        else:
            res = StatusResponse(ok=False, detail="El consumidor ya existe")
            return JSONResponse(
                status_code=rcodes.CONFLICT,
                content=jsonable_encoder(res.model_dump()),
            )
    except ValidationError as exc:
        error = errors.Error(error=str(exc.errors()[0]), detail=None)
        return JSONResponse(
            status_code=rcodes.BAD_REQUEST, content=jsonable_encoder(error.model_dump())
        )

@app.put(
    "/consumidores/{user_id}",
    response_model=StatusResponse,
    tags=["Consumidores"],
)
async def update_consumer(
    user_id: str, mod_consumer: sh.ModConsumidor, token: dict = Depends(auth_operations.oauth2_scheme_consumer)
):
    if await auth_operations.check_if_user_is_auth(user_id, token):
        code, response = dop.update_consumer(user_id, mod_consumer)
        return JSONResponse(
            status_code=code, content=jsonable_encoder(response.model_dump())
        )
    else:
        errorResponse = errors.Error(
            error="No tienes permiso para realizar esta accion", detail=None
        )
        return JSONResponse(
            status_code=rcodes.UNAUTHORIZED,
            content=jsonable_encoder(errorResponse.model_dump()),
        )

@app.delete(
    "consumidores/{user_id}/metodo_pago/{num_tarjeta}", 
    response_model=StatusResponse, 
    tags=["Consumidores"]
)
async def delete_payment_method(
    user_id: str, num_tarjeta: str, token: dict = Depends(auth_operations.oauth2_scheme_consumer)
):
    if await auth_operations.check_if_user_is_auth(user_id, token):
        code, response = dop.delete_payment_method(user_id, num_tarjeta)
        return JSONResponse(
            status_code=code, content=jsonable_encoder(response.model_dump())
        )
    else:
        errorResponse = errors.Error(
            error="No tienes permiso para realizar esta accion", detail=None
        )
        return JSONResponse(
            status_code=rcodes.UNAUTHORIZED,
            content=jsonable_encoder(errorResponse.model_dump()),
        )

@app.put(
    "/consumidores/{user_id}/metodo_pago",
    response_model=StatusResponse,
    tags=["Consumidores"],
)
async def update_payment_method(
    user_id: str, payment_method: sh.MetodoDePago, token: dict = Depends(auth_operations.oauth2_scheme_consumer)
):
    if await auth_operations.check_if_user_is_auth(user_id, token):
        code, response = dop.update_payment_method(user_id, payment_method)
        return JSONResponse(
            status_code=code, content=jsonable_encoder(response.model_dump())
        )
    else:
        errorResponse = errors.Error(
            error="No tienes permiso para realizar esta accion", detail=None
        )
        return JSONResponse(
            status_code=rcodes.UNAUTHORIZED,
            content=jsonable_encoder(errorResponse.model_dump()),
        )

@app.delete("/consumidores/{user_id}", response_model=StatusResponse, tags=["Consumidores"])
async def delete_consumer(
    user_id: str,  token: dict = Depends(auth_operations.oauth2_scheme_consumer)
):
    if await auth_operations.check_if_user_is_auth(user_id, token):
        code, response = dop.delete_consumer(user_id)
        return JSONResponse(
            status_code=code, content=jsonable_encoder(response.model_dump())
        )
    else:
        errorResponse = errors.Error(
            error="No tienes permiso para realizar esta acción", detail=None
        )
        return JSONResponse(
            status_code=rcodes.UNAUTHORIZED,
            content=jsonable_encoder(errorResponse.model_dump()),
        )

#endpoints empleados
@app.post("/token_empleado", response_model=auth_models.Token, tags=["Empleados"])
async def login_employee_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = auth_operations.authenticate_employee(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=rcodes.UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(
        minutes=auth_operations.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    access_token = auth_operations.create_access_token(
        data={"usuario": user.usuario, "cargo": user.cargo}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/empleados", tags=["Empleados"])
async def sign_in_employee(
    empleado: sh.Empleado, employee_id: str, token: dict = Depends(auth_operations.oauth2_scheme_employee)
):
    try:
        # json_data = json.load(json_data)
        if await auth_operations.check_if_employee_is_auth(employee_id, token) and auth_operations.check_employee_privilige(token) == "Administrador":
            if dop.create_employee(empleado):
                respuesta = StatusResponse(ok=True, detail="Empleado Creado")
                return JSONResponse(
                    status_code=rcodes.CREATED,
                    content=jsonable_encoder(respuesta.model_dump()),
                )
            else:
                res = StatusResponse(ok=False, detail="El empleado ya existe")
                return JSONResponse(
                    status_code=rcodes.CONFLICT,
                    content=jsonable_encoder(res.model_dump()),
                )
    except ValidationError as exc:
        error = errors.Error(error=str(exc.errors()[0]), detail=None)
        return JSONResponse(
            status_code=rcodes.BAD_REQUEST, content=jsonable_encoder(error.model_dump())
        )

@app.put(
    "/empleados/{employee_id}",
    response_model=StatusResponse,
    tags=["Empleados"],
)
async def update_Employee(
    user_id: str, employee_id: str, mod_employee: sh.ModEmpleado, token: dict = Depends(auth_operations.oauth2_scheme_employee)
):
    if await auth_operations.check_if_employee_is_auth(user_id, token) and auth_operations.check_employee_privilige(token) == "Administrador":
        code, response = dop.update_employee(employee_id, mod_employee)
        return JSONResponse(
            status_code=code, content=jsonable_encoder(response.model_dump())
        )
    else:
        errorResponse = errors.Error(
            error="No tienes permiso para realizar esta accion", detail=None
        )
        return JSONResponse(
            status_code=rcodes.UNAUTHORIZED,
            content=jsonable_encoder(errorResponse.model_dump()),
        )

@app.delete("/empleados/{employee_id}", response_model=StatusResponse, tags=["Empleados"])
async def delete_employee(
    user_id: str,  employee_id: str,token: dict = Depends(auth_operations.oauth2_scheme_consumer)
):
    if await auth_operations.check_if_employee_is_auth(user_id, token) and auth_operations.check_employee_privilige(token) == "Administrador":
        code, response = dop.delete_employee(employee_id)
        return JSONResponse(
            status_code=code, content=jsonable_encoder(response.model_dump())
        )
    else:
        errorResponse = errors.Error(
            error="No tienes permiso para realizar esta acción", detail=None
        )
        return JSONResponse(
            status_code=rcodes.UNAUTHORIZED,
            content=jsonable_encoder(errorResponse.model_dump()),
        )

#endpoints sucursales
@app.get("/sucursales", response_model=List[sh.SucursalModelAuth], tags=["Sucursales"])
async def get_sucursales():
    branches = dop.get_branches()
    return branches

@app.get("/sucursales/{id_sucursal}", response_model=sh.SucursalModelAuth, tags=["Sucursales"])
async def get_sucursal(id_sucursal: str):
    branch = dop.get_branch(id_sucursal)
    return branch

@app.post("/sucursales", response_model=StatusResponse, tags=["Sucursales"])
async def create_branch(
    user_id: str, new_branch: sh.Sucursal, token: dict = Depends(auth_operations.oauth2_scheme_employee)
):
    if await auth_operations.check_if_employee_is_auth(user_id, token) and auth_operations.check_employee_privilige(token) == "Administrador":
        dop.create_branch(new_branch)
        respuesta = StatusResponse(ok=True, detail="La sucursal ha sido creada")
        return JSONResponse(
            status_code=rcodes.CREATED,
            content=jsonable_encoder(respuesta.model_dump()),
        )
    else:
        respuesta = StatusResponse(ok=False, detail="Usuario sin privilegios")
        return JSONResponse(
            status_code=rcodes.UNAUTHORIZED,
            content=jsonable_encoder(respuesta)
        )

#TODO hacer validaciones
@app.put("/sucursales/{id_sucursal}", tags=["Sucursales"])
async def modify_branch(
    user_id: str, id_sucursal: str, modified_branch: sh.ModSucursal, token: dict = Depends(auth_operations.oauth2_scheme_employee)
):
    if await auth_operations.check_if_employee_is_auth(user_id, token) and auth_operations.check_employee_privilige(token) == "Administrador":
        code, response = dop.update_branch(id_sucursal, modified_branch)
        return JSONResponse(
            status_code=code, content=jsonable_encoder(response.model_dump())
        )
    else:
        errorResponse = errors.Error(
            error="No tienes el permiso para realizar esta acción", detail=None
        )
        return JSONResponse(
            status_code=rcodes.UNAUTHORIZED,
            content=jsonable_encoder(errorResponse.model_dump()),
        )

@app.delete("/sucursales/{id_sucursal}", response_model=StatusResponse, tags=["Sucursales"])
async def delete_branch(
    user_id: str, id_sucursal: str, token:dict = Depends(auth_operations.oauth2_scheme_employee)
):
    if await auth_operations.check_if_employee_is_auth(user_id, token) and auth_operations.check_employee_privilige(token) =="Administrador":
        code, response = dop.delete_branch(id_sucursal)
        return JSONResponse(
            status_code=code, content=jsonable_encoder(response.model_dump())
        )
    else:
        errorResponse = errors.Error(
            error="No tienes el permiso para realizar esta acción", detail="Error de privilegios"
        )
        return JSONResponse(
            status_code=rcodes.UNAUTHORIZED,
            content=jsonable_encoder(errorResponse.model_dump())
        )

@app.get("/consumidores/{user_id}/pedidos", response_model=List[sh.Pedido], tags=["Pedidos"])
async def get_orders(user_id: str, token: dict = Depends(auth_operations.oauth2_scheme_consumer)):
    if await auth_operations.check_if_user_is_auth(user_id, token):
        orders = dop.get_orders_by_consumer(user_id)
        return orders
    else:
        errorResponse = errors.Error(
            error="No tienes el permiso para realizar esta acción", detail=None
        )
        return JSONResponse(
            status_code=rcodes.UNAUTHORIZED,
            content=jsonable_encoder(errorResponse.model_dump()),
        )

@app.post("/consumidores/pedidos/", response_model=StatusResponse, tags=["Pedidos"])
async def create_order(
    consumer_id: str, order :sh.Pedido,token:dict = Depends(auth_operations.oauth2_scheme_consumer)
):
    if await auth_operations.check_if_user_is_auth(consumer_id, token):
        if not dop.user_has_active_cart(consumer_id):
            dop.create_order(consumer_id,order)
            respuesta = StatusResponse(ok=True, detail="El pedido ha sido creado")
            return JSONResponse(
                status_code=rcodes.CREATED,
                content=jsonable_encoder(respuesta.model_dump()),
            )
        else:
            respuesta = StatusResponse(ok = False, detail= "El consumidor ya cuenta co un pedido en carrito")
            return JSONResponse(
                status_code=rcodes.NOT_ACEPTABLE,
                content=jsonable_encoder(respuesta)
            )
    else:
        respuesta = StatusResponse(ok=False, detail="El consumidor no se encuentra autentificado")
        return JSONResponse(
            status_code=rcodes.UNAUTHORIZED,
            content=jsonable_encoder(respuesta)
        )

# edicion de pedidos antes de meterse en pedido
# un pedido solamente puede ser editado cuando esta en carrito
@app.put("/consumidores/pedidos/{id_pedido}", response_model=StatusResponse, tags=["Pedidos"])
async def edit_order(
    consumer_id: str, id_pedido: str, modified_order: sh.ModPedidoUsuario, token: dict = Depends(auth_operations.oauth2_scheme_consumer)
):
    if await auth_operations.check_if_user_is_auth(consumer_id, token):
        if dop.check_if_is_consumer_order(consumer_id, id_pedido):
            if dop.check_order_status(id_pedido) == "En carrito":
                code, response = dop.edit_order_consumer(id_pedido ,modified_order)
                return JSONResponse(
                    status_code=code, content=jsonable_encoder(response.model_dump())
                )
            else:
                respuesta = StatusResponse(ok=False, detail="El pedido no se encuentra en carrito")
                return JSONResponse(
                    status_code=rcodes.UNAUTHORIZED,
                    content=jsonable_encoder(respuesta)
                )
        else:
            respuesta = StatusResponse(ok=False, detail="El pedido no pertenece al consumidor")
            return JSONResponse(
                status_code=rcodes.UNAUTHORIZED,
                content=jsonable_encoder(respuesta)
            )
    else:
        errorResponse = errors.Error(
            error="No tienes el permiso para realizar esta acción", detail=None
        )
        return JSONResponse(
            status_code=rcodes.UNAUTHORIZED,
            content=jsonable_encoder(errorResponse.model_dump()),
        )

@app.put("/consumidores/pedidos/{id_pedido}/incidencia", response_model=StatusResponse, tags=["Pedidos"])
async def add_incidence_to_order(
    consumer_id: str, id_pedido: str, incidencia: sh.Incidencia, token: dict = Depends(auth_operations.oauth2_scheme_consumer)
):
    if await auth_operations.check_if_user_is_auth(consumer_id, token):
        if dop.check_if_is_consumer_order(consumer_id, id_pedido):
            if dop.check_order_status (id_pedido) == "Entregado":
                code, response = dop.add_incidence_to_order(id_pedido, incidencia)
                return JSONResponse(
                    status_code=code, content=jsonable_encoder(response.model_dump())
                )
            else:
                respuesta = StatusResponse(ok=False, detail="El pedido no se encuentra en carrito")
                return JSONResponse(
                    status_code=rcodes.UNAUTHORIZED,
                    content=jsonable_encoder(respuesta)
                )
        else:
            respuesta = StatusResponse(ok=False, detail="El pedido no pertenece al consumidor")
            return JSONResponse(
                status_code=rcodes.UNAUTHORIZED,
                content=jsonable_encoder(respuesta)
            )
    else:
        errorResponse = errors.Error(
            error="No tienes el permiso para realizar esta acción", detail=None
        )
        return JSONResponse(
            status_code=rcodes.UNAUTHORIZED,
            content=jsonable_encoder(errorResponse.model_dump()),
        )

@app.delete("/consumidores/pedidos/{id_pedido}", response_model=StatusResponse, tags=["Pedidos"])
async def cancel_order(
    consumer_id: str, id_pedido: str, token: dict = Depends(auth_operations.oauth2_scheme_consumer)
):
    if await auth_operations.check_if_user_is_auth(consumer_id, token):
        if dop.check_if_is_consumer_order(consumer_id, id_pedido):
            if dop.check_order_status(id_pedido) == "En validación":
                code, response = dop.cancel_order(id_pedido)
                return JSONResponse(
                    status_code=code, content=jsonable_encoder(response.model_dump())
                )
            else:
                respuesta = StatusResponse(ok=False, detail="El pedido no se encuentra en validación")
                return JSONResponse(
                    status_code=rcodes.UNAUTHORIZED,
                    content=jsonable_encoder(respuesta)
                )
        else:
            respuesta = StatusResponse(ok=False, detail="El pedido no pertenece al consumidor")
            return JSONResponse(
                status_code=rcodes.UNAUTHORIZED,
                content=jsonable_encoder(respuesta)
            )
    else:
        errorResponse = errors.Error(
            error="No tienes el permiso para realizar esta acción", detail=None
        )
        return JSONResponse(
            status_code=rcodes.UNAUTHORIZED,
            content=jsonable_encoder(errorResponse.model_dump()),
        )
#TODO
#Ruta de empleado con el id de pedido para edicion de estado
@app.put("/repartidores/pedidos/{id_pedido}", response_model=StatusResponse, tags=["Pedidos"])
async def edit_order_delivery(
    employee_id: str, id_pedido: str, modified_order: sh.ModPedidoRepartidor, token: dict = Depends(auth_operations.oauth2_scheme_employee)
):
    if await auth_operations.check_if_employee_is_auth(employee_id, token):
        if auth_operations.check_employee_privilige(token) == "Repartidor":
            if dop.check_if_is_employee_order(employee_id, id_pedido):
                code, response = dop.edit_order_delivery(id_pedido, modified_order)
                return JSONResponse(
                    status_code=code, content=jsonable_encoder(response.model_dump())
                )
            else:
                respuesta = StatusResponse(ok=False, detail="El pedido no pertenece al repartidor")
                return JSONResponse(
                    status_code=rcodes.UNAUTHORIZED,
                    content=jsonable_encoder(respuesta)
                )            
        else:
            respuesta = StatusResponse(ok=False, detail="El empleado no es repartidor")
            return JSONResponse(
                status_code=rcodes.UNAUTHORIZED,
                content=jsonable_encoder(respuesta)
            )
    else:
        errorResponse = errors.Error(
            error="No tienes el permiso para realizar esta acción", detail=None
        )
        return JSONResponse(
            status_code=rcodes.UNAUTHORIZED,
            content=jsonable_encoder(errorResponse.model_dump()),
        )

@app.put("/pedidos/{id_pedido}", response_model=StatusResponse, tags=["Pedidos"])
async def edit_order_executive(
    admin_id : str, id_pedido: str, modified_order: sh.ModPedidoEjecutivo, token: dict = Depends(auth_operations.oauth2_scheme_employee)
):
    if await auth_operations.check_if_employee_is_auth(admin_id, token):
        if auth_operations.check_employee_privilige(token) == "Ejecutivo de ventas":
            code, response = dop.edit_order_executive(id_pedido, modified_order)
            return JSONResponse(
                status_code=code, content=jsonable_encoder(response.model_dump())
            )
        else:
            respuesta = StatusResponse(ok=False, detail="El empleado no es administrador")
            return JSONResponse(
                status_code=rcodes.UNAUTHORIZED,
                content=jsonable_encoder(respuesta)
            )

@app.get("/productos/{id_sucursal}", response_model=List[sh.CatalogoProductos], tags=["Productos"])
async def get_products(id_sucursal: str):
    products = dop.get_products(id_sucursal)
    return products

#get productos por sucursal y por busqueda
@app.get("/productos/{id_sucursal}/", response_model=List[sh.CatalogoProductos], tags=["Productos"])
async def get_products_by_query(id_sucursal: str, skip: int = 0, limit: int = 0, categoria: str | None = None, nombre: str | None = None, precio: float | None = None, cBarras: str | None = None):
    products = dop.get_products_by_query(id_sucursal,  categoria, nombre, precio, cBarras)
    return products

@app.post("/productos/{id_sucursal}", response_model=StatusResponse, tags=["Productos"])
async def create_product(
    user_id: str, id_sucursal: str, product: sh.CatalogoProductos, token: dict = Depends(auth_operations.oauth2_scheme_employee)
):
    if await auth_operations.check_if_employee_is_auth(user_id, token) and auth_operations.check_employee_privilige(token) == "Administrador":
        dop.create_product(id_sucursal, product)
        respuesta = StatusResponse(ok=True, detail="El producto ha sido creado")
        return JSONResponse(
            status_code=rcodes.CREATED,
            content=jsonable_encoder(respuesta.model_dump()),
        )
    else:
        respuesta = StatusResponse(ok=False, detail="Usuario sin privilegios")
        return JSONResponse(
            status_code=rcodes.UNAUTHORIZED,
            content=jsonable_encoder(respuesta)
        )

@app.put("/productos/{id_sucursal}/{id_producto}", response_model=StatusResponse, tags=["Productos"])
async def modify_product(
    user_id: str, id_producto: str, modified_product: sh.CatalogoProductosMod, token: dict = Depends(auth_operations.oauth2_scheme_employee)
):
    if await auth_operations.check_if_employee_is_auth(user_id, token) and auth_operations.check_employee_privilige(token) == "Administrador":
        code, response = dop.update_product(id_producto, modified_product)
        return JSONResponse(
            status_code=code, content=jsonable_encoder(response.model_dump())
        )
    else:
        errorResponse = errors.Error(
            error="No tienes el permiso para realizar esta acción", detail=None
        )
        return JSONResponse(
            status_code=rcodes.UNAUTHORIZED,
            content=jsonable_encoder(errorResponse.model_dump()),
        )

@app.delete("/productos/{id_producto}", response_model=StatusResponse, tags=["Productos"])
async def delete_product(
    user_id: str, id_producto: str, token: dict = Depends(auth_operations.oauth2_scheme_employee)
):
    if await auth_operations.check_if_employee_is_auth(user_id, token) and auth_operations.check_employee_privilige(token) == "Administrador":
        code, response = dop.delete_product(id_producto)
        return JSONResponse(
            status_code=code, content=jsonable_encoder(response.model_dump())
        )
    else:
        errorResponse = errors.Error(
            error="No tienes el permiso para realizar esta acción", detail=None
        )
        return JSONResponse(
            status_code=rcodes.UNAUTHORIZED,
            content=jsonable_encoder(errorResponse.model_dump()),
        )

@app.post("/upload-image/" ,tags=["prueba"])
async def upload_image(file: UploadFile = File(...)):
    try:
        blob = bucket.blob(file.filename)
        blob.upload_from_file(file.file, content_type=file.content_type)
        blob.make_public()
        return {"url": blob.public_url}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/image/{image_name}")
async def get_image(image_name: str):
    try:
        blob = bucket.blob(image_name)
        if not blob.exists():
            raise HTTPException(status_code=404, detail="Image not found")
        return {"url": blob.public_url}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

#@app.get("/health", response_model=HealthCheckResponse)
#async def health(saludo):
#    response = HealthCheckResponse(message="Adios {}".format(saludo))
#    return JSONResponse(status_code=rcodes.OK, content=jsonable_encoder(response))
#
#
#@app.get("/status")
#async def statue(token: dict = Depends(auth_operations.oauth2_scheme)):
#    time = datetime.now()
#    return JSONResponse(
#        status_code=rcodes.OK,
#        content=jsonable_encoder(
#            VersionResponse(version=1.0, detail=(HealthCheckResponse(time=time)))
#        ),
#    )

#
#@app.post(
#    "/usuarios/{user_id}/actualizar/foto",
#    response_model=StatusResponse,
#    tags=["Usuarios"],
#)
#async def update_profile_photo(
#    user_id: str,
#    file: UploadFile,
#    token: Annotated[str, Depends(auth_operations.oauth2_scheme)],
#):
#    if await auth_operations.check_if_user_is_auth(user_id, token):
#        code, response = await dc.update_profile_photo(user_id, file)
#        return JSONResponse(
#            status_code=code, content=jsonable_encoder(response.model_dump())
#        )
#    else:
#        errorResponse = errors.Error(
#            error="No tienes permiso para realizar esta accion", detail=None
#        )
#        return JSONResponse(
#            status_code=rcodes.UNAUTHORIZED,
#            content=jsonable_encoder(errorResponse.model_dump()),
#        )
#
#
#@app.get(
#    "/usuarios/buscar/{email}",
#    response_model=UsersResponse,
#    tags=["Usuarios"],
#)
#async def search_users_by_email(email: str):
#    """
#    Endpoint to search a list of users that match with the email
#    """
#    code, response = dc.find_users_by_email(email)
#    return JSONResponse(
#        status_code=code, content=jsonable_encoder(response.model_dump())
#    )


#@app.post("/files/{id1}/{id2}")
#async def create_file(
#    # file: Annotated[bytes, File()],
#    id1: str,
#    id2: str,
#    fileb: Annotated[UploadFile, File()],
#    token: Annotated[str, dict],
#):
#    token = json.loads(token)
#    return {
#        "id1": id1,
#        "id2": id2,
#        "token": token,
#        "fileb_content_type": fileb.content_type,
#    }
#
