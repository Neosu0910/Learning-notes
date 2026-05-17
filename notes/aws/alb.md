# AWS ALB 筆記

ALB（Application Load Balancer）是 AWS 的第七層（應用層）負載均衡器，負責把進來的 HTTP/HTTPS 流量分發到後端的多台伺服器或容器。它是現代 AWS 架構裡幾乎必備的元件。

---

## 核心概念

### 為什麼需要 Load Balancer

```
沒有 ALB：
  所有流量 → 單台 EC2 → 掛了就全部中斷

有 ALB：
  所有流量 → ALB → EC2-a（AZ-a）
                 → EC2-b（AZ-b）
                 → EC2-c（AZ-a）
  任何一台掛掉，ALB 自動把流量導向其他健康的機器
```

ALB 解決三個問題：
1. **高可用性**：後端有多台，一台掛掉不影響服務
2. **水平擴展**：流量增加時加機器，ALB 自動分流
3. **SSL 終止**：在 ALB 層處理 HTTPS，後端只需處理 HTTP

### ALB vs NLB vs CLB

AWS 有三種 Load Balancer：

| | ALB | NLB | CLB |
|--|-----|-----|-----|
| 層級 | Layer 7（應用層）| Layer 4（傳輸層）| Layer 4/7（舊版）|
| 協定 | HTTP、HTTPS、WebSocket | TCP、UDP、TLS | HTTP、HTTPS、TCP |
| 路由能力 | 依 URL、Header、Host 路由 | 只依 IP + Port | 有限 |
| 效能 | 一般 | 極高（百萬 RPS）| 一般 |
| 適用場景 | Web API、微服務 | 遊戲、IoT、需要固定 IP | 舊有系統（不建議新建）|

> 大多數 Web 應用選 ALB，需要超低延遲或固定 IP 才考慮 NLB。

---

## 三個核心元件

### 1. Listener（監聽器）

Listener 定義 ALB 要監聽哪個 Port 和協定，以及收到請求後要做什麼。

```
ALB
├── Listener: HTTP:80  → 規則：全部重導向到 HTTPS
└── Listener: HTTPS:443 → 規則：轉發到 Target Group
```

每個 Listener 可以有多條規則（Rules），按優先順序判斷：

```
HTTPS:443 Listener 的規則：
  Priority 1: Host = api.example.com  → 轉發到 api-target-group
  Priority 2: Path = /admin/*         → 轉發到 admin-target-group
  Priority 3: （預設）                 → 轉發到 default-target-group
```

### 2. Target Group（目標群組）

Target Group 是後端目標的集合，ALB 把流量轉發到這裡。Target 可以是：
- EC2 Instance
- IP 位址（包含 VPC 外的 IP）
- Lambda Function
- ECS Task（容器）

**Health Check（健康檢查）：**
ALB 會定期對 Target Group 裡的每個目標發送健康檢查請求，只把流量導向健康的目標。

```
健康檢查設定範例：
  Protocol: HTTP
  Path: /health
  Port: 8000
  Healthy threshold: 2（連續 2 次成功才算健康）
  Unhealthy threshold: 3（連續 3 次失敗才算不健康）
  Interval: 30 秒
  Timeout: 5 秒
```

你的後端需要實作一個 `/health` 端點：
```python
# FastAPI 範例
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health_check():
    return {"status": "ok"}
```

### 3. Rule（規則）

Rule 決定符合條件的請求要轉發到哪個 Target Group。

**條件類型：**
| 條件 | 說明 | 範例 |
|------|------|------|
| Host Header | 依域名路由 | `api.example.com` vs `www.example.com` |
| Path Pattern | 依 URL 路徑路由 | `/api/*` vs `/static/*` |
| HTTP Header | 依請求 Header | `X-Version: v2` |
| Query String | 依 URL 參數 | `?env=staging` |
| HTTP Method | 依請求方法 | GET vs POST |
| Source IP | 依來源 IP | 只允許特定 IP 段 |

---

## 路由設定範例

### 情境：微服務架構，依路徑路由

```
https://api.example.com/users/...   → user-service (ECS)
https://api.example.com/orders/...  → order-service (ECS)
https://api.example.com/static/...  → S3 (直接回傳)
```

```bash
# 用 AWS CLI 建立 Target Group
aws elbv2 create-target-group \
  --name user-service-tg \
  --protocol HTTP \
  --port 8001 \
  --vpc-id vpc-xxxxxxxx \
  --target-type ip \
  --health-check-path /health

# 建立路由規則（Path-based routing）
aws elbv2 create-rule \
  --listener-arn arn:aws:elasticloadbalancing:...:listener/... \
  --priority 10 \
  --conditions '[{"Field":"path-pattern","Values":["/users/*"]}]' \
  --actions '[{"Type":"forward","TargetGroupArn":"arn:...user-service-tg"}]'
```

### 情境：HTTP 自動重導向到 HTTPS

```bash
# 在 HTTP:80 Listener 加上重導向規則
aws elbv2 create-rule \
  --listener-arn arn:aws:elasticloadbalancing:...:listener/http-listener \
  --priority 1 \
  --conditions '[{"Field":"path-pattern","Values":["/*"]}]' \
  --actions '[{
    "Type": "redirect",
    "RedirectConfig": {
      "Protocol": "HTTPS",
      "Port": "443",
      "StatusCode": "HTTP_301"
    }
  }]'
```

---

## SSL / HTTPS 設定

ALB 支援 SSL 終止（SSL Termination）：HTTPS 在 ALB 層解密，後端只需處理 HTTP。

```
Client ──HTTPS──> ALB ──HTTP──> EC2 / ECS
         (加密)        (明文，但在 VPC 內部，安全)
```

**掛上 ACM 憑證：**
```bash
# 先在 ACM 申請憑證（或匯入自有憑證）
aws acm request-certificate \
  --domain-name example.com \
  --subject-alternative-names "*.example.com" \
  --validation-method DNS

# 建立 HTTPS Listener 並掛上憑證
aws elbv2 create-listener \
  --load-balancer-arn arn:aws:elasticloadbalancing:...:loadbalancer/... \
  --protocol HTTPS \
  --port 443 \
  --certificates CertificateArn=arn:aws:acm:...:certificate/... \
  --default-actions Type=forward,TargetGroupArn=arn:...
```

---

## Sticky Session（黏性會話）

預設 ALB 每次請求都可能導向不同的後端。如果你的應用把 Session 存在本地記憶體（不推薦），需要開啟 Sticky Session，讓同一個用戶的請求都導向同一台後端。

```bash
# 開啟 Sticky Session（基於 Cookie）
aws elbv2 modify-target-group-attributes \
  --target-group-arn arn:... \
  --attributes \
    Key=stickiness.enabled,Value=true \
    Key=stickiness.type,Value=lb_cookie \
    Key=stickiness.lb_cookie.duration_seconds,Value=86400
```

> 最佳實踐：Session 應該存在 Redis 或資料庫，這樣不需要 Sticky Session，後端可以真正無狀態（stateless）。

---

## Access Log

ALB 可以把所有請求記錄到 S3，方便事後分析：

```bash
# 開啟 Access Log
aws elbv2 modify-load-balancer-attributes \
  --load-balancer-arn arn:... \
  --attributes \
    Key=access_logs.s3.enabled,Value=true \
    Key=access_logs.s3.bucket,Value=my-alb-logs \
    Key=access_logs.s3.prefix,Value=my-app
```

Log 格式包含：時間、客戶端 IP、請求方法、URL、回應碼、延遲、Target Group、後端 IP 等。

---

## 常見架構

### 基本 Web 應用架構

```
Internet
  └── Route 53（DNS）
        └── ALB（Public Subnet，跨 AZ）
              ├── AZ-a: EC2 / ECS Task（Private Subnet）
              └── AZ-b: EC2 / ECS Task（Private Subnet）
                          └── RDS（Private Subnet）
```

### 微服務架構（單一 ALB，多個 Target Group）

```
ALB
├── /api/users/*  → user-service Target Group  → ECS Service A
├── /api/orders/* → order-service Target Group → ECS Service B
└── /api/notify/* → notify-service Target Group → Lambda
```

### 內部 ALB（Internal ALB）

ALB 可以設定為 Internal（只在 VPC 內部可存取），用於微服務之間的通訊：

```
外部 ALB（Public）→ API Gateway Service（ECS）
                          ↓ 呼叫內部服務
                    內部 ALB（Internal）
                          ├── user-service（ECS）
                          └── order-service（ECS）
```

---

## 費用

ALB 費用由兩部分組成：
- **固定費用**：每小時約 $0.008（約 $5.76/月）
- **LCU（Load Balancer Capacity Unit）**：依流量計費，每 LCU 約 $0.008/小時

LCU 由以下四個維度中最高的決定：
1. 新連線數（每秒）
2. 活躍連線數
3. 處理的流量（GB/小時）
4. 規則評估次數

> 一般中小型應用每月 ALB 費用約 $15–30 USD。

---

## 常見問題排查

| 問題 | 可能原因 | 排查方式 |
|------|---------|---------|
| 502 Bad Gateway | 後端沒有回應或回應格式錯誤 | 檢查 Target Group 健康狀態、後端 log |
| 503 Service Unavailable | Target Group 裡沒有健康的目標 | 檢查 Health Check 設定和後端 /health 端點 |
| 504 Gateway Timeout | 後端回應超時（預設 60 秒）| 調整 `idle_timeout` 或優化後端效能 |
| 連線被重置 | Security Group 沒有允許 ALB 到後端的流量 | 確認後端 Security Group 允許來自 ALB Security Group 的流量 |

**Security Group 設定重點：**
```
ALB Security Group:
  Inbound: TCP/443 from 0.0.0.0/0
  Inbound: TCP/80  from 0.0.0.0/0

後端 EC2 / ECS Security Group:
  Inbound: TCP/8000 from ALB Security Group  ← 只允許來自 ALB，不對外開放
```
