from typing import Collection
import mercado_cuevas_api.config as cf
from mercado_cuevas_api.documentdb.document import Collections
import mercado_cuevas_api.documentdb.schemas as schemas
from mercado_cuevas_api.documentdb.document_operations import transform_id_object

def get_consumer(phoneNumber: str):
    try:
        cls = Collections().get_collection(cf.CONSUMERS_COLLECTION)
        search = {"nCelular": phoneNumber}
        ans = cls.find_one(search)
        if ans:
            return schemas.ConsumidorModelAuth(**transform_id_object(ans))
        else:
            return None
    except Exception as e:
        # print(str(e))
        return None

def get_employee(username: str):
    try:
        cls = Collections().get_collection(cf.EMPLOYEES_COLLECTION)
        search = {"usuario": username}
        ans = cls.find_one(search)
        print(ans)
        if ans:
            return schemas.EmpleadoModelAuth(**transform_id_object(ans))
        else:
            return None
    except Exception as e:
        print(e)
        return None
