from sqlalchemy.orm import Session
from . import models, schemas
from passlib.context import CryptContext

# パスワードをハッシュ化するためのコンテキストを設定
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()  # メールアドレスに基づいてユーザーをデータベースから検索

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)  # ユーザー作成時にパスワードをハッシュ化
    db_user = models.User(email=user.email, hashed_password=hashed_password, name=user.name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(models.User).filter(models.User.name == username).first()  # ユーザー名に基づいてユーザーを検索
    if not user:  # ユーザーが見つからない場合は、認証失敗
        return False
    if not pwd_context.verify(password, user.hashed_password):  # パスワードが一致しない場合は、認証失敗
        return False
    return user  # 認証成功