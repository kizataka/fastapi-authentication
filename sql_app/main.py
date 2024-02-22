from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from . import crud, models, schemas, database

SECRET_KEY = "your_secret_key"  # JWTの署名に使用される秘密鍵
ALGORITHM = "HS256"  # JWTの署名に使用されるアルゴリズム
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # トークンの有効期限

app = FastAPI()

models.Base.metadata.create_all(bind=database.engine)

# トークンの取得に使用されるURLを指定
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# パスワードをハッシュ化するためのコンテキストを設定
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 依存関係
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# JWTを生成する関数
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# ユーザーがログインし、トークンを取得
@app.post("/token", summary="ログインしてトークンを取得")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.name}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# ユーザー情報を登録
@app.post("/users/", response_model=schemas.UserRead)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # 既に同じメールアドレスまたはユーザー名を持つユーザーが存在するか確認
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    # ユーザーをデータベースに追加
    return crud.create_user(db=db, user=user)