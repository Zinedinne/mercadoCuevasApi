import bson
from datetime import datetime
from fastapi import UploadFile
from pydantic import EmailStr
import bson.json_util as json_util
from pymongo import DESCENDING
import mercado_cuevas_api.config as cf
import mercado_cuevas_api.documentdb.payments as payments
from mercado_cuevas_api.schemas import errors
import mercado_cuevas_api.documentdb.schemas as schemas
import mercado_cuevas_api.schemas.models as models
from mercado_cuevas_api.documentdb.document import Collections
import mercado_cuevas_api.constants.response_constants as rcodes
from mercado_cuevas_api.schemas.responses import (
#    BestRoutesResponse,
#    UserRoutesResponse,
#    ExploracionesResponse,
#    CreatedObjectResponse,
    CreatedObjectResponse,
    StatusResponse,
#    GoogleStorageResponse,
#    UsersResponse,
)
#from eco_explore_api.storage.google_storage import gstorage
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def serialize_id(uid: str):
    return bson.ObjectId(uid)

def transform_id_object(obj: dict):
    for element in obj:
        curr = obj[element]
        if isinstance(curr, list):
            sub_curr = []
            for c in curr:
                if bson.ObjectId.is_valid(c):
                    sub_curr.append(str(c))
                else:
                    sub_curr.append(c)
            obj[element] = sub_curr
        elif bson.ObjectId.is_valid(curr):
            obj[element] = str(curr)
    return obj

def consumer_exists(user_id: bson.ObjectId):
    if isinstance(user_id, str):
        user_id = serialize_id(user_id)
    cls = Collections().get_collection(cf.CONSUMERS_COLLECTION)
    usr_search = {"_id": user_id}
    ans = cls.find_one(filter=usr_search)
    return bool(ans)

def employee_exists(user_id: bson.ObjectId):
    if isinstance(user_id, str):
        user_id = serialize_id(user_id)
    cls = Collections().get_collection(cf.EMPLOYEES_COLLECTION)
    usr_search = {"_id": user_id}
    ans = cls.find_one(filter=usr_search)
    return bool(ans)

def branch_exists(branch_id: bson.ObjectId):
    if isinstance(branch_id, str):
        branch_id = serialize_id(branch_id)
    cls = Collections().get_collection(cf.BRANCHES_COLLECTION)
    branch_search = {"_id": branch_id}
    ans = cls.find_one(filter=branch_search)
    return bool(ans)

def get_consumer(user_id: bson.ObjectId):
    if isinstance(user_id, str):
        user_id = serialize_id(user_id)
    cls = Collections().get_collection(cf.CONSUMERS_COLLECTION)
    usr_search = {"_id": user_id}
    ans = cls.find_one(filter=usr_search)
    return ans

def create_consumer(consumidor: schemas.Consumidor):
    cls = Collections().get_collection(cf.CONSUMERS_COLLECTION)
    ans = cls.find_one({"nCelular": consumidor.nCelular})
    if not ans:
        save = consumidor.password
        consumidor = consumidor.model_dump()
        consumidor["password"] = pwd_context.hash(save)
        ans = cls.insert_one(consumidor)
        return ans.acknowledged
    return False

def delete_consumer(user_id: str):
    errorResponse = errors.Error(error="", detail=None)
    if consumer_exists(user_id):
        try: 
            user_id = serialize_id(user_id)
            cls= Collections().get_collection(cf.CONSUMERS_COLLECTION)
            result = cls.delete_one({"_id": user_id})
            print(result)
            if result:
                return [
                    rcodes.OK,
                    StatusResponse(ok=True, detail=(f"Consumidor con el ID {user_id} eliminado correctamente")),
                ]
            else:
                errorResponse.error = "No se Elimino el consumidor"
                return [rcodes.NOT_FOUND, errorResponse]
        except Exception as e:
            errorResponse.error = "Ocurrio un error al actualizar la informacion"
            errorResponse.detail = str(e)
            return [rcodes.CONFLICT, errorResponse]

def update_consumer(user_id: str, updated_user: schemas.ModConsumidor):
    errorResponse = errors.Error(error="", detail=None)
    try:
        cls = Collections().get_collection(cf.CONSUMERS_COLLECTION)
        user_id = serialize_id(user_id)
        if consumer_exists(user_id):
            try:
                ans = cls.update_one(
                    {"_id": user_id}, {"$set": updated_user.model_dump(exclude_unset=True)}
                )
                if ans:
                    return [
                        rcodes.CREATED,
                        StatusResponse(ok=True, detail="Informacion Actualizada"),
                    ]
                else:
                    errorResponse.error = "No se modifico la informacion"
                    return [rcodes.NOT_FOUND, errorResponse]
            except Exception as e:
                errorResponse.error = "Ocurrio un error al actualizar la informacion"
                errorResponse.detail = str(e)
                return [rcodes.CONFLICT, errorResponse]
        else:
            errorResponse.error = "El usuario no existe"
            return [rcodes.NOT_FOUND, errorResponse]
    except Exception as e:
        errorResponse.error = "Objeto Invalido"
        errorResponse.detail = str(e)
        return [rcodes.BAD_REQUEST, errorResponse]

def add_payment_method(user_id: str, payment_method: schemas.MetodoDePago):
    errorResponse = errors.Error(error="", detail=None)
    if  payments.validate_card(payment_method):
        errorResponse.error = "Metodo de Pago Invalido"
        return [rcodes.BAD_REQUEST, errorResponse]
    else:
        cls = Collections().get_collection(cf.CONSUMERS_COLLECTION)
        user_id = serialize_id(user_id)
        filter = {"_id" : user_id}
        payment_method = payment_method.model_dump()
        ans = cls.update_one(filter, {"$push": {"metodoDePago": payment_method}})
        if ans:
            return [
                rcodes.OK,
                StatusResponse(ok=True, detail="Informacion Actualizada"),
            ]
        else:
            errorResponse.error = "No se modifico la informacion"
            return [rcodes.NOT_FOUND, errorResponse]

def delete_payment_method(user_id: str, payment_method: schemas.MetodoDePago):
    errorResponse = errors.Error(error="", detail=None)
    cls = Collections().get_collection(cf.CONSUMERS_COLLECTION)
    user_id = serialize_id(user_id)
    filter = {"_id" : user_id}
    payment_method = payment_method.model_dump()
    ans = cls.update_one(filter, {"$pull": {"metodoDePago": payment_method}})
    if ans:
        return [
            rcodes.OK,
            StatusResponse(ok=True, detail="Informacion Actualizada"),
        ]
    else:
        errorResponse.error = "No se modifico la informacion"
        return [rcodes.NOT_FOUND, errorResponse]

def create_employee(empleado: schemas.Consumidor):
    cls = Collections().get_collection(cf.EMPLOYEES_COLLECTION)
    ans = cls.find_one({"usuario": empleado.usuario})
    if not ans:
        save = empleado.password
        empleado.sucursal = serialize_id(empleado.sucursal)
        empleado.password = pwd_context.hash(save)
        ans = cls.insert_one(empleado.dict())
        return ans.acknowledged
    return False

def update_employee(id_employee: str, mod_employee: schemas.ModEmpleado):
    errorResponse = errors.Error(error="", detail=None)
    try:
        cls = Collections().get_collection(cf.EMPLOYEES_COLLECTION)
        id_employee = serialize_id(id_employee)
        if mod_employee.sucursal != None:
            mod_employee.sucursal = serialize_id(mod_employee.sucursal)
        if employee_exists(id_employee):
            try:
                ans = cls.update_one(
                    {"_id": id_employee}, {"$set": mod_employee.model_dump(exclude_unset=True)}
                )
                if ans:
                    return [
                        rcodes.CREATED,
                        StatusResponse(ok=True, detail="Informacion Actualizada"),
                    ]
                else:
                    errorResponse.error = "No se modifico la informacion"
                    return [rcodes.NOT_FOUND, errorResponse]
            except Exception as e:
                errorResponse.error = "Ocurrio un error al actualizar la informacion"
                errorResponse.detail = str(e)
                return [rcodes.CONFLICT, errorResponse]
        else:
            errorResponse.error = "El usuario no existe"
            return [rcodes.NOT_FOUND, errorResponse]
    except Exception as e:
        errorResponse.error = "Objeto Invalido"
        errorResponse.detail = str(e)
        return [rcodes.BAD_REQUEST, errorResponse]

def delete_employee(employee_id: str):
    errorResponse = errors.Error(error="", detail=None)
    if employee_exists(employee_id):
        try: 
            employee_id = serialize_id(employee_id)
            cls= Collections().get_collection(cf.EMPLOYEES_COLLECTION)
            result = cls.delete_one({"_id": employee_id})
            if result:
                return [rcodes.OK, StatusResponse(ok=True, detail=(f"Consumidor con el ID {employee_id} eliminado correctamente"))]
            else:
                errorResponse.error = "No se Elimino el consumidor"
                return [rcodes.NOT_FOUND, errorResponse]
        except Exception as e:
            errorResponse.error = "Ocurrio un error al actualizar la informacion"
            errorResponse.detail = str(e)
            return [rcodes.CONFLICT, errorResponse]

def create_branch(branch: schemas.Sucursal):
    cls = Collections().get_collection(cf.BRANCHES_COLLECTION)
    ans = cls.find_one({"nombreComercial": branch.nombreComercial})
    if not ans:
        branch = branch.model_dump()
        ans = cls.insert_one(branch)
        return ans.acknowledged
    return False

def get_branches():
    cls = Collections().get_collection(cf.BRANCHES_COLLECTION)
    ans = cls.find()
    branches = [] 
    for branch in ans:
        branches.append(schemas.SucursalModelAuth(**transform_id_object(branch)))
    if ans:
        return branches
    else:
        return None

def get_branch(id_branch: str):
    id_branch = serialize_id(id_branch)
    cls = Collections().get_collection(cf.BRANCHES_COLLECTION)
    search = {"_id": id_branch}
    ans = cls.find_one(filter = search)
    ans = schemas.SucursalModelAuth(**transform_id_object(ans))
    return ans

def update_branch(id_branch: str, updated_branch: schemas.ModSucursal):
    errorResponse = errors.Error(error="", detail=None)
    try:
        cls = Collections().get_collection(cf.BRANCHES_COLLECTION)
        id_branch = serialize_id(id_branch)
        if branch_exists(id_branch):
            try:
                ans = cls.update_one(
                    {"_id": id_branch}, {"$set": updated_branch.model_dump(exclude_unset=True)}
                )
                if ans:
                    return [
                        rcodes.CREATED,
                        StatusResponse(ok=True, detail="Informacion Actualizada"),
                    ]
                else:
                    errorResponse.error = "No se modifico la informacion"
                    return [rcodes.NOT_FOUND, errorResponse]
            except Exception as e:
                errorResponse.error = "Ocurrio un error al actualizar la informacion"
                errorResponse.detail = str(e)
                return [rcodes.CONFLICT, errorResponse]
        else:
            errorResponse.error = "La sucursal no existe"
            return [rcodes.NOT_FOUND, errorResponse]
    except Exception as e:
        errorResponse.error = "Objeto Invalido"
        errorResponse.detail = str(e)
        return [rcodes.BAD_REQUEST, errorResponse]

def delete_branch(branch_id: str):
    errorResponse = errors.Error(error="", detail=None)
    serialize_id(branch_id)
    if branch_exists(branch_id):
        try: 
            branch_id = serialize_id(branch_id)
            cls= Collections().get_collection(cf.BRANCHES_COLLECTION)
            result = cls.delete_one({"_id": branch_id})
            print(result)
            if result:
                return [
                    rcodes.OK,
                    StatusResponse(ok=True, detail=(f"Sucursal con el ID {branch_id} eliminada correctamente")),
                ]
            else:
                errorResponse.error = "No se Elimino la sucursal"
                return [rcodes.NOT_FOUND, errorResponse]
        except Exception as e:
            errorResponse.error = "Ocurrio un error al eliminar la sucursal"
            errorResponse.detail = str(e)
            return [rcodes.CONFLICT, errorResponse]

def user_has_active_cart(consumer_id):
    cls = Collections().get_collection(cf.ORDERS_COLLECTION)
    filter = {"idConsumidor" : consumer_id, "estado" : "En carrito"} 
    res = cls.find_one(filter)
    if res:
        return True
    return False

def check_order_status(order_id):
    cls = Collections().get_collection(cf.ORDERS_COLLECTION)
    order_id = serialize_id(order_id)
    filter = {"_id" : order_id}
    res = cls.find_one(filter)
    print(res)
    if res:
        print("Se encontro el pedido")
        return res.get("estado")
    else:
        print("No se encontro el pedido")
        return None

def check_if_is_consumer_order(consumer_id, order_id):
    cls = Collections().get_collection(cf.ORDERS_COLLECTION)
    order_id = serialize_id(order_id)
    filter = {"_id" : order_id, "idConsumidor" : consumer_id}
    res = cls.find_one(filter)
    if res:
        return True
    return False

def get_orders_by_consumer(consumer_id):
    cls = Collections().get_collection(cf.ORDERS_COLLECTION)
    filter = {"idConsumidor" : consumer_id, "estado" : {"$ne" : "En validación"}}
    res = cls.find(filter)
    if res:
        orders = []
        for order in res:
            orders.append(schemas.Pedido(**transform_id_object(order)))
        return orders

def create_order(user_id: str, order: schemas.Pedido):
    cls = Collections().get_collection(cf.ORDERS_COLLECTION)
    print(order)
    order.idConsumidor = user_id
    order.estado = "En carrito"
    order = order.model_dump(exclude_unset=True)
    ans = cls.insert_one(order)
    return ans.acknowledged

def edit_order_consumer(order_id, modified_order: schemas.ModPedidoUsuario):
    errorResponse = errors.Error(error="", detail=None)
    # check if modified_order.productos dict is not empty
    if modified_order.productos != None and len(modified_order.productos)==0:
        modified_order.productos = None
    if modified_order.estado == "En Validación":
        modified_order.fechaRealizacion = datetime.now()
    try:
        cls = Collections().get_collection(cf.ORDERS_COLLECTION)
        order_id = serialize_id(order_id)
        try:
            ans = cls.update_one(
                {"_id": order_id}, {"$set": modified_order.model_dump(exclude_unset=True)}
            )
            if ans:
                return [
                    rcodes.OK,
                    StatusResponse(ok=True, detail="Informacion Actualizada"),
                ]
            else:
                errorResponse.error = "No se modifico la informacion"
                return [rcodes.NOT_FOUND, errorResponse]
        except Exception as e:
            errorResponse.error = "Ocurrio un error al actualizar la informacion"
            errorResponse.detail = str(e)
            return [rcodes.CONFLICT, errorResponse]
    except Exception as e:
        errorResponse.error = "Objeto Invalido"
        errorResponse.detail = str(e)
        return [rcodes.BAD_REQUEST, errorResponse]

def edit_order_delivery(order_id, modified_order: schemas.ModPedidoRepartidor):
    errorResponse = errors.Error(error="", detail=None)
    try:
        cls = Collections().get_collection(cf.ORDERS_COLLECTION)
        order_id = serialize_id(order_id)
        try:
            ans = cls.update_one(
                {"_id": order_id}, {"$set": modified_order.model_dump(exclude_unset=True)}
            )
            if ans:
                return [
                    rcodes.OK,
                    StatusResponse(ok=True, detail="Informacion Actualizada"),
                ]
            else:
                errorResponse.error = "No se modifico la informacion"
                return [rcodes.NOT_FOUND, errorResponse]
        except Exception as e:
            errorResponse.error = "Ocurrio un error al actualizar la informacion"
            errorResponse.detail = str(e)
            return [rcodes.CONFLICT, errorResponse]
    except Exception as e:
        errorResponse.error = "Objeto Invalido"
        errorResponse.detail = str(e)
        return [rcodes.BAD_REQUEST, errorResponse]

def edit_order_executive(order_id, modified_order: schemas.ModPedidoEjecutivo):
    errorResponse = errors.Error(error="", detail=None)
    try:
        cls = Collections().get_collection(cf.ORDERS_COLLECTION)
        order_id = serialize_id(order_id)
        try:
            ans = cls.update_one(
                {"_id": order_id}, {"$set": modified_order.model_dump(exclude_unset=True)}
            )
            if ans:
                return [
                    rcodes.OK,
                    StatusResponse(ok=True, detail="Informacion Actualizada"),
                ]
            else:
                errorResponse.error = "No se modifico la informacion"
                return [rcodes.NOT_FOUND, errorResponse]
        except Exception as e:
            errorResponse.error = "Ocurrio un error al actualizar la informacion"
            errorResponse.detail = str(e)
            return [rcodes.CONFLICT, errorResponse]
    except Exception as e:
        errorResponse.error = "Objeto Invalido"
        errorResponse.detail = str(e)
        return [rcodes.BAD_REQUEST, errorResponse]

def add_incidence_to_order(order_id: str, incidence: schemas.Incidencia):
    errorResponse = errors.Error(error="", detail=None)
    cls = Collections().get_collection(cf.ORDERS_COLLECTION)
    order_id = serialize_id(order_id)
    filter = {"_id" : order_id}
    incidence = incidence.model_dump()
    ans = cls.update_one(filter, {"$set": {"incidencia": incidence}})
    if ans:
        return [
            rcodes.OK,
            StatusResponse(ok=True, detail="Informacion Actualizada"),
        ]
    else:
        errorResponse.error = "No se modifico la informacion"
        return [rcodes.NOT_FOUND, errorResponse]

def cancel_order(order_id: str):
    errorResponse = errors.Error(error="", detail=None)
    cls = Collections().get_collection(cf.ORDERS_COLLECTION)
    order_id = serialize_id(order_id)
    filter = {"_id" : order_id}
    ans = cls.update_one(filter, {"$set": {"estado": "Cancelado"}})
    if ans:
        return [
            rcodes.OK,
            StatusResponse(ok=True, detail="Informacion Actualizada"),
        ]
    else:
        errorResponse.error = "No se modifico la informacion"
        return [rcodes.NOT_FOUND, errorResponse]

def check_if_is_employee_order(employee_id, order_id):
    cls = Collections().get_collection(cf.ORDERS_COLLECTION)
    order_id = serialize_id(order_id)
    filter = {"_id" : order_id, "idRepartidor" : employee_id}
    res = cls.find_one(filter)
    if res:
        return True
    return False

def get_products(id_branch: str):
    cls = Collections().get_collection(cf.PRODUCTS_CATALOG_COLLECTION)
    ans = cls.find({"cantidad.idSucursal": id_branch})
    products = [] 
    for product in ans:
        products.append(schemas.CatalogoProductos(**product))
    if ans:
        return products
    else:
        return None

def get_products_by_query(id_branch: str, categoria: str, nombre:str, precio: float, cBarras: str):
    cls = Collections().get_collection(cf.PRODUCTS_CATALOG_COLLECTION)
    query = {"cantidad.idSucursal": id_branch}
    if categoria:
        query["categoria"] = categoria
    if nombre:
        query["nombre"] = nombre
    if precio:
        query["precio"] = precio
    if cBarras:
        query["cBarras"] = cBarras
    ans = cls.find(query)
    print(ans)
    products = [] 
    for product in ans:
        products.append(schemas.CatalogoProductos(**product))
    if ans:
        return products
    else:
        return None

def delete_product(id_producto: str):
    errorResponse = errors.Error(error="", detail=None)
    try: 
        id_producto = serialize_id(id_producto)
        cls= Collections().get_collection(cf.PRODUCTS_CATALOG_COLLECTION)
        result = cls.delete_one({"_id": id_producto})
        print(result)
        if result:
            return [
                rcodes.OK,
                StatusResponse(ok=True, detail=(f"Producto con el ID {id_producto} eliminado correctamente")),
            ]
        else:
            errorResponse.error = "No se Elimino el producto"
            return [rcodes.NOT_FOUND, errorResponse]
    except Exception as e:
        errorResponse.error = "Ocurrio un error al eliminar el producto"
        errorResponse.detail = str(e)
        return [rcodes.CONFLICT, errorResponse]

def create_product(id_branch: str,product: schemas.CatalogoProductos):
    cls = Collections().get_collection(cf.PRODUCTS_CATALOG_COLLECTION)
    ans = cls.find_one({"cBarras": product.cBarras})
    if not ans:
        product = product.model_dump()
        print(product)
        ans = cls.insert_one(product)
        return ans.acknowledged
    return False

def update_product(id_producto: str, modified_product: schemas.CatalogoProductosMod):
    errorResponse = errors.Error(error="", detail=None)
    cls = Collections().get_collection(cf.PRODUCTS_CATALOG_COLLECTION)
    id_producto = serialize_id(id_producto)
    ans = cls.find_one({"_id": id_producto})
    if ans:
        try:
            ans = cls.update_one(
                {"_id": id_producto}, {"$set": modified_product.model_dump(exclude_unset=True)}
            )
            if ans:
                return [
                    rcodes.CREATED,
                    StatusResponse(ok=True, detail="Informacion Actualizada"),
                ]
            else:
                errorResponse.error = "No se modifico la informacion"
                return [rcodes.NOT_FOUND, errorResponse]
        except Exception as e:
            errorResponse.error = "Ocurrio un error al actualizar la informacion"
            errorResponse.detail = str(e)
            return [rcodes.CONFLICT, errorResponse]
    else:
        errorResponse.error = "El producto no existe"
        return [rcodes.NOT_FOUND, errorResponse]