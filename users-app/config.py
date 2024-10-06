from passlib.context import CryptContext
from os import environ
from dotenv import load_dotenv
from enum import Enum

load_dotenv()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
key = environ.get("SECRET_KEY")
algorithm = environ.get("ALGORITHM")
cache_url = environ.get("CACHE_URL")
db_url = environ.get("DB_URL")
exp = int(environ.get("EXPIRE_MINUTES"))
app_mail = environ.get("APP_MAIL")

class user_role(Enum):
    base = "Base"
    dispatch_tech = "Dispatch_Tech"
    infrastructure_tech = "Infrastructure_Tech"
    installation_tech = "Installation_Tech"
    dispatch_admin = "Dispatch_Admin"
    infrastructure_admin = "Infrastructure_Admin"
    installation_admin = "Installation_Admin"
    reporting_admin = "Reporting_Admin"
    stock_admin = "Stock_Admin"
    general_admin = "General_Admin"



