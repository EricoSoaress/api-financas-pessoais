# app/main.py

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from jose import JWTError, jwt
from .database import engine, Base

Base.metadata.create_all(bind=engine)

# 1. IMPORTS DOS NOSSOS MÓDULOS
from . import models, schemas, crud, security
from .database import engine, SessionLocal

# 2. CRIAÇÃO DAS TABELAS (se não existirem)
models.Base.metadata.create_all(bind=engine)


# 3. CRIAÇÃO DA INSTÂNCIA PRINCIPAL DO FastAPI
# A variável 'app' é definida AQUI.
app = FastAPI(
    title="Minhas Finanças API",
    description="API para o aplicativo de gerenciamento de finanças pessoais.",
    version="0.1.0"
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# 4. DEFINIÇÃO DA DEPENDÊNCIA DO BANCO DE DADOS
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- FUNÇÃO PARA OBTER O USUÁRIO ATUAL (PROTEÇÃO) ---
def get_usuario_atual(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decodifica o token JWT
        payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        # Extrai o e-mail ("subject") do payload
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Busca o usuário no banco de dados
    user = crud.buscar_usuario_por_email(db, email=username)
    if user is None:
        raise credentials_exception
    return user

# 5. DEFINIÇÃO DOS ENDPOINTS
# Agora que 'app' já existe, podemos usá-la para criar os endpoints.
# --- ENDPOINT PARA CRIAR TRANSAÇÃO (PROTEGIDO) ---
@app.get("/transacoes", response_model=list[schemas.TransacaoPublic])
def listar_todas_transacoes(
    db: Session = Depends(get_db),
    usuario_atual: models.Usuario = Depends(get_usuario_atual)
):
    """
    Lista todas as transações do usuário atualmente logado.
    """
    return crud.listar_transacoes_por_usuario(db=db, usuario_id=usuario_atual.id)

# --- ENDPOINT PARA ATUALIZAR UMA TRANSAÇÃO (PROTEGIDO) ---
@app.put("/transacoes/{transacao_id}", response_model=schemas.TransacaoPublic)
def atualizar_uma_transacao(
    transacao_id: int,
    transacao: schemas.TransacaoCreate, # Novos dados vêm no corpo da requisição
    db: Session = Depends(get_db),
    usuario_atual: models.Usuario = Depends(get_usuario_atual)
):
    """
    Atualiza uma transação específica do usuário logado.
    """
    # 1. Busca a transação no banco de dados pelo ID fornecido.
    db_transacao = crud.buscar_transacao_por_id(db, transacao_id=transacao_id)

    # 2. Se a transação não for encontrada, retorna um erro 404.
    if db_transacao is None:
        raise HTTPException(status_code=404, detail="Transação não encontrada")

    # 3. VERIFICAÇÃO DE POSSE: Garante que o usuário só pode editar suas transações.
    if db_transacao.usuario_id != usuario_atual.id:
        raise HTTPException(status_code=403, detail="Não tem permissão para alterar esta transação")

    # 4. Se tudo estiver certo, chama a função para atualizar os dados.
    return crud.atualizar_transacao(
        db=db, db_transacao=db_transacao, transacao_atualizada=transacao
    )


@app.post("/transacoes", response_model=schemas.TransacaoPublic, status_code=status.HTTP_201_CREATED)
def criar_nova_transacao(
    transacao: schemas.TransacaoCreate,
    db: Session = Depends(get_db),
    usuario_atual: models.Usuario = Depends(get_usuario_atual)
):
    """
    Cria uma nova transação para o usuário atualmente logado.
    """
    nova_transacao = crud.criar_transacao(
        db=db, transacao=transacao, usuario_id=usuario_atual.id
    )
    return nova_transacao

@app.post("/token", response_model=schemas.Token)
def login_para_obter_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    usuario = crud.buscar_usuario_por_email(db, email=form_data.username)
    if not usuario or not security.verificar_senha(form_data.password, usuario.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.criar_token_acesso(
        data={"sub": usuario.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/usuarios", response_model=schemas.UsuarioPublic, status_code=status.HTTP_201_CREATED)
def criar_novo_usuario(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    db_user = crud.buscar_usuario_por_email(db, email=usuario.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="E-mail já cadastrado."
        )
    novo_usuario = crud.criar_usuario(db=db, usuario=usuario)
    return novo_usuario

# --- ENDPOINT PARA DELETAR UMA TRANSAÇÃO (PROTEGIDO) ---
@app.delete("/transacoes/{transacao_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_uma_transacao(
    transacao_id: int,
    db: Session = Depends(get_db),
    usuario_atual: models.Usuario = Depends(get_usuario_atual)
):
    """
    Deleta uma transação específica do usuário logado.
    """
    # 1. Busca a transação que se quer deletar.
    db_transacao = crud.buscar_transacao_por_id(db, transacao_id=transacao_id)

    # 2. Se não existir, retorna 404.
    if db_transacao is None:
        raise HTTPException(status_code=404, detail="Transação não encontrada")

    # 3. Verifica se o usuário é o dono da transação.
    if db_transacao.usuario_id != usuario_atual.id:
        raise HTTPException(status_code=403, detail="Não tem permissão para deletar esta transação")

    # 4. Se tudo estiver certo, deleta a transação.
    crud.deletar_transacao(db, db_transacao=db_transacao)
    
    # Com o status 204, a resposta não tem corpo, então retornamos None.
    return None

@app.get("/transacoes/{transacao_id}", response_model=schemas.TransacaoPublic)
def ler_uma_transacao(
    transacao_id: int,
    db: Session = Depends(get_db),
    usuario_atual: models.Usuario = Depends(get_usuario_atual)
):
    """
    Retorna os detalhes de uma transação específica do usuário logado.
    """
    # 1. Busca a transação no banco de dados.
    db_transacao = crud.buscar_transacao_por_id(db, transacao_id=transacao_id)

    # 2. Se não encontrar, retorna erro 404.
    if db_transacao is None:
        raise HTTPException(status_code=404, detail="Transação não encontrada")

    # 3. Verifica se o usuário logado é o dono da transação.
    if db_transacao.usuario_id != usuario_atual.id:
        raise HTTPException(status_code=403, detail="Não tem permissão para ver esta transação")

    # 4. Se tudo estiver correto, retorna a transação encontrada.
    return db_transacao


@app.get("/")
def ola_mundo():
    return {"mensagem": "Bem-vindo à API Minhas Finanças!"}