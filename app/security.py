# app/security.py
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
# ... o código anterior (pwd_context, verificar_senha, gerar_hash_senha) fica aqui ...
# Define o contexto de criptografia, dizendo para usar o algoritmo bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verificar_senha(senha_plana: str, senha_hash: str) -> bool:
    """Verifica se a senha plana corresponde ao hash."""
    return pwd_context.verify(senha_plana, senha_hash)

def gerar_hash_senha(senha: str) -> str:
    """Gera o hash de uma senha plana."""
    return pwd_context.hash(senha)

# --- CONFIGURAÇÃO DO TOKEN JWT ---

# CHAVE SECRETA: Em um projeto real, esta chave NUNCA deve estar no código.
# Deve ser lida de uma variável de ambiente.
SECRET_KEY = "uma-chave-secreta-muito-dificil-de-adivinhar-9a8b7c6d5e4f"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 # O token expirará em 30 minutos

def criar_token_acesso(data: dict, expires_delta: Optional[timedelta] = None):
    """Cria um novo token de acesso JWT."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        # Define o tempo de expiração padrão de 30 minutos
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt