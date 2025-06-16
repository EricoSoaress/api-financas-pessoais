# app/main.py (versão final e completa)

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from typing import List # <--- ESTA É A LINHA QUE CORRIGE O ERRO

# 1. Importar todos os nossos módulos
from . import crud, models, schemas
from .database import SessionLocal, engine, Base

# 2. Criar as tabelas no banco de dados
Base.metadata.create_all(bind=engine)

# 3. Criar a aplicação FastAPI
app = FastAPI()


# --- Dependências ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Endpoints ---

@app.get("/")
def read_root():
    return {"message": "Bem-vindo à API de Finanças Pessoais"}

@app.post("/login/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, email=form_data.username)
    if not user or not crud.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=30)
    access_token = crud.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users/", response_model=schemas.Usuario)
def create_user(user: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.get("/users/", response_model=List[schemas.Usuario])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@app.post("/transactions/", response_model=schemas.Transacao)
def create_transaction_for_user(
    transaction: schemas.TransacaoCreate, db: Session = Depends(get_db)
):
    return crud.create_user_transaction(db=db, transaction=transaction, user_id=transaction.owner_id)

@app.get("/transactions/{user_id}", response_model=List[schemas.Transacao])
def read_transactions_for_user(user_id: int, db: Session = Depends(get_db)):
    transactions = crud.get_transactions_by_user(db, user_id=user_id)
    return transactions