# app/schemas.py

from pydantic import BaseModel, EmailStr
from datetime import date
from decimal import Decimal
from typing import List, Optional # Garanta que Optional está importado

# --- Transacao Schemas (sem alteração) ---
class TransacaoBase(BaseModel):
    description: str
    value: float
    type: str

class TransacaoCreate(TransacaoBase):
    owner_id: int

class Transacao(TransacaoBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True

# --- Usuario Schemas (COM ALTERAÇÃO) ---
class UsuarioBase(BaseModel):
    email: EmailStr
    # Adicionamos o nome aqui para que todos os schemas que herdam o tenham
    nome: str

class UsuarioCreate(UsuarioBase):
    # Alterado de 'password' para 'senha' para corresponder ao app
    senha: str

class Usuario(UsuarioBase):
    id: int
    # Adicionamos a data aqui para corresponder ao modelo do banco
    data_criacao: str
    transactions: List[Transacao] = []

    class Config:
        from_attributes = True