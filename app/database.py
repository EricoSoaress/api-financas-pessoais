# app/database.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env (se ele existir)
load_dotenv()

# Pega a URL do banco de dados a partir das variáveis de ambiente
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# Se a URL começar com "postgres://", substitui por "postgresql://"
# A Heroku usa "postgres://", mas o SQLAlchemy espera "postgresql://"
if SQLALCHEMY_DATABASE_URL and SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Caso a variável de ambiente não seja encontrada (para desenvolvimento local)
# usamos um banco de dados SQLite.
if not SQLALCHEMY_DATABASE_URL:
    SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

# Cria a "engine" do banco de dados
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    # O argumento 'connect_args' só é necessário para SQLite.
    connect_args={"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()