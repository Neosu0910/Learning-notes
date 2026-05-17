# AWS Route 53 筆記

Route 53 是 AWS 的 DNS（Domain Name System）服務，同時也提供域名註冊和健康檢查功能。名字來自 DNS 使用的 Port 53。

---

## DNS 基礎複習

在看 Route 53 之前，先確認 DNS 的概念：

```
你在瀏覽器輸入 api.example.com
        ↓
DNS 查詢：api.example.com 對應哪個 IP？
        ↓
Route 53 回答：54.230.12.45
        ↓
瀏覽器連到 54.230.12.45
```

DNS 就是「域名 → IP」的電話簿，Route 53 是 AWS 幫你管這本電話簿的服務。

---

## 核心概念

### Hosted Zone（託管區域）

Hosted Zone 是某個域名的 DNS 記錄集合，類似一個資料夾，裡面放著這個域名所有的 DNS 設定。

| 類型 | 說明 |
|------|------|
| Public Hosted Zone | 對外公開，任何人都能查詢 |
| Private Hosted Zone | 只在 VPC 內部可查詢，用於內部服務的 DNS |

```bash
# 建立 Public Hosted Zone
aws route53 create-hosted-zone \
  --name example.com \
  --caller-reference $(date +%s)

# 建立 Private Hosted Zone（只在指定 VPC 內有效）
aws route53 create-hosted-zone \
  --name internal.example.com \
  --caller-reference $(date +%s) \
  --hosted-zone-config PrivateZone=true \
  --vpc VPCRegion=ap-northeast-1,VPCId=vpc-xxxxxxxx
```

### Record（DNS 記錄）

Record 是 Hosted Zone 裡的一筆設定，定義某個域名對應到什麼。

**常見 Record 類型：**

| 類型 | 說明 | 範例 |
|------|------|------|
| A | 域名 → IPv4 位址 | `api.example.com → 54.230.12.45` |
| AAAA | 域名 → IPv6 位址 | `api.example.com → 2001:db8::1` |
| CNAME | 域名 → 另一個域名 | `www.example.com → example.com` |
| MX | 郵件伺服器 | `example.com → mail.example.com` |
| TXT | 文字記錄 | 用於 SSL 憑證驗證、SPF 設定 |
| NS | Name Server | 這個域名由哪些 DNS 伺服器管理 |
| Alias | AWS 特有，域名 → AWS 資源 | `example.com → ALB DNS 名稱` |

### TTL（Time To Live）

TTL 是 DNS 快取的存活時間（秒）。設定越短，改動越快生效，但 DNS 查詢次數越多。

```
TTL = 300（5 分鐘）：
  用戶查詢 api.example.com → 得到 IP，快取 5 分鐘
  5 分鐘內再查詢 → 直接用快取，不問 Route 53
  5 分鐘後 → 重新查詢 Route 53

實際影響：
  你改了 DNS 記錄，最多需要等 TTL 秒才會全部生效
  遷移前建議先把 TTL 調低（如 60 秒），遷移後再調回來
```

---

## Alias Record（別名記錄）

Alias 是 Route 53 特有的功能，讓你把域名直接指向 AWS 資源，而不需要知道對方的 IP。

**為什麼需要 Alias：**
- ALB、CloudFront 的 IP 會變動，不能用 A Record 直接指
- CNAME 不能用在根域名（`example.com`），只能用在子域名（`www.example.com`）
- Alias 解決了這兩個問題，而且查詢免費

```bash
# 把根域名指向 ALB（用 Alias）
aws route53 change-resource-record-sets \
  --hosted-zone-id Z1234567890 \
  --change-batch '{
    "Changes": [{
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "example.com",
        "Type": "A",
        "AliasTarget": {
          "HostedZoneId": "Z35SXDOTRQ7X7K",
          "DNSName": "my-alb-1234567890.ap-northeast-1.elb.amazonaws.com",
          "EvaluateTargetHealth": true
        }
      }
    }]
  }'
```

**Alias 支援的 AWS 資源：**
- ALB / NLB / CLB
- CloudFront Distribution
- API Gateway
- S3 靜態網站
- Elastic Beanstalk
- 同一個 Hosted Zone 裡的其他 Record

---

## Routing Policy（路由策略）

Route 53 不只是單純的 DNS，它可以根據不同策略決定回傳哪個 IP，實現流量控制。

### Simple（簡單路由）

最基本的，一個域名對應一個或多個 IP，沒有特殊邏輯。

```
api.example.com → 54.230.12.45
```

### Weighted（加權路由）

把流量按比例分配，常用於 A/B 測試或灰度發布。

```bash
# 90% 流量給 v1，10% 給 v2
aws route53 change-resource-record-sets \
  --hosted-zone-id Z1234567890 \
  --change-batch '{
    "Changes": [
      {
        "Action": "CREATE",
        "ResourceRecordSet": {
          "Name": "api.example.com",
          "Type": "A",
          "SetIdentifier": "v1",
          "Weight": 90,
          "TTL": 60,
          "ResourceRecords": [{"Value": "54.230.12.45"}]
        }
      },
      {
        "Action": "CREATE",
        "ResourceRecordSet": {
          "Name": "api.example.com",
          "Type": "A",
          "SetIdentifier": "v2",
          "Weight": 10,
          "TTL": 60,
          "ResourceRecords": [{"Value": "54.230.12.46"}]
        }
      }
    ]
  }'
```

### Latency-based（延遲路由）

根據用戶到各個 AWS Region 的延遲，自動導向最近的 Region。

```
台灣用戶 → 延遲測試 → ap-northeast-1（東京）最近 → 導向東京的 ALB
美國用戶 → 延遲測試 → us-east-1（維吉尼亞）最近 → 導向美國的 ALB
```

### Failover（故障轉移路由）

設定主備架構，主要端點掛掉時自動切換到備用端點。

```
正常：api.example.com → Primary（ap-northeast-1 的 ALB）
故障：Health Check 失敗 → api.example.com → Secondary（ap-southeast-1 的 ALB）
```

```bash
# Primary Record
{
  "Name": "api.example.com",
  "Type": "A",
  "SetIdentifier": "primary",
  "Failover": "PRIMARY",
  "HealthCheckId": "health-check-id",
  "AliasTarget": { ... primary ALB ... }
}

# Secondary Record
{
  "Name": "api.example.com",
  "Type": "A",
  "SetIdentifier": "secondary",
  "Failover": "SECONDARY",
  "AliasTarget": { ... secondary ALB ... }
}
```

### Geolocation（地理位置路由）

根據用戶的地理位置（國家/洲）決定導向哪個端點。

```
台灣用戶 → tw.example.com 的後端
日本用戶 → jp.example.com 的後端
其他地區 → default 後端
```

常用於：
- 法規合規（歐盟用戶的資料必須存在歐盟）
- 語言/內容本地化
- 限制特定地區存取

### Multivalue Answer（多值回答）

回傳多個 IP，並結合 Health Check，只回傳健康的 IP。比 Simple 多了健康檢查，但不是真正的 Load Balancer。

---

## Health Check（健康檢查）

Route 53 可以定期檢查端點是否健康，搭配 Failover 或其他路由策略使用。

```bash
# 建立 HTTP Health Check
aws route53 create-health-check \
  --caller-reference $(date +%s) \
  --health-check-config '{
    "IPAddress": "54.230.12.45",
    "Port": 443,
    "Type": "HTTPS",
    "ResourcePath": "/health",
    "FullyQualifiedDomainName": "api.example.com",
    "RequestInterval": 30,
    "FailureThreshold": 3
  }'
```

**Health Check 類型：**
| 類型 | 說明 |
|------|------|
| HTTP / HTTPS | 檢查端點是否回傳 2xx 或 3xx |
| TCP | 檢查 TCP 連線是否成功 |
| Calculated | 組合多個 Health Check 的結果 |
| CloudWatch Alarm | 依 CloudWatch Alarm 狀態判斷 |

---

## 常見使用情境

### 情境一：把域名指向 ALB

```
example.com → Route 53 → ALB → ECS / EC2
```

```bash
# 1. 在 Route 53 建立 Hosted Zone
# 2. 把域名的 NS 記錄更新到 Route 53 提供的 Name Server
# 3. 建立 Alias A Record 指向 ALB

aws route53 change-resource-record-sets \
  --hosted-zone-id Z1234567890 \
  --change-batch '{
    "Changes": [{
      "Action": "UPSERT",
      "ResourceRecordSet": {
        "Name": "api.example.com",
        "Type": "A",
        "AliasTarget": {
          "HostedZoneId": "Z35SXDOTRQ7X7K",
          "DNSName": "my-alb.ap-northeast-1.elb.amazonaws.com",
          "EvaluateTargetHealth": true
        }
      }
    }]
  }'
```

### 情境二：ACM 憑證 DNS 驗證

申請 ACM 憑證時，需要在 Route 53 加一筆 TXT 或 CNAME 記錄來證明你擁有這個域名：

```bash
# ACM 會給你一個驗證用的 CNAME 記錄，加進去後 ACM 自動核發憑證
# 格式：
# _abc123.example.com → _xyz789.acm-validations.aws.

# 如果域名在 Route 53，可以在 ACM Console 直接點「在 Route 53 建立記錄」，一鍵完成
```

### 情境三：Private Hosted Zone（內部服務 DNS）

微服務之間互相呼叫，用有意義的域名而不是 IP：

```
VPC 內部：
  order-service 呼叫 user-service.internal → Route 53 Private Hosted Zone 解析
  → 10.0.1.50（user-service 的 Internal ALB）

外部無法解析 user-service.internal，只有 VPC 內部可以
```

```bash
# 建立 Private Hosted Zone
aws route53 create-hosted-zone \
  --name internal \
  --caller-reference $(date +%s) \
  --hosted-zone-config PrivateZone=true \
  --vpc VPCRegion=ap-northeast-1,VPCId=vpc-xxxxxxxx

# 加入 A Record 指向 Internal ALB
aws route53 change-resource-record-sets \
  --hosted-zone-id ZPRIVATE123 \
  --change-batch '{
    "Changes": [{
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "user-service.internal",
        "Type": "A",
        "AliasTarget": {
          "HostedZoneId": "Z35SXDOTRQ7X7K",
          "DNSName": "internal-alb.ap-northeast-1.elb.amazonaws.com",
          "EvaluateTargetHealth": true
        }
      }
    }]
  }'
```

---

## 完整架構中的位置

```
用戶輸入 api.example.com
        ↓
Route 53（DNS 解析）
        ↓ 回傳 ALB 的 IP
ALB（負載均衡 + SSL 終止）
        ↓
ECS Tasks（實際處理請求）
        ↓
RDS / ElastiCache / S3
```

Route 53 是整個架構的入口，負責把域名解析到 ALB，之後的流量分發由 ALB 負責。

---

## 費用

| 項目 | 費用 |
|------|------|
| Hosted Zone | $0.50/月（前 25 個），$0.10/月（之後每個）|
| DNS 查詢 | $0.40 / 百萬次查詢（前 10 億次）|
| Alias 查詢（指向 AWS 資源）| **免費** |
| Health Check | $0.50/月（基本），$1.00/月（HTTPS）|

> Alias Record 查詢免費是很大的優勢，所以指向 ALB、CloudFront 時一律用 Alias。
