from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from urllib.parse import quote_plus
from ..config.config import *

engine = create_engine(f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=disable", 
    pool_pre_ping=True,
    pool_size=DB_POOLSIZE,         
    max_overflow=DB_MAXOVERFLOW,      
    pool_timeout=DB_POOLTIMEOUT,      
    pool_recycle=DB_POOLRECYCLE
)

def get_db():
    with DBContext() as db:
        try:
            yield db
        except:
            db.rollback()
            raise
        else:
            db.commit()

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()
metadata = Base.metadata

class DBContext:
    def __init__(self):
        self.db = SessionLocal()

    def __enter__(self):
        return self.db

    def __exit__(self, et, ev, traceback):
        self.db.close()
