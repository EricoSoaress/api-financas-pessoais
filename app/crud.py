# app/crud.py (versão corrigida)

from sqlalchemy.orm import Session
from . import models, schemas
# IMPORTAÇÃO QUE FALTAVA:
from .security import get_password_hash, create_access_token, verify_password

def get_user(db: Session, user_id: int):
    return db.query(models.Usuario).filter(models.Usuario.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.Usuario).filter(models.Usuario.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Usuario).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UsuarioCreate):
    # A chamada para esta função agora funciona, pois ela foi importada.
    hashed_password = get_password_hash(user.password)
    db_user = models.Usuario(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_transactions_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Transacao).filter(models.Transacao.owner_id == user_id).offset(skip).limit(limit).all()

def create_user_transaction(db: Session, transaction: schemas.TransacaoCreate, user_id: int):
    db_transaction = models.Transacao(**transaction.model_dump(), owner_id=user_id)
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def update_transaction(db: Session, transaction_id: int, transaction: schemas.TransacaoBase):
    db_transaction = db.query(models.Transacao).filter(models.Transacao.id == transaction_id).first()
    if db_transaction:
        db_transaction.description = transaction.description
        db_transaction.value = transaction.value
        db_transaction.type = transaction.type
        db.commit()
        db.refresh(db_transaction)
    return db_transaction