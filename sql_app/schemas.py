from pydantic import BaseModel, EmailStr, Field

# ユーザー作成時に使用するスキーマ
class UserCreate(BaseModel):
    name: str = Field(..., example="user1")
    email: EmailStr = Field(..., example="user1@example.com")
    password: str = Field(..., min_length=8, example="strongpassword")

# ユーザーデータを読み取る際に使用するスキーマ
class UserRead(BaseModel):
    id: int
    name: str
    email: EmailStr

    class Config:
        orm_mode = True

# ユーザー認証（ログイン）に使用するスキーマ
class UserLogin(BaseModel):
    username: str = Field(..., example="user1")
    password: str = Field(..., min_length=8, example="strongpassword")