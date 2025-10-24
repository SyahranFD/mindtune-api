import os
from urllib.parse import quote_plus

DB_USER = "postgres"
DB_PASS = quote_plus(os.getenv("DB_PASS", "admin"))
DB_NAME = os.getenv("DB_NAME", "fastapi_mindtune_api")
DB_HOST = "localhost"
DB_PORT = "5433"

DB_POOLSIZE = 50
DB_MAXOVERFLOW = 25
DB_POOLTIMEOUT = 30
DB_POOLRECYCLE = 1800
