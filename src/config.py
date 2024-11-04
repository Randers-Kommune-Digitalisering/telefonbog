import os
from dotenv import load_dotenv

load_dotenv()

DELTA_CERT_BASE64 = os.environ["DELTA_CERT_BASE64"].strip()
DELTA_CERT_PASSWORD = os.environ["DELTA_CERT_PASSWORD"].strip()

KEYCLOAK_URL = os.environ["KEYCLOAK_URL"].strip()
KEYCLOAK_REALM = os.environ["KEYCLOAK_REALM"].strip()
KEYCLOAK_CLIENT = os.environ["KEYCLOAK_CLIENT"].strip()

DB_SCHEMA = "telefonbog"
DB_USER = os.environ['DB_USER']
DB_PASS = os.environ['DB_PASS']
DB_HOST = os.environ['DB_HOST']
DB_PORT = os.environ['DB_PORT']
DB_DATABASE = os.environ['DB_DATABASE']