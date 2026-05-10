# 後端 API 基礎概念

## 1. 什麼是後端？

一個 Web 應用通常分兩層：

```
使用者的瀏覽器 / App（前端）
        ↕  透過網路傳送請求
    你的伺服器（後端）
        ↕  讀寫資料
      資料庫
```

**前端**負責畫面，**後端**負責邏輯和資料。你寫的 FastAPI 程式就是後端。

---

## 2. HTTP 是什麼？

HTTP（HyperText Transfer Protocol）是前後端溝通的語言規則。

每次溝通都是一組「問答」：

- **Request（請求）**：前端發出，說「我要什麼」
- **Response（回應）**：後端回覆，說「給你結果」

### Request 的組成

```
方法   路徑          版本
GET   /users/42    HTTP/1.1
Host: api.example.com
Authorization: Bearer abc123    ← Headers（附加資訊）

{"name": "Alice"}               ← Body（資料，GET 通常沒有）
```

### Response 的組成

```
HTTP/1.1  200  OK               ← 狀態碼
Content-Type: application/json  ← Headers

{"id": 42, "name": "Alice"}     ← Body（回傳的資料）
```

---

## 3. HTTP 方法（Methods）

| 方法 | 用途 | 對應操作 |
|------|------|----------|
| `GET` | 取得資料 | 讀取（Read） |
| `POST` | 新增資料 | 建立（Create） |
| `PUT` | 完整更新 | 更新（Update） |
| `PATCH` | 部分更新 | 更新（Update） |
| `DELETE` | 刪除資料 | 刪除（Delete） |

---

## 4. HTTP 狀態碼

後端用數字告訴前端「這次請求的結果」：

| 範圍 | 意思 | 常見例子 |
|------|------|----------|
| 2xx | 成功 | `200 OK`、`201 Created` |
| 4xx | 客戶端錯誤 | `400 Bad Request`、`404 Not Found`、`422 Unprocessable Entity` |
| 5xx | 伺服器錯誤 | `500 Internal Server Error` |

---

## 5. REST API 是什麼？

REST 是一種設計 API 的風格（不是技術，是約定）。

核心概念：**用 URL 表示資源，用 HTTP 方法表示動作**。

### 範例：使用者資源

| 動作 | 方法 | URL |
|------|------|-----|
| 取得所有使用者 | `GET` | `/users` |
| 取得單一使用者 | `GET` | `/users/{id}` |
| 新增使用者 | `POST` | `/users` |
| 更新使用者 | `PUT` | `/users/{id}` |
| 刪除使用者 | `DELETE` | `/users/{id}` |

### 好的 REST 設計原則

- URL 用名詞，不用動詞（`/users` 而不是 `/getUsers`）
- 用複數（`/users` 而不是 `/user`）
- 巢狀資源用斜線（`/users/42/posts` 表示使用者 42 的文章）

---

## 6. FastAPI 對應範例

```python
from fastapi import FastAPI

app = FastAPI()

# GET /users → 取得所有使用者
@app.get("/users")
def get_users():
    return [{"id": 1, "name": "Alice"}]

# GET /users/{user_id} → 取得單一使用者
@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {"id": user_id, "name": "Alice"}

# POST /users → 新增使用者
@app.post("/users", status_code=201)
def create_user(name: str):
    return {"id": 2, "name": name}
```

FastAPI 會自動：
- 解析 URL 參數（`user_id`）
- 驗證型別（`int`）
- 產生 `/docs` 互動文件

---

## 重點整理

- HTTP 是前後端溝通的協定，每次溝通是一組 request/response
- HTTP 方法（GET/POST/PUT/DELETE）對應 CRUD 操作
- 狀態碼告訴前端請求結果（2xx 成功、4xx 客戶端錯誤、5xx 伺服器錯誤）
- REST 是設計 API 的風格：URL 表示資源，方法表示動作
