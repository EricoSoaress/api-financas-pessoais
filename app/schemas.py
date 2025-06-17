# app/schemas.py

from pydantic import BaseModel, EmailStr
from datetime import date, datetime
from decimal import Decimal
from typing import List

# ==================== TRANSAÇÃO SCHEMAS (COM ALTERAÇÃO) ====================
class TransacaoBase(BaseModel):
    # Nomes dos campos alterados para corresponder ao app Android
    descricao: str
    valor: Decimal # Usar Decimal para valores monetários é uma boa prática
    tipo: str

class TransacaoCreate(TransacaoBase):
    # O owner_id foi removido. A API vai descobrir isso pelo token.
    pass

class Transacao(TransacaoBase):
    id: int
    data: date
    usuario_id: int # Alterado de owner_id para corresponder ao modelo do banco

    class Config:
        from_attributes = True
# =========================================================================

# --- Usuario Schemas (sem alteração da última vez) ---
class UsuarioBase(BaseModel):
    email: EmailStr
    nome: str

class UsuarioCreate(UsuarioBase):
    senha: str

class Usuario(UsuarioBase):
    id: int
    data_criacao: str
    # O nome da relação é 'transacoes', como no modelo SQLAlchemy
    transacoes: List[Transacao] = []

    class Config:
        from_attributes = True