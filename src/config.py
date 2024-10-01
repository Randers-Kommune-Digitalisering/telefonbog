import os
from dotenv import load_dotenv

load_dotenv()

DELTA_CERT_BASE64 = os.environ["DELTA_CERT_BASE64"].strip()
DELTA_CERT_PASSWORD = os.environ["DELTA_CERT_PASSWORD"].strip()

KEYCLOAK_URL = os.environ["KEYCLOAK_URL"].strip()
KEYCLOAK_REALM = os.environ["KEYCLOAK_REALM"].strip()
KEYCLOAK_CLIENT = os.environ["KEYCLOAK_CLIENT"].strip()
