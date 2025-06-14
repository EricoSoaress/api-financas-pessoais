# app/schemas.py

from pydantic import BaseModel, EmailStr
from pydantic import BaseModel, EmailStr
from datetime import date
from decimal import Decimal


# ... (schemas UsuarioCreate, UsuarioPublic, Token)

# Schema para a criação de um usuário (o que o usuário nos envia)
class UsuarioCreate(BaseModel):
    nome: str
    email: EmailStr  # Pydantic valida se é um e-mail válido
    senha: str

# Schema para a resposta (o que enviamos de volta ao usuário)
# NUNCA inclua a senha na resposta!
class UsuarioPublic(BaseModel):
    id: int
    nome: str
    email: EmailStr

    class Config:
        from_attributes = True # Antigamente orm_mode = True
        # Permite que o Pydantic leia os dados de um objeto ORM (nosso modelo SQLAlchemy)
# app/schemas.py

# schemas tonken
class Token(BaseModel):
    access_token: str
    token_type: str



# Schema para receber os dados de criação de uma transação
class TransacaoCreate(BaseModel):
    descricao: str
    valor: Decimal
    tipo: str # 'receita' ou 'despesa'

# Schema para exibir uma transação
class TransacaoPublic(BaseModel):
    id: int
    descricao: str
    valor: Decimal
    tipo: str
    data: date
    usuario_id: int

    class Config:
        from_attributes = True    