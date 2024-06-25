import os
from dotenv import load_dotenv


class EnvVar:
    def __init__(self):
        try:
            load_dotenv()
        except Exception:
            pass

    def get_variable(self, name, alt="No Content"):
        try:
            value = os.getenv(name)
            return value if value else alt
        except Exception:
            return alt


# Enviroments Variables
env = EnvVar()

DOCUMENT_DB_USER = env.get_variable("DB_USER", "franzrivera9471")
DOCUMENT_DB_PASSWORD = env.get_variable("DB_PASSWORD", "7FlxlDmSGAk3iqnE")
DEFAULT_DATABASE = env.get_variable("DEFAULT_DATABASE", "MercadoCuevas")
DOCUMENT_DB_URL = env.get_variable("DB_URL", "clustermercadocuevas.kpvrhvl.mongodb.net")
PRODUCTS_CATALOG_COLLECTION = env.get_variable("PRODUCTS_CATALOG_COLLECTION", "catalogoProductos")
CONSUMERS_COLLECTION = env.get_variable("CONSUMERS_COLLECTION", "consumidores")
EMPLOYEES_COLLECTION = env.get_variable("EMPLOYEES_COLLECTION", "empleados")
ORDERS_COLLECTION = env.get_variable("ORDERS_COLLECTION", "pedidos")
BRANCHES_COLLECTION = env.get_variable("BRANCHES_COLLECTION", "sucursales")
# todo change next variables with proper values
GOOGLE_PROJECT = env.get_variable("GOOGLE_PROJECT_ID", "MercadoCuevasStorage")
BUCKET_NAME = env.get_variable("GOOGLE_STORAGE_BUCKET", "mercado_cuevas")
GRPC_SERVER_URL = env.get_variable(
    "GRPC_SERVER", "ec2-3-137-140-200.us-east-2.compute.amazonaws.com:8001"
)
SECRET_KEY_AUTH = env.get_variable(
    "AUTH_SECRET", "c075ee3a5199f68f16f85f38a88d26fc46b142c4c6b46b795c959a4a1b6444b0"
)
AUTH_ALGORITH = env.get_variable("AUTH_ALGORITH", "HS256")
