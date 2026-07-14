# 軟體業常見縮寫速查表

> 在公司聽到新的隨時補充進來

---

## 開發工具類

| 縮寫 | 全稱 | 白話 |
|---|---|---|
| **IDE** | Integrated Development Environment | 寫 code 的編輯器（VS Code, IntelliJ, Kiro） |
| **SDK** | Software Development Kit | 別人提供給你的工具包，讓你能用他們的服務（例如 boto3 就是 AWS 的 Python SDK） |
| **CLI** | Command Line Interface | 用終端機打字操作的工具（`aws cli`, `docker cli`, `terraform`） |
| **API** | Application Programming Interface | 程式之間溝通的介面（你打一個 URL，它回你資料） |
| **GUI** | Graphical User Interface | 有畫面可以點的介面（AWS Console 就是 GUI） |

---

## 開發流程類

| 縮寫 | 全稱 | 白話 |
|---|---|---|
| **CI/CD** | Continuous Integration / Continuous Deployment | 自動測試 + 自動部署的流程 |
| **PR** | Pull Request | 請別人 review 你的 code 再 merge |
| **MR** | Merge Request | 同上，GitLab 用這個名字 |
| **CR** | Code Review | 看別人的 code，給意見 |
| **QA** | Quality Assurance | 測試/品質保證（有時指測試工程師） |
| **UAT** | User Acceptance Testing | 使用者驗收測試（上線前讓使用者試） |
| **VCS** | Version Control System | 版本控制系統（Git） |
| **SCM** | Source Code Management | 原始碼管理（同上，不同說法） |

---

## 架構/基礎設施類

| 縮寫 | 全稱 | 白話 |
|---|---|---|
| **IaC** | Infrastructure as Code | 用程式碼管理基礎設施（Terraform, CDK） |
| **CDK** | Cloud Development Kit | 用程式語言（Python/TypeScript）寫基礎設施，底層產生 CloudFormation。跟 Terraform 做一樣的事，但用你熟悉的語言而不是 HCL |
| **VPC** | Virtual Private Cloud | AWS 裡你的私有網路空間 |
| **ALB** | Application Load Balancer | 把流量分配到多台 server |
| **NLB** | Network Load Balancer | 更底層的 load balancer（TCP/UDP 層） |
| **EC2** | Elastic Compute Cloud | AWS 的虛擬機 |
| **ECS** | Elastic Container Service | AWS 跑 Docker container 的服務 |
| **EKS** | Elastic Kubernetes Service | AWS 跑 Kubernetes 的服務 |
| **ECR** | Elastic Container Registry | AWS 存 Docker image 的倉庫 |
| **RDS** | Relational Database Service | AWS 管理的資料庫 |
| **S3** | Simple Storage Service | AWS 的檔案儲存 |
| **IAM** | Identity and Access Management | AWS 的權限管理 |
| **DNS** | Domain Name System | 把網址翻譯成 IP（Route 53 做這件事） |
| **CDN** | Content Delivery Network | 把靜態資源放到全球各地加速（CloudFront） |
| **SNS** | Simple Notification Service | AWS 的推播通知服務 |
| **SQS** | Simple Queue Service | AWS 的訊息佇列 |
| **ASG** | Auto Scaling Group | 自動根據流量增減 server 數量 |
| **AZ** | Availability Zone | AWS 的資料中心分區（同 region 裡不同機房） |
| **ARN** | Amazon Resource Name | AWS 資源的唯一識別碼 |

---

## 程式/概念類

| 縮寫 | 全稱 | 白話 |
|---|---|---|
| **OOP** | Object-Oriented Programming | 物件導向程式設計（用 class） |
| **JSON** | JavaScript Object Notation | 資料格式，長得像 Python 的 dict |
| **YAML** | YAML Ain't Markup Language | 另一種設定檔格式（docker-compose 用這個） |
| **REST** | Representational State Transfer | API 的一種設計風格（GET/POST/PUT/DELETE） |
| **CRUD** | Create, Read, Update, Delete | 資料的四種基本操作 |
| **ORM** | Object-Relational Mapping | 用 class 操作資料庫，不用寫 SQL（SQLAlchemy） |
| **ENV** | Environment | 環境（dev/staging/prod），也指環境變數 |
| **DB** | Database | 資料庫 |
| **SQL** | Structured Query Language | 查詢資料庫的語言 |
| **HTTP** | HyperText Transfer Protocol | 瀏覽器跟 server 溝通的協定 |
| **HTTPS** | HTTP Secure | 加密版的 HTTP |
| **TCP** | Transmission Control Protocol | 網路傳輸協定（可靠、有順序） |
| **IP** | Internet Protocol | 網路位址協定（每台機器有一個 IP） |
| **SSH** | Secure Shell | 安全連線到遠端 server 的方式 |
| **SSL/TLS** | Secure Sockets Layer / Transport Layer Security | 加密連線（HTTPS 就是用這個） |
| **JWT** | JSON Web Token | 一種登入驗證的 token 格式 |
| **OAuth** | Open Authorization | 第三方登入的授權標準（用 Google 登入） |
| **CORS** | Cross-Origin Resource Sharing | 前端跨網域請求的安全機制 |
| **regex** | Regular Expression | 正則表達式（文字比對規則） |

---

## 軟體設計/架構類

| 縮寫 | 全稱 | 白話 |
|---|---|---|
| **MVC** | Model-View-Controller | 程式架構模式（分資料/畫面/邏輯） |
| **DRY** | Don't Repeat Yourself | 不要重複寫一樣的 code |
| **SOLID** | 五個 OOP 設計原則的首字母 | 寫好維護 code 的五條規則 |
| **KISS** | Keep It Simple, Stupid | 保持簡單 |
| **YAGNI** | You Ain't Gonna Need It | 不需要的東西不要先寫 |
| **DDD** | Domain-Driven Design | 以業務領域為核心的設計方法 |
| **TDD** | Test-Driven Development | 先寫測試再寫 code |
| **BDD** | Behavior-Driven Development | 以行為描述為核心的開發方式 |

---

## 溝通/會議常聽到的

| 縮寫 | 全稱 | 白話 |
|---|---|---|
| **ETA** | Estimated Time of Arrival | 預計什麼時候完成 |
| **WIP** | Work In Progress | 還在做，還沒好 |
| **TBD** | To Be Determined | 還沒決定 |
| **TBA** | To Be Announced | 待公布 |
| **FYI** | For Your Information | 知會你一下 |
| **LGTM** | Looks Good To Me | Code Review 時：我看沒問題，可以 merge |
| **nit** | Nitpick | Code Review 時：小問題，改不改都行（不影響功能，只是風格/命名建議） |
| **ASAP** | As Soon As Possible | 盡快 |
| **POC** | Proof of Concept | 先做個小 demo 驗證可行性 |
| **MVP** | Minimum Viable Product | 最小可用產品（先上最核心功能） |
| **SLA** | Service Level Agreement | 服務保證（例如 uptime 99.9%） |
| **SLO** | Service Level Objective | 服務目標（內部設定的目標，比 SLA 嚴格） |
| **KPI** | Key Performance Indicator | 關鍵績效指標 |
| **OKR** | Objectives and Key Results | 目標與關鍵成果（目標設定框架） |
| **EOD** | End of Day | 今天結束前 |
| **OOO** | Out of Office | 不在辦公室（請假） |
| **SOW** | Statement of Work | 工作說明書（跟客戶簽的，定義專案範圍、交付內容、時程、費用） |
| **1:1** | One-on-One | 跟主管的一對一面談 |
| **standup** | Daily Standup | 每日站立會議（報告昨天做了什麼、今天要做什麼） |
| **retro** | Retrospective | 回顧會議（這個 sprint 做得好/不好的） |
