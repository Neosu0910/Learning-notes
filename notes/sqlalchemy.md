# ORM 與 SQLAlchemy

## 1. ORM 是什麼？

ORM（Object-Relational Mapping，物件關聯對映）讓你用 **Python 物件**操作資料庫，不用直接寫 SQL。

### 沒有 ORM（直接寫 SQL）

```python
import sqlite3

conn = sqlite3.connect("app.db")
cursor = conn.cursor()

# 查詢
cursor.execute("SELECT * FROM users WHERE id = ?", (1,))
row = cursor.fetchone()
user = {"id": row[0], "name": row[1], "email": row[2]}  # 手動對應欄位
```

### 有 ORM（SQLAlchemy）

```python
user = db.query(User).filter(User.id == 1).first()
print(user.name)  # 直接用屬性存取
```

ORM 幫你：
- 把 Python class 對應到資料表
- 把 Python 物件對應到資料列
- 自動產生 SQL，你只寫 Python

---

## 2. SQLAlchemy 核心概念

### Model（模型）= 資料表的 Python 對應

```python
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"          # 對應資料表名稱

    id    = Column(Integer, primary_key=True, index=True)
    name  = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
```

對應關係：

```
Python class User   ←→   資料表 users
Python attribute id ←→   欄位 id (INTEGER PRIMARY KEY)
Python instance     ←→   一筆資料列（row）
```

### Engine（引擎）= 資料庫連線

```python
from sqlalchemy import create_engine

# SQLite（開發用，存成本地檔案）
engine = create_engine("sqlite:///./app.db")

# PostgreSQL（正式環境）
# engine = create_engine("postgresql://user:password@localhost/dbname")
```

### Session（會話）= 操作資料庫的工作單元

Session 是你跟資料庫溝通的「工作視窗」。所有的查詢和修改都透過它進行。

```python
from sqlalchemy.orm import sessionmaker

SessionLocal = sessionmaker(bind=engine)

# 使用 Session
db = SessionLocal()
try:
    # 在這裡做資料庫操作
    users = db.query(User).all()
finally:
    db.close()  # 記得關閉
```

---

## 3. 基本 CRUD 操作

### Create（新增）

```python
new_user = User(name="Alice", email="alice@example.com")
db.add(new_user)
db.commit()        # 提交到資料庫
db.refresh(new_user)  # 重新載入（取得資料庫產生的 id）
print(new_user.id)    # 現在有 id 了
```

### Read（查詢）

```python
# 取得所有
users = db.query(User).all()

# 條件查詢
user = db.query(User).filter(User.id == 1).first()

# 多個條件
user = db.query(User).filter(
    User.name == "Alice",
    User.email.like("%@example.com")
).first()

# 排序 + 分頁
users = db.query(User).order_by(User.name).offset(0).limit(10).all()
```

### Update（更新）

```python
user = db.query(User).filter(User.id == 1).first()
user.name = "Alicia"
db.commit()
```

### Delete（刪除）

```python
user = db.query(User).filter(User.id == 1).first()
db.delete(user)
db.commit()
```

---

## 4. 關聯（Relationships）

### 一對多：User 有多個 Post

```python
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"
    id    = Column(Integer, primary_key=True)
    name  = Column(String)

    posts = relationship("Post", back_populates="author")  # 反向關聯

class Post(Base):
    __tablename__ = "posts"
    id      = Column(Integer, primary_key=True)
    title   = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))      # 外鍵

    author = relationship("User", back_populates="posts")  # 反向關聯
```

使用方式：

```python
user = db.query(User).filter(User.id == 1).first()
print(user.posts)        # 取得該使用者的所有文章（自動 JOIN）

post = db.query(Post).filter(Post.id == 1).first()
print(post.author.name)  # 取得文章作者名稱
```

---

## 5. 在 FastAPI 中整合 SQLAlchemy

### 專案結構

```
app/
├── main.py          ← FastAPI 應用
├── database.py      ← 資料庫設定
├── models.py        ← SQLAlchemy Models
└── schemas.py       ← Pydantic Schemas（資料驗證）
```

### database.py

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DATABASE_URL = "sqlite:///./app.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

# FastAPI 依賴注入用的 Session 工廠
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### main.py

```python
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, database

app = FastAPI()

# 建立資料表（開發用，正式環境用 Alembic migration）
models.Base.metadata.create_all(bind=database.engine)

@app.get("/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(database.get_db)):
    #                              ↑ FastAPI 自動注入 Session
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

### `Depends(get_db)` 的作用

FastAPI 的依賴注入系統會：
1. 在每個 request 開始時呼叫 `get_db()`，建立新的 Session
2. 把 Session 傳給你的函式
3. Request 結束後自動執行 `finally: db.close()`

你不需要手動管理 Session 的生命週期。

---

## 6. SQLAlchemy vs 直接寫 SQL 比較

| | 直接寫 SQL | SQLAlchemy ORM |
|---|---|---|
| 學習曲線 | 需要熟悉 SQL | 需要熟悉 ORM 概念 |
| 程式碼風格 | SQL 字串 | Python 物件 |
| 型別安全 | 無 | 有（搭配 Pydantic） |
| 複雜查詢 | 直觀 | 有時較繁瑣 |
| 資料庫切換 | 需改 SQL | 通常只改連線字串 |

---

## 重點整理

- ORM 讓你用 Python 物件操作資料庫，不用直接寫 SQL
- SQLAlchemy Model = 資料表的 Python 對應
- Session 是操作資料庫的工作單元，記得 commit 和 close
- `relationship()` 讓你直接用屬性存取關聯資料
- FastAPI 用 `Depends(get_db)` 自動管理 Session 生命週期
