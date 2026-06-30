# Docker & Docker Compose 完整學習筆記

## 目錄
1. [Docker 是什麼](#docker-是什麼)
2. [核心概念](#核心概念)
3. [Dockerfile 完整教學](#dockerfile-完整教學)
4. [Build Image](#build-image)
5. [Run Container](#run-container)
6. [打包與推送 Image](#打包與推送-image)
7. [Docker Compose](#docker-compose)
8. [實戰範例：FastAPI + PostgreSQL](#實戰範例fastapi--postgresql)
9. [常用指令速查](#常用指令速查)
10. [Best Practices](#best-practices)

---

## Docker 是什麼

**一句話：** 把你的程式 + 所有依賴打包成一個可移植的「容器」，在任何地方都能跑。

### 解決什麼問題？

| 沒有 Docker | 有 Docker |
|---|---|
| 「我這邊跑得好好的啊」 | 環境一致，你跑得動就哪裡都跑得動 |
| 裝 Python 3.11 結果伺服器是 3.8 | Image 裡固定版本 |
| 多個專案依賴互相衝突 | 每個 container 是獨立環境 |
| 部署要寫一堆安裝步驟文件 | 一個 Dockerfile 搞定 |

### Docker vs 虛擬機 (VM)

```
VM:                          Docker Container:
┌─────────────────┐          ┌─────────────────┐
│   你的 App      │          │   你的 App      │
├─────────────────┤          ├─────────────────┤
│   Guest OS      │          │   (沒有 OS！)   │
├─────────────────┤          ├─────────────────┤
│   Hypervisor    │          │   Docker Engine │
├─────────────────┤          ├─────────────────┤
│   Host OS       │          │   Host OS       │
└─────────────────┘          └─────────────────┘
啟動要幾分鐘                   啟動只要幾秒
占 GB 級記憶體                 占 MB 級記憶體
```

---

## 核心概念

### 三個最重要的東西

```
Dockerfile  →(build)→  Image  →(run)→  Container
  (食譜)                (冷凍食品)        (正在吃的那盤菜)
```

| 概念 | 比喻 | 說明 |
|---|---|---|
| **Dockerfile** | 食譜 | 一份文字檔，描述怎麼打包你的 app |
| **Image** | 冷凍食品 | build 出來的成品，不可變，可以分享 |
| **Container** | 正在跑的實例 | 從 image 啟動的 process，可以有很多個 |

### 其他重要概念

| 概念 | 說明 |
|---|---|
| **Registry** | 存放 image 的倉庫（Docker Hub, ECR, GCR） |
| **Volume** | 持久化資料（container 刪了資料還在） |
| **Network** | container 之間的網路溝通 |
| **Tag** | image 的版本標籤（例如 `nginx:1.25` 或 `my-app:latest`） |
| **Layer** | Image 由多層組成，每條 Dockerfile 指令 = 一層 |

---

## Dockerfile 完整教學

### 最簡單的 Dockerfile

```dockerfile
# 用官方 Python 3.11 作為基底
FROM python:3.11-slim

# 設定工作目錄
WORKDIR /app

# 複製檔案到 container 裡
COPY . .

# 安裝依賴
RUN pip install -r requirements.txt

# 告訴 Docker 這個 container 用 8000 port
EXPOSE 8000

# container 啟動時執行的指令
CMD ["python", "main.py"]
```

### 每一行指令詳解

#### FROM — 選擇基底 image

```dockerfile
# 完整格式: FROM image:tag
FROM python:3.11-slim     # Python 官方 image，slim 版比較小
FROM node:20-alpine       # Node.js，alpine 版更小（基於 Alpine Linux）
FROM ubuntu:22.04         # 完整的 Ubuntu
FROM scratch              # 空白 image（用於 Go binary 等不需要 OS 的情況）
```

**怎麼選？**
- `-slim`：去掉不必要的工具，適合多數情況
- `-alpine`：最小的 Linux，但有時套件相容性問題
- 無後綴：完整版，最大但最不會出問題

#### WORKDIR — 設定工作目錄

```dockerfile
WORKDIR /app
# 之後的 COPY, RUN, CMD 都在 /app 底下執行
# 如果目錄不存在會自動建立
```

#### COPY vs ADD — 複製檔案

```dockerfile
COPY requirements.txt .          # 複製單一檔案
COPY . .                         # 複製整個目錄
COPY --chown=1000:1000 . .       # 複製並設定擁有者

# ADD 多了兩個功能（但通常用 COPY 就好）:
ADD archive.tar.gz /app/         # 自動解壓縮
ADD https://example.com/file .   # 下載 URL（不建議，用 RUN curl）
```

#### RUN — 在 build 時執行指令

```dockerfile
# 安裝套件
RUN pip install -r requirements.txt

# 多條指令合併（減少 layer 數量）
RUN apt-get update && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*

# 建立使用者（安全性 best practice）
RUN adduser --disabled-password --gecos "" appuser
```

#### ENV — 設定環境變數

```dockerfile
ENV PYTHONUNBUFFERED=1
ENV APP_ENV=production
ENV PORT=8000

# container 裡的程式可以讀到這些變數
# Python: os.environ["APP_ENV"]
```

#### ARG — Build 時的變數（不會留在最終 image）

```dockerfile
ARG PYTHON_VERSION=3.11
FROM python:${PYTHON_VERSION}-slim

# build 時傳入: docker build --build-arg PYTHON_VERSION=3.12 .
```

#### EXPOSE — 宣告使用的 port

```dockerfile
EXPOSE 8000
# 這只是「文件」作用，實際要在 run 時 -p 映射才有效
# docker run -p 8000:8000 my-app
```

#### CMD vs ENTRYPOINT — container 啟動時執行什麼

```dockerfile
# CMD: container 預設要跑的指令（可以被 docker run 覆蓋）
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# ENTRYPOINT: 固定的執行入口（不容易被覆蓋）
ENTRYPOINT ["python"]
CMD ["main.py"]
# → 預設跑 python main.py
# → docker run my-app test.py → 跑 python test.py（只覆蓋 CMD）
```

**常見組合：**
```dockerfile
# Web app: 直接用 CMD
CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]

# CLI 工具: ENTRYPOINT 固定程式，CMD 當預設參數
ENTRYPOINT ["aws"]
CMD ["--help"]
```

#### USER — 切換執行身分

```dockerfile
# 不要用 root 跑你的 app（安全性）
RUN adduser --disabled-password appuser
USER appuser
```

#### .dockerignore — 排除不需要的檔案

在專案根目錄建立 `.dockerignore`：
```
.git
.venv
__pycache__
*.pyc
.env
node_modules
.DS_Store
```

### 完整 Dockerfile 範例：Python FastAPI

```dockerfile
# ==============================================================
# Stage 1: 安裝依賴（Multi-stage build）
# ==============================================================
FROM python:3.11-slim AS builder

WORKDIR /app

# 先複製 requirements，利用 Docker layer cache
# 只有 requirements.txt 改了才會重新安裝
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ==============================================================
# Stage 2: 最終 image（更小、更乾淨）
# ==============================================================
FROM python:3.11-slim

# 安全性: 不用 root
RUN adduser --disabled-password --gecos "" appuser

WORKDIR /app

# 從 builder stage 複製已安裝的套件
COPY --from=builder /root/.local /home/appuser/.local

# 複製程式碼
COPY . .

# 設定 PATH 讓 user 安裝的套件可以被找到
ENV PATH=/home/appuser/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

# 切換到非 root 使用者
USER appuser

EXPOSE 8000

# 健康檢查（ECS 和 Docker Compose 都支援）
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Multi-stage Build 為什麼重要？

```
沒有 multi-stage:
  base image (200MB) + build tools (300MB) + 你的 code (50MB) = 550MB

有 multi-stage:
  base image (200MB) + 你的 code + 依賴 (80MB) = 280MB
```

Build 工具（gcc, make 等）只在編譯時需要，不應該出現在最終 image 裡。

---

## Build Image

### 基本 build

```bash
# 在 Dockerfile 所在目錄執行
docker build -t my-app .

# 解析:
# docker build     → 建立 image
# -t my-app        → 給 image 取名（tag）
# .                → Dockerfile 的位置（build context）
```

### 帶版本的 build

```bash
# 加版本 tag
docker build -t my-app:1.0.0 .
docker build -t my-app:latest .

# 同時打多個 tag
docker build -t my-app:1.0.0 -t my-app:latest .
```

### 指定不同的 Dockerfile

```bash
docker build -f Dockerfile.prod -t my-app:prod .
docker build -f deploy/Dockerfile -t my-app .
```

### 傳入 build arguments

```bash
docker build --build-arg PYTHON_VERSION=3.12 -t my-app .
docker build --build-arg ENV=production --build-arg PORT=3000 -t my-app .
```

### 針對不同平台 build（M1 Mac → Linux server）

```bash
# 你的 Mac 是 ARM，但 AWS ECS 跑 AMD64
docker build --platform linux/amd64 -t my-app .

# 或同時 build 多平台
docker buildx build --platform linux/amd64,linux/arm64 -t my-app .
```

### 查看 build 的 image

```bash
docker images
# REPOSITORY   TAG       IMAGE ID       CREATED         SIZE
# my-app       latest    abc123def456   5 seconds ago   280MB
# my-app       1.0.0     abc123def456   5 seconds ago   280MB
```

---

## Run Container

### 基本 run

```bash
docker run my-app
# 直接跑，log 會印在終端機，Ctrl+C 停止
```

### 常用參數組合

```bash
# 最常用: 背景執行 + port 映射 + 自動刪除
docker run -d -p 8000:8000 --rm --name my-app-container my-app

# 參數解析:
# -d           → detach，背景執行（不佔住終端機）
# -p 8000:8000 → host port:container port 映射
# --rm         → container 停止後自動刪除
# --name       → 給 container 取名（方便後續操作）
```

### 傳入環境變數

```bash
# 單一變數
docker run -e DB_HOST=localhost -e DB_PORT=5432 my-app

# 從檔案讀取（不要把 .env commit 到 git）
docker run --env-file .env my-app
```

### 掛載 Volume（持久化資料）

```bash
# Bind mount: 本機目錄 ↔ container 目錄（開發用）
docker run -v $(pwd):/app my-app
# 本機的 code 改了，container 裡也會即時改變

# Named volume: Docker 管理的持久儲存（資料庫用）
docker run -v postgres_data:/var/lib/postgresql/data postgres
```

### 進入正在跑的 container（偵錯用）

```bash
# 開一個 shell 進去看
docker exec -it my-app-container /bin/bash

# 如果是 alpine image（沒有 bash）
docker exec -it my-app-container /bin/sh

# 只執行一個指令
docker exec my-app-container ls /app
```

### 查看 container 狀態

```bash
# 列出正在跑的 container
docker ps

# 列出全部（包括停止的）
docker ps -a

# 查看 log
docker logs my-app-container
docker logs -f my-app-container    # -f 持續追蹤（像 tail -f）
docker logs --tail 50 my-app-container  # 只看最後 50 行

# 查看資源使用
docker stats
```

### 停止和刪除

```bash
docker stop my-app-container     # 優雅停止（送 SIGTERM）
docker kill my-app-container     # 強制停止（送 SIGKILL）
docker rm my-app-container       # 刪除 container
docker rm -f my-app-container    # 強制刪除（即使在跑）
```

---

## 打包與推送 Image

### 推送到 Docker Hub

```bash
# 1. 登入
docker login

# 2. Tag image（Docker Hub 格式: username/repo:tag）
docker tag my-app:latest neosu/my-app:1.0.0
docker tag my-app:latest neosu/my-app:latest

# 3. Push
docker push neosu/my-app:1.0.0
docker push neosu/my-app:latest
```

### 推送到 AWS ECR（ECS 部署用這個）

```bash
# 1. 取得 ECR 登入憑證
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com

# 2. 建立 ECR repository（第一次才需要）
aws ecr create-repository --repository-name my-app --region us-east-1

# 3. Build image（指定平台，因為 ECS 跑 linux/amd64）
docker build --platform linux/amd64 -t my-app .

# 4. Tag 成 ECR 格式
docker tag my-app:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/my-app:1.0.0
docker tag my-app:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/my-app:latest

# 5. Push 到 ECR
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/my-app:1.0.0
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/my-app:latest
```

### 匯出/匯入 Image（離線傳輸）

```bash
# 存成 tar 檔案
docker save my-app:latest -o my-app.tar

# 從 tar 載入
docker load -i my-app.tar
```

### 完整 CI/CD 流程圖

```
開發者 push code
    ↓
CI (GitHub Actions / CodePipeline)
    ↓
docker build → docker tag → docker push to ECR
    ↓
更新 ECS Task Definition (新的 image tag)
    ↓
ECS Service 做 rolling update
    ↓
新版本上線
```

---

## Docker Compose

### 是什麼？

**一句話：** 用一個 `docker-compose.yml` 檔案同時管理多個 container。

適用情境：
- 本地開發：app + database + redis 一起跑
- 測試環境：一個指令啟動整套服務
- 不適合正式部署（正式用 ECS / Kubernetes）

### 基本結構

```yaml
# docker-compose.yml
version: "3.9"

services:
  # 服務 1: 你的 app
  app:
    build: .                    # 用當前目錄的 Dockerfile build
    ports:
      - "8000:8000"            # host:container
    environment:
      - DB_HOST=db
      - DB_PORT=5432
    depends_on:
      - db                     # 確保 db 先啟動

  # 服務 2: PostgreSQL
  db:
    image: postgres:15         # 直接用現成 image
    environment:
      - POSTGRES_USER=admin
      - POSTGRES_PASSWORD=secret
      - POSTGRES_DB=myapp
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:               # 宣告 named volume
```

### Docker Compose 常用指令

```bash
# 啟動所有服務（背景）
docker compose up -d

# 啟動並重新 build image
docker compose up -d --build

# 查看 log
docker compose logs
docker compose logs -f app      # 只看 app 的 log

# 停止所有服務
docker compose down

# 停止並刪除 volumes（清除資料庫資料）
docker compose down -v

# 只啟動特定服務
docker compose up -d db

# 查看狀態
docker compose ps

# 進入某個 container
docker compose exec app /bin/bash

# 執行一次性指令（例如跑 migration）
docker compose run --rm app python manage.py migrate
```

### services 區塊詳解

```yaml
services:
  app:
    # === 來源（二選一） ===
    build: .                          # 從 Dockerfile build
    # image: my-app:latest            # 或直接用現有 image

    # === 進階 build 設定 ===
    build:
      context: .                      # build context 路徑
      dockerfile: Dockerfile.dev      # 指定 Dockerfile
      args:
        - PYTHON_VERSION=3.12         # build args
      target: development             # multi-stage 只 build 到某個 stage

    # === 網路 ===
    ports:
      - "8000:8000"                   # host:container
      - "9229:9229"                   # debug port
    expose:
      - "8000"                        # 只在 compose network 內開放

    # === 環境變數 ===
    environment:
      DB_HOST: db
      DEBUG: "true"
    env_file:
      - .env                          # 從檔案讀取

    # === 資料掛載 ===
    volumes:
      - .:/app                        # bind mount（開發用，即時同步）
      - /app/node_modules             # 排除 node_modules
      - data_volume:/app/data         # named volume

    # === 啟動順序 ===
    depends_on:
      db:
        condition: service_healthy    # 等 db 健康檢查通過才啟動

    # === 健康檢查 ===
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 10s

    # === 重啟策略 ===
    restart: unless-stopped           # 除非手動停止，否則自動重啟

    # === 資源限制 ===
    deploy:
      resources:
        limits:
          cpus: "0.5"
          memory: 512M
```

---

## 實戰範例：FastAPI + PostgreSQL + Redis

### 專案結構

```
my-project/
├── docker-compose.yml
├── docker-compose.prod.yml    # 正式環境覆蓋設定
├── Dockerfile
├── Dockerfile.dev             # 開發用（有 hot reload）
├── .dockerignore
├── .env.example
├── requirements.txt
├── main.py
└── alembic/                   # DB migration
```

### Dockerfile（正式環境）

```dockerfile
FROM python:3.11-slim AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.11-slim

RUN adduser --disabled-password appuser
WORKDIR /app

COPY --from=builder /root/.local /home/appuser/.local
COPY . .

ENV PATH=/home/appuser/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

USER appuser
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Dockerfile.dev（開發環境，有 hot reload）

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 開發環境不 COPY code，用 volume mount 即時同步
# COPY . .  ← 不需要

ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# --reload: 檔案改了自動重啟
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

### docker-compose.yml（開發環境）

```yaml
version: "3.9"

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile.dev
    ports:
      - "8000:8000"
    volumes:
      - .:/app                     # 即時同步 code
    environment:
      - DATABASE_URL=postgresql://admin:secret@db:5432/myapp
      - REDIS_URL=redis://redis:6379/0
      - ENV=development
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: secret
      POSTGRES_DB: myapp
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U admin -d myapp"]
      interval: 5s
      timeout: 3s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### docker-compose.prod.yml（正式環境覆蓋）

```yaml
# 用法: docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
version: "3.9"

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile       # 用正式版 Dockerfile
    volumes: []                     # 不要 mount 本地 code
    environment:
      - ENV=production
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: "1.0"
          memory: 1G

  db:
    ports: []                       # 正式環境不對外開放 DB port
```

### 開發工作流程

```bash
# 第一次啟動
docker compose up -d --build

# 看 app 的 log
docker compose logs -f app

# 改了 requirements.txt 後重新 build
docker compose up -d --build app

# 跑 DB migration
docker compose exec app alembic upgrade head

# 進 DB 看資料
docker compose exec db psql -U admin -d myapp

# 清掉全部重來
docker compose down -v
```

---

## 常用指令速查

### Image 操作

| 指令 | 用途 |
|---|---|
| `docker build -t name:tag .` | Build image |
| `docker images` | 列出所有 image |
| `docker rmi image_name` | 刪除 image |
| `docker image prune` | 刪除沒在用的 image |
| `docker tag source target` | 幫 image 加 tag |
| `docker push name:tag` | 推送到 registry |
| `docker pull name:tag` | 從 registry 拉 |

### Container 操作

| 指令 | 用途 |
|---|---|
| `docker run -d -p 8000:8000 image` | 背景執行 |
| `docker ps` | 列出執行中的 container |
| `docker ps -a` | 列出全部 container |
| `docker logs -f container` | 追蹤 log |
| `docker exec -it container bash` | 進入 container |
| `docker stop container` | 停止 |
| `docker rm container` | 刪除 |
| `docker rm -f $(docker ps -aq)` | 刪除全部 container |

### 清理

| 指令 | 用途 |
|---|---|
| `docker system prune` | 清除所有沒在用的東西 |
| `docker system prune -a` | 更激進的清理（含未使用 image） |
| `docker volume prune` | 清除沒在用的 volume |
| `docker system df` | 查看 Docker 占了多少空間 |

### Docker Compose 操作

| 指令 | 用途 |
|---|---|
| `docker compose up -d` | 背景啟動所有服務 |
| `docker compose up -d --build` | 重新 build 後啟動 |
| `docker compose down` | 停止並刪除 container |
| `docker compose down -v` | 連 volume 一起刪 |
| `docker compose ps` | 查看服務狀態 |
| `docker compose logs -f service` | 看特定服務 log |
| `docker compose exec service cmd` | 在服務裡執行指令 |
| `docker compose run --rm service cmd` | 一次性執行 |

---

## Best Practices

### Dockerfile 最佳實踐

1. **用 .dockerignore** — 不要把 .git、node_modules、.venv 複製進去
2. **先 COPY 依賴檔，再 COPY code** — 善用 layer cache
   ```dockerfile
   COPY requirements.txt .     # ← 很少改
   RUN pip install -r requirements.txt
   COPY . .                    # ← 常改，但上面的 cache 還在
   ```
3. **用 multi-stage build** — 最終 image 不要有 build tools
4. **不要用 root** — 加 `USER appuser`
5. **固定版本** — `python:3.11-slim` 而不是 `python:latest`
6. **合併 RUN 指令** — 減少 layer 數量
7. **加 HEALTHCHECK** — ECS 和 orchestrator 需要知道你的 app 是否健康

### 安全性

1. **不要把 secrets 寫在 Dockerfile 裡** — 用環境變數或 secrets manager
2. **定期更新 base image** — 修安全漏洞
3. **掃描 image 漏洞** — `docker scout cves my-app`
4. **最小權限原則** — 只安裝需要的套件，只開需要的 port

### 效能

1. **Image 越小越好** — 用 slim/alpine、multi-stage
2. **善用 cache** — 不常改的東西放前面
3. **不要在 container 裡存資料** — 用 volume 或外部服務
4. **一個 container 一個 process** — 不要在同一個 container 跑 app + db

---

## 與 ECS 的關係

```
本地開發                    正式部署
─────────                  ─────────
docker-compose.yml         Terraform (ECS Task Definition)
  ↓                          ↓
docker compose up          terraform apply
  ↓                          ↓
本地跑多個 container        ECS 跑多個 task
  ↓                          ↓
localhost:8000             ALB DNS name
```

**重點：** Dockerfile 是共用的，不管本地或 ECS 都用同一個 Dockerfile build image。
差別只是「誰來管理 container」：
- 本地 → Docker Compose
- 正式 → ECS（由 Terraform 設定）

你的 ECS Task Definition 裡的 `container_definitions` 就是告訴 ECS：
用哪個 image、開哪個 port、給多少 CPU/memory — 跟 docker-compose.yml 的 services 是同一個概念。
