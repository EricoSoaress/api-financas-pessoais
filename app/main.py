# app/main.py

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from fastapi import status

from . import crud, models, schemas, security
from .database import SessionLocal, engine, Base

Base.metadata.create_all(bind=engine)



app = FastAPI()

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
    if not user or not security.verify_password(form_data.password, user.senha_hash):
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=30)
    access_token = security.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# ALTERAÇÃO AQUI: A rota foi corrigida de "/users/" para "/usuarios/"
@app.post("/usuarios/", response_model=schemas.Usuario)
def create_user(user: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

# ... resto do seu arquivo main.py ...

@app.get("/usuarios/", response_model=List[schemas.Usuario])
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

@app.put("/transactions/{transaction_id}", response_model=schemas.Transacao)
def update_transaction_endpoint(
    transaction_id: int, transaction: schemas.TransacaoBase, db: Session = Depends(get_db)
):
    db_transaction = crud.update_transaction(db, transaction_id=transaction_id, transaction=transaction)
    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return db_transaction

@app.delete("/transactions/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    deleted_transaction = crud.delete_transaction(db, transaction_id=transaction_id)
    if deleted_transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return {"detail": "Transaction deleted successfully"}

@app.get("/transaction/{transaction_id}", response_model=schemas.Transacao)
def read_transaction(transaction_id: int, db: Session = Depends(get_db)):
    db_transaction = crud.get_transaction_by_id(db, transaction_id=transaction_id)
    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return db_transaction