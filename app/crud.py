# app/crud.py

from sqlalchemy.orm import Session
from . import models, schemas, security

def buscar_usuario_por_email(db: Session, email: str):
    """Busca um usuário no banco de dados pelo seu e-mail."""
    return db.query(models.Usuario).filter(models.Usuario.email == email).first()

def criar_usuario(db: Session, usuario: schemas.UsuarioCreate):
    """Cria um novo usuário no banco de dados."""
    # Gera o hash da senha antes de salvar
    senha_hash = security.gerar_hash_senha(usuario.senha)
    
    # Cria o objeto do modelo SQLAlchemy com a senha em hash
    db_usuario = models.Usuario(
        nome=usuario.nome,
        email=usuario.email,
        senha_hash=senha_hash
    )
    
    db.add(db_usuario)  # Adiciona o novo usuário à sessão do banco
    db.commit()         # Confirma a transação, salvando no banco
    db.refresh(db_usuario) # Atualiza o objeto db_usuario com os dados do banco (como o id)
    return db_usuario

def criar_transacao(db: Session, transacao: schemas.TransacaoCreate, usuario_id: int):
    """Cria uma nova transação no banco de dados, associada a um usuário."""
    db_transacao = models.Transacao(
        **transacao.model_dump(),  # Desempacota o dicionário do Pydantic
        usuario_id=usuario_id
    )
    db.add(db_transacao)
    db.commit()
    db.refresh(db_transacao)
    return db_transacao
    
def listar_transacoes_por_usuario(db: Session, usuario_id: int):
    """Busca todas as transações de um usuário específico."""
    return db.query(models.Transacao).filter(models.Transacao.usuario_id == usuario_id).all()

def buscar_transacao_por_id(db: Session, transacao_id: int):
    """Busca uma única transação pelo seu ID."""
    return db.query(models.Transacao).filter(models.Transacao.id == transacao_id).first()

def atualizar_transacao(
    db: Session, db_transacao: models.Transacao, transacao_atualizada: schemas.TransacaoCreate
):
    """Atualiza os dados de uma transação existente no banco."""
    # Converte o schema Pydantic para um dicionário
    update_data = transacao_atualizada.model_dump(exclude_unset=True)
    
    # Itera sobre o dicionário e atualiza os campos do objeto SQLAlchemy
    for key, value in update_data.items():
        setattr(db_transacao, key, value)
        
    db.add(db_transacao)
    db.commit()
    db.refresh(db_transacao)
    return db_transacao   

def deletar_transacao(db: Session, db_transacao: models.Transacao):
    """Deleta uma transação do banco de dados."""
    db.delete(db_transacao)
    db.commit()
    return