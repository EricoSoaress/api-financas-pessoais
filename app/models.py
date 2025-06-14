# app/models.py - VERSÃO FINAL COM TUDO INCLUÍDO

from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base
from datetime import date, datetime, timezone

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    senha_hash = Column(String)
    data_criacao = Column(String, default=lambda: datetime.now(timezone.utc).isoformat())

    # AQUI ESTÁ A LINHA ESSENCIAL QUE FOI OMITIDA E CAUSOU O ERRO
    transacoes = relationship("Transacao", back_populates="dono")


class Transacao(Base):
    __tablename__ = "transacoes"

    id = Column(Integer, primary_key=True, index=True)
    descricao = Column(String, index=True)
    valor = Column(Numeric(10, 2))
    tipo = Column(String)
    data = Column(Date, default=date.today)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))

    dono = relationship("Usuario", back_populates="transacoes")