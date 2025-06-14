# app/database.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# URL de conexão com o banco de dados SQLite
# "sqlite:///./minhas_financas.db" significa que usaremos SQLite
# e o arquivo do banco se chamará "minhas_financas.db" e ficará na raiz do projeto.
SQLALCHEMY_DATABASE_URL = "sqlite:///./minhas_financas.db"

# O "engine" é o ponto de entrada para o banco de dados.
# O argumento connect_args é necessário apenas para o SQLite para permitir
# que mais de um "thread" se comunique com o banco.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Cada instância de SessionLocal será uma sessão (uma "conversa") com o banco.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Usaremos esta classe Base para criar nossos modelos do banco de dados (as tabelas).
Base = declarative_base()