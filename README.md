# TIL — Today I Learned

工程師日常學習筆記，記錄每天在工作中遇到的新名詞、概念與實作。
涵蓋後端開發、資料庫、AWS 雲端架構、Python 生態系等主題。

> 筆記原則：每個概念都附上實際例子與可執行的程式碼，把自己當成什麼都不會的人來寫。

---

## 📁 結構

```
.
├── notes/                  # 主題式學習筆記
│   ├── aws/                # AWS 雲端相關
│   ├── pythonnote.md       # Python 語法基礎
│   ├── backend-basics.md   # HTTP、REST API
│   ├── database-basics.md  # SQL、資料庫概念
│   ├── sqlalchemy.md       # ORM、SQLAlchemy
│   └── fastapi.md          # FastAPI 框架
│
└── 2026/                   # 每日速記與名詞解釋（依年月分類）
    └── 05/
        ├── 05note.md       # 當月每日速記（原始名詞）
        └── 05-glossary.md  # 展開的詳細解釋
```

---

## 📚 主題式筆記

### Python & 後端
| 檔案 | 內容 |
|------|------|
| [pythonnote.md](./notes/pythonnote.md) | Python 語法入門（變數、函式、class、迴圈等） |
| [backend-basics.md](./notes/backend-basics.md) | HTTP、REST API、request/response 概念 |
| [database-basics.md](./notes/database-basics.md) | SQL、table/column/relation 概念 |
| [sqlalchemy.md](./notes/sqlalchemy.md) | ORM 是什麼、SQLAlchemy 怎麼用 |
| [fastapi.md](./notes/fastapi.md) | FastAPI 路由、依賴注入、Pydantic |

### AWS
| 檔案 | 內容 |
|------|------|
| [aws-networking.md](./notes/aws/aws-networking.md) | VPC、Subnet、Security Group、Route Table |
| [step-functions.md](./notes/aws/step-functions.md) | AWS Step Functions 狀態機 |
| [aws-chatbot-practice.md](./notes/aws/aws-chatbot-practice.md) | AWS Chatbot 實作練習 |

---

## 📅 每日名詞筆記（TIL）

每天上班聽到來不及查的名詞，下班後整理成詳細解釋。

| 速記檔 | 解釋檔 |
|--------|--------|
| [2026/05/05note.md](./2026/05/05note.md) | [2026/05/05-glossary.md](./2026/05/05-glossary.md) |

---

## 🗺️ 建議閱讀順序（新手）

1. [pythonnote.md](./notes/pythonnote.md) — 先熟悉 Python 語法基礎
2. [backend-basics.md](./notes/backend-basics.md) — 搞懂 HTTP 和 REST
3. [database-basics.md](./notes/database-basics.md) — 理解資料庫結構
4. [sqlalchemy.md](./notes/sqlalchemy.md) — ORM 概念 + SQLAlchemy 實作
5. [fastapi.md](./notes/fastapi.md) — FastAPI 框架細節
6. [aws-networking.md](./notes/aws/aws-networking.md) — 進入 AWS 雲端世界
