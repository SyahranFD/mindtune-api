import os
from urllib.parse import quote_plus

DB_USER = "postgres"
DB_PASS = quote_plus(os.getenv("DB_PASS", "Asis@2024"))
DB_NAME = os.getenv("DB_NAME", "db_asis_prod")
DB_HOST = "172.17.0.1"
DB_PORT = "5432"

DB_POOLSIZE = 50
DB_MAXOVERFLOW = 25
DB_POOLTIMEOUT = 30
DB_POOLRECYCLE = 1800
