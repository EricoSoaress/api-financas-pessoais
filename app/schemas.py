# app/schemas.py

from typing import List
from pydantic import BaseModel, EmailStr
from pydantic import BaseModel, EmailStr
from datetime import date
from decimal import Decimal


# ... (schemas UsuarioCreate, UsuarioPublic, Token)

# Schema para a criação de um usuário (o que o usuário nos envia)
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


# Esquemas para Usuário
class UsuarioBase(BaseModel):
    email: str

class UsuarioCreate(UsuarioBase):
    password: str

# ==================== ESTE É O ESQUEMA QUE FALTAVA ====================
# Note o nome "Usuario", que corresponde ao seu padrão.
class Usuario(UsuarioBase):
    id: int
    transactions: List[Transacao] = []

    class Config:
        from_attributes = True
# =====================================================================