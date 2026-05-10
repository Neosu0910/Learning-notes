# 資料庫基礎概念

## 1. 為什麼需要資料庫？

程式的變數在程式關掉後就消失了。資料庫讓資料**持久保存**，下次啟動還在。

---

## 2. 關聯式資料庫的結構

關聯式資料庫（如 PostgreSQL、MySQL、SQLite）把資料存在**表格（Table）**裡。

### Table（資料表）

就像 Excel 的一張工作表：

```
users 資料表
┌────┬──────────┬─────────────────────┐
│ id │ name     │ email               │
├────┼──────────┼─────────────────────┤
│  1 │ Alice    │ alice@example.com   │
│  2 │ Bob      │ bob@example.com     │
│  3 │ Charlie  │ charlie@example.com │
└────┴──────────┴─────────────────────┘
```

- **Table（資料表）**：一個主題的資料集合（例如 `users`、`posts`）
- **Column（欄位）**：資料的屬性（例如 `id`、`name`、`email`）
- **Row（列）**：一筆完整的資料記錄

### Primary Key（主鍵）

每張表通常有一個唯一識別欄位，叫做 **Primary Key（PK）**。

- 通常是 `id`，自動遞增（1, 2, 3...）
- 確保每筆資料都能被唯一識別
- 不能重複、不能是 NULL

---

## 3. 資料表之間的關係（Relations）

真實世界的資料彼此有關聯。

### 一對多（One-to-Many）

一個使用者可以有多篇文章：

```
users                    posts
┌────┬───────┐           ┌────┬─────────────┬─────────┐
│ id │ name  │           │ id │ title       │ user_id │
├────┼───────┤           ├────┼─────────────┼─────────┤
│  1 │ Alice │           │  1 │ Hello World │    1    │ ← Alice 的文章
│  2 │ Bob   │           │  2 │ FastAPI 入門│    1    │ ← Alice 的文章
└────┴───────┘           │  3 │ SQL 筆記    │    2    │ ← Bob 的文章
                         └────┴─────────────┴─────────┘
```

`posts.user_id` 是 **Foreign Key（外鍵）**，指向 `users.id`。

### 多對多（Many-to-Many）

一篇文章可以有多個標籤，一個標籤也可以屬於多篇文章。
需要一張**中間表**：

```
posts ←── post_tags ──→ tags
```

```sql
-- 中間表
post_tags
┌─────────┬────────┐
│ post_id │ tag_id │
├─────────┼────────┤
│    1    │    1   │
│    1    │    2   │
│    2    │    1   │
└─────────┴────────┘
```

---

## 4. SQL 基礎語法

SQL（Structured Query Language）是操作資料庫的語言。

### 建立資料表

```sql
CREATE TABLE users (
    id    INTEGER PRIMARY KEY AUTOINCREMENT,
    name  TEXT    NOT NULL,
    email TEXT    UNIQUE NOT NULL
);
```

### 新增資料（INSERT）

```sql
INSERT INTO users (name, email)
VALUES ('Alice', 'alice@example.com');
```

### 查詢資料（SELECT）

```sql
-- 取得所有使用者
SELECT * FROM users;

-- 取得特定欄位
SELECT id, name FROM users;

-- 加條件
SELECT * FROM users WHERE id = 1;

-- 排序
SELECT * FROM users ORDER BY name ASC;

-- 限制筆數
SELECT * FROM users LIMIT 10;
```

### 更新資料（UPDATE）

```sql
UPDATE users
SET name = 'Alicia'
WHERE id = 1;
```

> ⚠️ 沒有 `WHERE` 的 UPDATE 會更新**所有**資料，要小心！

### 刪除資料（DELETE）

```sql
DELETE FROM users WHERE id = 1;
```

> ⚠️ 沒有 `WHERE` 的 DELETE 會刪除**所有**資料！

### JOIN（跨表查詢）

```sql
-- 取得每篇文章和作者名稱
SELECT posts.title, users.name AS author
FROM posts
JOIN users ON posts.user_id = users.id;
```

---

## 5. 常見資料型別

| SQL 型別 | 說明 | Python 對應 |
|----------|------|-------------|
| `INTEGER` | 整數 | `int` |
| `TEXT` / `VARCHAR` | 字串 | `str` |
| `FLOAT` / `REAL` | 浮點數 | `float` |
| `BOOLEAN` | 布林值 | `bool` |
| `DATETIME` | 日期時間 | `datetime` |
| `JSON` | JSON 資料 | `dict` |

---

## 重點整理

- 資料庫讓資料持久保存
- 資料存在 Table（表）裡，Table 有 Column（欄）和 Row（列）
- Primary Key 唯一識別每筆資料
- Foreign Key 建立表與表之間的關聯
- SQL 是操作資料庫的語言（SELECT / INSERT / UPDATE / DELETE）
