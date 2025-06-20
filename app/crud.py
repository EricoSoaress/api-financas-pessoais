from sqlalchemy.orm import Session
from . import models, schemas
from .security import get_password_hash

def get_user(db: Session, user_id: int):
    return db.query(models.Usuario).filter(models.Usuario.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.Usuario).filter(models.Usuario.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Usuario).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UsuarioCreate):
    hashed_password = get_password_hash(user.senha)
    db_user = models.Usuario(
        email=user.email,
        nome=user.nome,
        senha_hash=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_transactions_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    # ALTERAÇÃO FINAL: Adicionado um segundo critério de ordenação pelo ID.
    return db.query(models.Transacao).filter(
        models.Transacao.usuario_id == user_id
    ).order_by(models.Transacao.data.desc(), models.Transacao.id.desc()).offset(skip).limit(limit).all()

def get_transaction_by_id(db: Session, transaction_id: int, user_id: int):
    return db.query(models.Transacao).filter(
        models.Transacao.id == transaction_id,
        models.Transacao.usuario_id == user_id
    ).first()

def create_user_transaction(db: Session, transaction: schemas.TransacaoCreate, user_id: int):
    db_transaction = models.Transacao(**transaction.model_dump(), usuario_id=user_id)
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def update_transaction(db: Session, transaction_id: int, transaction_data: schemas.TransacaoCreate, user_id: int):
    db_transaction = get_transaction_by_id(db, transaction_id=transaction_id, user_id=user_id)
    if db_transaction:
        db_transaction.descricao = transaction_data.descricao
        db_transaction.valor = transaction_data.valor
        db_transaction.tipo = transaction_data.tipo
        db.commit()
        db.refresh(db_transaction)
    return db_transaction

def delete_transaction(db: Session, transaction_id: int, user_id: int):
    db_transaction = get_transaction_by_id(db, transaction_id=transaction_id, user_id=user_id)
    if db_transaction:
        db.delete(db_transaction)
        db.commit()
        return db_transaction
    return None