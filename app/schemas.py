

from pydantic import BaseModel, EmailStr
from datetime import date, datetime
from decimal import Decimal
from typing import List


class TransacaoBase(BaseModel):
    descricao: str
    valor: Decimal
    tipo: str

class TransacaoCreate(TransacaoBase):
  
    pass

class Transacao(TransacaoBase):
    id: int
    data: date
    usuario_id: int 

    class Config:
        from_attributes = True
# =========================================================================


class UsuarioBase(BaseModel):
    email: EmailStr
    nome: str

class UsuarioCreate(UsuarioBase):
    senha: str

class Usuario(UsuarioBase):
    id: int
    data_criacao: str
   
    transacoes: List[Transacao] = []

    class Config:
        from_attributes = True
