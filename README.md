# TIL — Today I Learned

工程師日常學習筆記，記錄每天在工作中遇到的新名詞、概念與實作。
涵蓋後端開發、雲端架構、容器化、Linux、CI/CD、Python 生態系等主題。

> 筆記原則：每個概念都附上實際例子與可執行的程式碼，把自己當成什麼都不會的人來寫。

---

## 📁 結構

```
.
├── notes/                  # 主題式學習筆記
│   ├── aws/                # AWS 雲端服務
│   ├── pythonnote.md       # Python 語法
│   ├── backend-basics.md   # HTTP、REST API
│   ├── database-basics.md  # SQL、資料庫
│   ├── networking-basics.md # 網路基礎
│   ├── sqlalchemy.md       # ORM
│   └── fastapi.md          # FastAPI 框架
│
├── knowledge/              # 工作中學到的技術知識
│   ├── processes/          # 升級流程、遷移指南
│   ├── architecture/       # 系統架構設計
│   ├── lessons/            # 踩坑紀錄
│   └── tools/              # 工具使用心得
│
├── Python Practice/        # Python 練習程式碼
├── Python-FastAPI/         # FastAPI 專案練習
│
├── 2026/                   # 每日速記與名詞解釋（依年月）
│
├── docker-guide.md         # Docker 指南
├── k8s-guide.md            # Kubernetes 指南
├── linux-guide.md          # Linux 指南
├── linux-practice.md       # Linux 實作練習
├── redhat-guide.md         # Red Hat 相關
├── terraform-ecs.md        # Terraform + ECS
├── abbreviations.md        # 縮寫對照表
└── admin.md                # 管理相關筆記
```

---

## 📚 主題式筆記

### Python & 後端

| 檔案 | 內容 |
|------|------|
| [pythonnote.md](./notes/pythonnote.md) | Python 語法入門 |
| [backend-basics.md](./notes/backend-basics.md) | HTTP、REST API、request/response |
| [database-basics.md](./notes/database-basics.md) | SQL、table/column/relation |
| [networking-basics.md](./notes/networking-basics.md) | 網路基礎概念 |
| [sqlalchemy.md](./notes/sqlalchemy.md) | ORM、SQLAlchemy |
| [fastapi.md](./notes/fastapi.md) | FastAPI 路由、依賴注入、Pydantic |

### AWS

| 檔案 | 內容 |
|------|------|
| [aws-networking.md](./notes/aws/aws-networking.md) | VPC、Subnet、Security Group |
| [alb.md](./notes/aws/alb.md) | Application Load Balancer |
| [ec2.md](./notes/aws/ec2.md) | EC2 |
| [ecs.md](./notes/aws/ecs.md) | ECS 容器服務 |
| [iam.md](./notes/aws/iam.md) | IAM 權限管理 |
| [route53.md](./notes/aws/route53.md) | Route53 DNS |
| [cloudwatch.md](./notes/aws/cloudwatch.md) | CloudWatch 監控 |
| [step-functions.md](./notes/aws/step-functions.md) | Step Functions 狀態機 |
| [aws-chatbot-practice.md](./notes/aws/aws-chatbot-practice.md) | AWS Chatbot 實作 |

### Infrastructure & DevOps

| 檔案 | 內容 |
|------|------|
| [docker-guide.md](./docker-guide.md) | Docker 容器化 |
| [k8s-guide.md](./k8s-guide.md) | Kubernetes 基礎 |
| [terraform-ecs.md](./terraform-ecs.md) | Terraform + ECS 部署 |
| [linux-guide.md](./linux-guide.md) | Linux 指南 |
| [linux-practice.md](./linux-practice.md) | Linux 實作練習 |
| [redhat-guide.md](./redhat-guide.md) | Red Hat 系統 |

### Knowledge（工作中消化的技術知識）

| 檔案 | 內容 |
|------|------|
| [external-dns-upgrade.md](./knowledge/processes/external-dns-upgrade.md) | K8s 元件升級流程（RBAC → Image） |
| [gateway-api-migration.md](./knowledge/processes/gateway-api-migration.md) | Ingress → Gateway API 遷移概念 |

---

## 📅 每日名詞筆記（TIL）

每天上班聽到來不及查的名詞，下班後整理成詳細解釋。

| 月份 | 速記 | 解釋 |
|------|------|------|
| 2026/05 | [05note.md](./2026/05/05note.md) | [05-glossary.md](./2026/05/05-glossary.md) |
| 2026/06 | [06note.md](./2026/06/06note.md) | [06-glossary.md](./2026/06/06-glossary.md) |

---

## 🐍 Python Practice

練習用的 Python 程式碼，涵蓋基礎語法到進階概念：

| 檔案 | 主題 |
|------|------|
| basic.py | 基礎語法 |
| condition.py | 條件判斷 |
| forwhile.py | 迴圈 |
| function-basic.py | 函式基礎 |
| callback-function.py | Callback 函式 |
| generator.py | Generator |
| instance.py | 物件實例 |
| test-class.py | Class |
| module.py | Module 使用 |
| 01_python_core.py | Python 核心概念 |
| 02_async_basics.py | Async/Await 基礎 |
| 03_dict_get.py | Dict 操作 |
