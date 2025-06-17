from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List
from fastapi.middleware.cors import CORSMiddleware

from . import crud, models, schemas, security
from .database import SessionLocal, engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login/token")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = security.decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    email: str = payload.get("sub")
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido, sem 'sub'",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = crud.get_user_by_email(db, email=email)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
    return user

@app.get("/")
def read_root():
    return {"message": "Bem-vindo à API de Finanças Pessoais"}

@app.post("/login/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, email=form_data.username)
    if not user or not security.verify_password(form_data.password, user.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=60)
    access_token = security.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/usuarios/", response_model=schemas.Usuario)
def create_user(user: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.post("/transacoes/", response_model=schemas.Transacao)
def create_transaction(
    transaction: schemas.TransacaoCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    return crud.create_user_transaction(db=db, transaction=transaction, user_id=current_user.id)

@app.get("/transacoes/", response_model=List[schemas.Transacao])
def read_transactions(
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    return crud.get_transactions_by_user(db, user_id=current_user.id)

# ==================== ENDPOINTS NOVOS E CORRIGIDOS ====================

# 1. NOVO ENDPOINT para buscar uma transação específica
@app.get("/transacoes/{transaction_id}", response_model=schemas.Transacao)
def read_transaction_by_id(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    db_transaction = crud.get_transaction_by_id(db, transaction_id=transaction_id, user_id=current_user.id)
    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Transação não encontrada")
    return db_transaction

# 2. ENDPOINT DE UPDATE CORRIGIDO, seguro e com a rota certa
@app.put("/transacoes/{transaction_id}", response_model=schemas.Transacao)
def update_transaction(
    transaction_id: int,
    transaction_data: schemas.TransacaoCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    db_transaction = crud.update_transaction(db, transaction_id=transaction_id, transaction_data=transaction_data, user_id=current_user.id)
    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Transação não encontrada ou você não tem permissão para editar")
    return db_transaction

# 3. ENDPOINT DE DELETE CORRIGIDO, seguro e com a rota certa
@app.delete("/transacoes/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    deleted_transaction = crud.delete_transaction(db, transaction_id=transaction_id, user_id=current_user.id)
    if deleted_transaction is None:
        raise HTTPException(status_code=404, detail="Transação não encontrada ou você não tem permissão para deletar")
    return