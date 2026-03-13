# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# 1. KONFIGURACJA BAZY DANYCH
DATABASE_URL = "sqlite:///fundacja.db"

# 2. SILNIK
engine = create_engine(
    DATABASE_URL, 
    connect_args={'check_same_thread': False} if "sqlite" in DATABASE_URL else {}
)

# 3. SESJA
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. BAZA MODELI
Base = declarative_base()

def get_db():
    """Funkcja pomocnicza do tworzenia i zamykania sesji (Context Manager)"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()