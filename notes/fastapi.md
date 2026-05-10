# FastAPI 基礎

## 1. FastAPI 是什麼？

FastAPI 是一個現代 Python Web 框架，特點：

- **快速**：效能接近 Node.js / Go
- **自動文件**：自動產生 `/docs`（Swagger UI）和 `/redoc`
- **型別驗證**：整合 Pydantic，自動驗證 request/response 資料
- **非同步支援**：原生支援 `async/await`

---

## 2. 路由（Routes）

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")           # HTTP 方法 + 路徑
def read_root():
    return {"message": "Hello World"}
```

### 路徑參數

```python
@app.get("/users/{user_id}")
def get_user(user_id: int):   # FastAPI 自動把字串轉成 int，型別錯誤會回 422
    return {"user_id": user_id}
```

### Query 參數

```python
@app.get("/users")
def list_users(skip: int = 0, limit: int = 10):
    # 對應 GET /users?skip=0&limit=10
    return {"skip": skip, "limit": limit}
```

---

## 3. Pydantic Schema（資料驗證）

Pydantic 讓你定義資料的「形狀」，FastAPI 用它驗證 request body 和格式化 response。

```python
from pydantic import BaseModel

class UserCreate(BaseModel):
    name: str
    email: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str

    model_config = {"from_attributes": True}  # 允許從 ORM 物件轉換
```

### 在路由中使用

```python
@app.post("/users", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    #            ↑ 自動從 request body 解析並驗證
    db_user = User(name=user.name, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user  # FastAPI 用 UserResponse 格式化輸出
```

### Schema vs Model 的差別

| | SQLAlchemy Model | Pydantic Schema |
|---|---|---|
| 用途 | 對應資料庫表格 | 驗證 API 輸入/輸出 |
| 位置 | `models.py` | `schemas.py` |
| 範例 | `class User(Base)` | `class UserResponse(BaseModel)` |

通常一個資源會有多個 Schema：
- `UserCreate`：建立時的輸入（不含 id）
- `UserUpdate`：更新時的輸入（欄位可選）
- `UserResponse`：回傳給前端的格式（含 id）

---

## 4. 依賴注入（Dependency Injection）

`Depends()` 讓你把共用邏輯抽出來，FastAPI 自動執行並注入結果。

```python
from fastapi import Depends

# 定義依賴
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 注入到路由
@app.get("/users")
def list_users(db: Session = Depends(get_db)):
    return db.query(User).all()
```

常見用途：
- 資料庫 Session（`get_db`）
- 驗證登入狀態（`get_current_user`）
- 共用的查詢參數

---

## 5. 錯誤處理

```python
from fastapi import HTTPException

@app.get("/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

`HTTPException` 會自動回傳對應的 HTTP 狀態碼和錯誤訊息。

---

## 6. 自動文件

啟動後直接開瀏覽器：

- `http://localhost:8000/docs` → Swagger UI（可互動測試）
- `http://localhost:8000/redoc` → ReDoc（閱讀用）

---

## 7. 啟動應用

```bash
uvicorn app.main:app --reload
#        ↑模組路徑  ↑FastAPI 實例  ↑開發模式（檔案變更自動重啟）
```

---

## 重點整理

- 路由用裝飾器定義（`@app.get`、`@app.post` 等）
- Pydantic Schema 負責驗證輸入、格式化輸出
- SQLAlchemy Model 和 Pydantic Schema 是不同的東西，各司其職
- `Depends()` 處理共用邏輯（Session、認證等）
- FastAPI 自動產生互動式 API 文件

## DTO
DTO（Data Transfer Object） 是一個設計模式的術語，意思是「專門用來傳遞資料的物件」，不包含業務邏輯。在 FastAPI 專案裡，通常會把 Pydantic model 放在 dto/ 資料夾，用來定義 API 的 request/response 格式。