# CloudWatch Metrics & Alarms + SNS 通知

## 目錄
1. [CloudWatch 是什麼](#cloudwatch-是什麼)
2. [Metrics 概念](#metrics-概念)
3. [常用 Metrics 整理](#常用-metrics-整理)
4. [Alarms 機制](#alarms-機制)
5. [SNS Topic 建置](#sns-topic-建置)
6. [Alarm + SNS 整合](#alarm--sns-整合)
7. [Terraform 實作](#terraform-實作)
8. [AWS CLI 操作](#aws-cli-操作)
9. [實際情境範例](#實際情境範例)
10. [Best Practices](#best-practices)

---

## CloudWatch 是什麼

**一句話：** AWS 的監控服務，負責收集指標 (Metrics)、設定警報 (Alarms)、收集 Log。

### 三大功能

| 功能 | 用途 | 類比 |
|---|---|---|
| **Metrics** | 收集數字指標（CPU、記憶體、請求數） | 汽車儀表板 |
| **Alarms** | 指標超過門檻時觸發動作 | 超速警報 |
| **Logs** | 收集和查詢 log 文字 | 行車紀錄器 |

這份筆記專注在 Metrics + Alarms + SNS 通知的部分。

---

## Metrics 概念

### 什麼是 Metric？

一個 Metric 就是一個「隨時間變化的數值」。

```
Metric = Namespace + MetricName + Dimensions + DataPoints

例如:
  Namespace:  AWS/ECS
  MetricName: CPUUtilization
  Dimensions: ClusterName=prod, ServiceName=my-app
  DataPoints: [72.5% at 10:00, 68.3% at 10:01, 91.2% at 10:02, ...]
```

### 核心術語

| 術語 | 說明 | 範例 |
|---|---|---|
| **Namespace** | Metric 的分類空間 | `AWS/ECS`, `AWS/EC2`, `AWS/ALB` |
| **MetricName** | 指標名稱 | `CPUUtilization`, `RequestCount` |
| **Dimension** | 篩選條件（哪個資源的） | `ClusterName=prod` |
| **Period** | 統計的時間間隔 | 60 秒、300 秒 |
| **Statistic** | 怎麼聚合這段時間的資料 | Average, Sum, Maximum, Minimum |
| **Unit** | 數值單位 | Percent, Count, Bytes, Seconds |

### Metric 的資料怎麼來？

```
1. AWS 自動產生（免費）
   → EC2 CPU, ECS CPU/Memory, ALB 請求數, RDS 連線數...

2. 你自己送進去（Custom Metrics，要付費）
   → 業務指標：訂單數、登入失敗次數、佇列深度...
   → 用 aws cloudwatch put-metric-data 送
```

### Period 和 Statistic 怎麼搭配？

假設你的 ECS service CPU 每秒的值是：`70, 72, 85, 90, 60`

| Statistic | Period=60s 的結果 | 適合什麼場景 |
|---|---|---|
| Average | 75.4% | 整體趨勢，最常用 |
| Maximum | 90% | 抓 spike，偵測突發高峰 |
| Minimum | 60% | 確認是否有閒置 |
| Sum | 377 | 計數型指標（RequestCount） |
| SampleCount | 5 | 有幾筆資料點 |

---

## 常用 Metrics 整理

### ECS (Fargate)

| MetricName | 說明 | 常用 Statistic |
|---|---|---|
| `CPUUtilization` | Task 的 CPU 使用率 (%) | Average |
| `MemoryUtilization` | Task 的記憶體使用率 (%) | Average |

Dimensions: `ClusterName`, `ServiceName`

### ALB (Application Load Balancer)

| MetricName | 說明 | 常用 Statistic |
|---|---|---|
| `RequestCount` | 請求總數 | Sum |
| `HTTPCode_Target_5XX_Count` | 後端回 5xx 的次數 | Sum |
| `HTTPCode_ELB_5XX_Count` | ALB 本身的 5xx | Sum |
| `TargetResponseTime` | 後端回應時間 (秒) | Average / p99 |
| `HealthyHostCount` | 健康的 target 數量 | Minimum |
| `UnHealthyHostCount` | 不健康的 target 數量 | Maximum |

Dimensions: `LoadBalancer`, `TargetGroup`

### EC2

| MetricName | 說明 | 常用 Statistic |
|---|---|---|
| `CPUUtilization` | CPU 使用率 | Average |
| `StatusCheckFailed` | 系統/實例檢查失敗 | Maximum |
| `NetworkIn` / `NetworkOut` | 網路流量 (bytes) | Sum |

### RDS

| MetricName | 說明 | 常用 Statistic |
|---|---|---|
| `CPUUtilization` | DB CPU 使用率 | Average |
| `DatabaseConnections` | 目前連線數 | Average |
| `FreeStorageSpace` | 剩餘儲存空間 | Minimum |
| `ReadLatency` / `WriteLatency` | 讀寫延遲 | Average |

### Custom Metrics（你自己送的）

```bash
# 用 AWS CLI 送 custom metric
aws cloudwatch put-metric-data \
  --namespace "MyApp" \
  --metric-name "OrderCount" \
  --value 15 \
  --unit Count \
  --dimensions Environment=prod,Service=checkout
```

```python
# 用 boto3 送 custom metric
import boto3

client = boto3.client("cloudwatch")
client.put_metric_data(
    Namespace="MyApp",
    MetricData=[{
        "MetricName": "LoginFailures",
        "Value": 3,
        "Unit": "Count",
        "Dimensions": [
            {"Name": "Environment", "Value": "prod"},
        ]
    }]
)
```

---

## Alarms 機制

### Alarm 的三種狀態

```
OK         →  指標正常，在門檻內
ALARM      →  指標超過門檻，觸發動作
INSUFFICIENT_DATA  →  資料不夠，無法判斷（剛建立時常見）
```

### Alarm 的組成

```
Alarm = Metric + 條件 + 評估期間 + 動作

翻譯成白話:
「當 ECS service 的平均 CPU 在連續 3 個 5 分鐘內都超過 80%，
 就發 SNS 通知給我」
```

### 關鍵設定參數

| 參數 | 說明 | 範例 |
|---|---|---|
| `MetricName` | 監控哪個指標 | CPUUtilization |
| `Threshold` | 門檻值 | 80 |
| `ComparisonOperator` | 比較方式 | GreaterThanThreshold |
| `EvaluationPeriods` | 連續幾個 period 超標才觸發 | 3 |
| `Period` | 每個評估區間多長 | 300 (秒) = 5 分鐘 |
| `Statistic` | 用什麼統計方式 | Average |
| `AlarmActions` | 觸發 ALARM 時做什麼 | SNS Topic ARN |
| `OKActions` | 恢復 OK 時做什麼 | SNS Topic ARN |

### ComparisonOperator 選項

| 值 | 意思 |
|---|---|
| `GreaterThanThreshold` | > 門檻 |
| `GreaterThanOrEqualToThreshold` | >= 門檻 |
| `LessThanThreshold` | < 門檻 |
| `LessThanOrEqualToThreshold` | <= 門檻 |

### EvaluationPeriods 的作用

```
設定: Period=300, EvaluationPeriods=3, Threshold=80%

時間軸:
  10:00-10:05  CPU=85%  ← 超標 (1/3)
  10:05-10:10  CPU=90%  ← 超標 (2/3)
  10:10-10:15  CPU=82%  ← 超標 (3/3) → 觸發 ALARM!

如果中間有一次沒超:
  10:00-10:05  CPU=85%  ← 超標 (1/3)
  10:05-10:10  CPU=70%  ← 正常，重新計算
  10:10-10:15  CPU=82%  ← 超標 (1/3)
  → 不會觸發，避免短暫 spike 誤報
```

### Datapoints to Alarm（更彈性的設定）

```
「5 個 period 裡有 3 個超標就觸發」

設定: EvaluationPeriods=5, DatapointsToAlarm=3

好處: 允許偶爾的 spike，但持續異常還是會被抓到
```

---

## SNS Topic 建置

### SNS 是什麼？

**Simple Notification Service** — AWS 的推播/通知服務。

```
事件來源 (CloudWatch Alarm)
    ↓ publish message
SNS Topic (訊息中轉站)
    ↓ 分發給所有訂閱者
┌─────────────────────────────────┐
│  Email 訂閱者 → 收到信          │
│  SMS 訂閱者 → 收到簡訊          │
│  Lambda 訂閱者 → 觸發 function  │
│  Slack webhook → 發到 channel   │
│  PagerDuty → 觸發 on-call       │
└─────────────────────────────────┘
```

### SNS 的核心概念

| 概念 | 說明 |
|---|---|
| **Topic** | 訊息的主題/頻道，訂閱者訂閱 topic |
| **Subscription** | 誰訂閱了這個 topic，用什麼方式接收 |
| **Publisher** | 誰發訊息到 topic（CloudWatch Alarm, Lambda...） |
| **Protocol** | 傳遞方式：email, sms, https, lambda, sqs |

### 用 AWS Console 建 SNS Topic + Email 訂閱

```
1. 到 SNS Console → Topics → Create topic
2. Type: Standard
3. Name: prod-alerts
4. Create topic

5. 在 topic 頁面 → Create subscription
6. Protocol: Email
7. Endpoint: your-email@example.com
8. Create subscription

9. 去信箱收確認信 → 點 Confirm subscription
   ⚠️ 不確認的話收不到通知！
```

### 用 AWS CLI 建 SNS

```bash
# 建立 Topic
aws sns create-topic --name prod-alerts
# 回傳: { "TopicArn": "arn:aws:sns:us-east-1:123456:prod-alerts" }

# 訂閱 Email
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:123456:prod-alerts \
  --protocol email \
  --notification-endpoint your-email@example.com

# 訂閱 HTTPS endpoint（Slack webhook, PagerDuty 等）
aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:123456:prod-alerts \
  --protocol https \
  --notification-endpoint https://hooks.slack.com/services/xxx/yyy/zzz

# 測試發送
aws sns publish \
  --topic-arn arn:aws:sns:us-east-1:123456:prod-alerts \
  --subject "Test Alert" \
  --message "This is a test notification"
```

---

## Alarm + SNS 整合

### 整體流程

```
ECS CPU > 80%
    ↓
CloudWatch Alarm 狀態變成 ALARM
    ↓
AlarmActions 指向 SNS Topic
    ↓
SNS Topic 發通知給所有訂閱者
    ↓
你收到 Email / Slack / SMS 通知
```

### 用 AWS CLI 建立 Alarm + 連接 SNS

```bash
# 建立 CloudWatch Alarm，連接到 SNS Topic
aws cloudwatch put-metric-alarm \
  --alarm-name "ecs-high-cpu" \
  --alarm-description "ECS service CPU > 80% for 15 minutes" \
  --namespace AWS/ECS \
  --metric-name CPUUtilization \
  --dimensions Name=ClusterName,Value=prod Name=ServiceName,Value=my-app \
  --statistic Average \
  --period 300 \
  --evaluation-periods 3 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --alarm-actions arn:aws:sns:us-east-1:123456:prod-alerts \
  --ok-actions arn:aws:sns:us-east-1:123456:prod-alerts \
  --treat-missing-data notBreaching
```

### 參數解析

```
--period 300                 → 每 5 分鐘看一次
--evaluation-periods 3       → 連續 3 次
--threshold 80               → CPU 超過 80%
--comparison-operator GreaterThanThreshold
  → 合起來: 連續 15 分鐘 CPU 平均 > 80% 就觸發

--alarm-actions              → ALARM 時通知
--ok-actions                 → 恢復正常時也通知（知道問題已解決）
--treat-missing-data notBreaching → 沒資料時不算超標
```

### treat-missing-data 選項

| 值 | 行為 | 適用情境 |
|---|---|---|
| `missing` | 維持當前狀態 | 預設 |
| `notBreaching` | 當作沒超標 | 資源可能不存在（scaling to 0） |
| `breaching` | 當作超標 | 資料消失本身就是問題 |
| `ignore` | 不計入評估 | 忽略資料缺口 |

---

## Terraform 實作

### 完整範例：ECS 監控 + SNS 通知

```hcl
# ==============================================================
# sns.tf — 通知主題
# ==============================================================

resource "aws_sns_topic" "alerts" {
  name = "${var.project}-${var.environment}-alerts"

  tags = {
    Project     = var.project
    Environment = var.environment
  }
}

# Email 訂閱（apply 後要去信箱確認！）
resource "aws_sns_topic_subscription" "email" {
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email
}

# 如果要多人訂閱
variable "alert_emails" {
  type    = list(string)
  default = ["dev-team@example.com", "oncall@example.com"]
}

resource "aws_sns_topic_subscription" "emails" {
  for_each  = toset(var.alert_emails)
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = each.value
}
```

```hcl
# ==============================================================
# alarms.tf — CloudWatch Alarms
# ==============================================================

# --- ECS CPU Alarm ---
resource "aws_cloudwatch_metric_alarm" "ecs_cpu_high" {
  alarm_name          = "${var.project}-${var.environment}-ecs-cpu-high"
  alarm_description   = "ECS CPU utilization > 80% for 15 minutes"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 3
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ECS"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  treat_missing_data  = "notBreaching"

  dimensions = {
    ClusterName = aws_ecs_cluster.main.name
    ServiceName = aws_ecs_service.app.name
  }

  alarm_actions = [aws_sns_topic.alerts.arn]
  ok_actions    = [aws_sns_topic.alerts.arn]

  tags = {
    Severity = "warning"
  }
}

# --- ECS Memory Alarm ---
resource "aws_cloudwatch_metric_alarm" "ecs_memory_high" {
  alarm_name          = "${var.project}-${var.environment}-ecs-memory-high"
  alarm_description   = "ECS Memory utilization > 85% for 10 minutes"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "MemoryUtilization"
  namespace           = "AWS/ECS"
  period              = 300
  statistic           = "Average"
  threshold           = 85
  treat_missing_data  = "notBreaching"

  dimensions = {
    ClusterName = aws_ecs_cluster.main.name
    ServiceName = aws_ecs_service.app.name
  }

  alarm_actions = [aws_sns_topic.alerts.arn]
  ok_actions    = [aws_sns_topic.alerts.arn]
}

# --- ALB 5XX Error Alarm ---
resource "aws_cloudwatch_metric_alarm" "alb_5xx" {
  alarm_name          = "${var.project}-${var.environment}-alb-5xx"
  alarm_description   = "ALB target 5XX errors > 10 in 5 minutes"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "HTTPCode_Target_5XX_Count"
  namespace           = "AWS/ApplicationELB"
  period              = 300
  statistic           = "Sum"
  threshold           = 10
  treat_missing_data  = "notBreaching"

  dimensions = {
    LoadBalancer = aws_lb.main.arn_suffix
    TargetGroup  = aws_lb_target_group.main.arn_suffix
  }

  alarm_actions = [aws_sns_topic.alerts.arn]
}

# --- ALB Healthy Host Count Alarm ---
resource "aws_cloudwatch_metric_alarm" "unhealthy_hosts" {
  alarm_name          = "${var.project}-${var.environment}-unhealthy-hosts"
  alarm_description   = "Healthy host count < desired count"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 2
  metric_name         = "HealthyHostCount"
  namespace           = "AWS/ApplicationELB"
  period              = 60
  statistic           = "Minimum"
  threshold           = var.desired_count
  treat_missing_data  = "breaching"

  dimensions = {
    LoadBalancer = aws_lb.main.arn_suffix
    TargetGroup  = aws_lb_target_group.main.arn_suffix
  }

  alarm_actions = [aws_sns_topic.alerts.arn]
  ok_actions    = [aws_sns_topic.alerts.arn]
}

# --- ALB Response Time Alarm ---
resource "aws_cloudwatch_metric_alarm" "response_time" {
  alarm_name          = "${var.project}-${var.environment}-slow-response"
  alarm_description   = "Average response time > 2 seconds for 10 minutes"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "TargetResponseTime"
  namespace           = "AWS/ApplicationELB"
  period              = 300
  statistic           = "Average"
  threshold           = 2
  treat_missing_data  = "notBreaching"

  dimensions = {
    LoadBalancer = aws_lb.main.arn_suffix
  }

  alarm_actions = [aws_sns_topic.alerts.arn]
}
```

```hcl
# ==============================================================
# outputs.tf — 查看建好的資源
# ==============================================================

output "sns_topic_arn" {
  value = aws_sns_topic.alerts.arn
}

output "alarm_names" {
  value = [
    aws_cloudwatch_metric_alarm.ecs_cpu_high.alarm_name,
    aws_cloudwatch_metric_alarm.ecs_memory_high.alarm_name,
    aws_cloudwatch_metric_alarm.alb_5xx.alarm_name,
    aws_cloudwatch_metric_alarm.unhealthy_hosts.alarm_name,
    aws_cloudwatch_metric_alarm.response_time.alarm_name,
  ]
}
```

### 用 Module 封裝（進階）

```hcl
# modules/ecs-alarm/variables.tf
variable "cluster_name" { type = string }
variable "service_name" { type = string }
variable "sns_topic_arn" { type = string }
variable "cpu_threshold" { type = number; default = 80 }
variable "memory_threshold" { type = number; default = 85 }

# modules/ecs-alarm/main.tf
resource "aws_cloudwatch_metric_alarm" "cpu" {
  alarm_name          = "${var.service_name}-cpu-high"
  comparison_operator = "GreaterThanThreshold"
  # ... (同上)
}

# 使用
module "api_alarms" {
  source        = "./modules/ecs-alarm"
  cluster_name  = "prod"
  service_name  = "api"
  sns_topic_arn = aws_sns_topic.alerts.arn
  cpu_threshold = 75   # 可以每個 service 設不同門檻
}

module "worker_alarms" {
  source        = "./modules/ecs-alarm"
  cluster_name  = "prod"
  service_name  = "worker"
  sns_topic_arn = aws_sns_topic.alerts.arn
  cpu_threshold = 90   # worker 比較吃 CPU，門檻設高一點
}
```

---

## AWS CLI 操作

### 查詢 Metric 資料

```bash
# 查看最近 1 小時的 ECS CPU（每 5 分鐘一個點）
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name CPUUtilization \
  --dimensions Name=ClusterName,Value=prod Name=ServiceName,Value=my-app \
  --start-time $(date -u -v-1H +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average Maximum
```

### 查看 Alarm 狀態

```bash
# 列出所有 alarm
aws cloudwatch describe-alarms

# 只看 ALARM 狀態的
aws cloudwatch describe-alarms --state-value ALARM

# 看特定 alarm
aws cloudwatch describe-alarms --alarm-names "ecs-high-cpu"
```

### 手動觸發 Alarm（測試用）

```bash
# 強制 alarm 進入 ALARM 狀態（測試 SNS 是否正常）
aws cloudwatch set-alarm-state \
  --alarm-name "ecs-high-cpu" \
  --state-value ALARM \
  --state-reason "Testing notification"
```

### SNS 相關

```bash
# 列出所有 topic
aws sns list-topics

# 列出某 topic 的訂閱者
aws sns list-subscriptions-by-topic \
  --topic-arn arn:aws:sns:us-east-1:123456:prod-alerts

# 發測試通知
aws sns publish \
  --topic-arn arn:aws:sns:us-east-1:123456:prod-alerts \
  --subject "[TEST] Alert" \
  --message "This is a test. Please ignore."
```

---

## 實際情境範例

### 情境 1：ECS Service 部署後 health check 失敗

**問題：** 部署新版本後，container 起不來，healthy host 歸零

**監控設定：**
```
Metric: HealthyHostCount
Condition: < desired_count
Period: 60s, EvaluationPeriods: 2
→ 2 分鐘內健康實例少於預期就通知
```

**收到通知後怎麼查：**
```bash
# 1. 看 ECS 事件
aws ecs describe-services --cluster prod --services my-app \
  --query "services[0].events[:5]"

# 2. 看 task 為什麼停止
aws ecs describe-tasks --cluster prod --tasks <task-arn> \
  --query "tasks[0].stoppedReason"

# 3. 看 container log
aws logs get-log-events \
  --log-group-name /ecs/my-app-prod \
  --log-stream-name ecs/app/<task-id>
```

### 情境 2：突然大量 5XX 錯誤

**問題：** 某個 API endpoint 開始回 500

**監控設定：**
```
Metric: HTTPCode_Target_5XX_Count
Condition: Sum > 10 in 5 minutes
→ 5 分鐘內超過 10 個 5XX 就通知
```

**為什麼用 Sum 不是 Average：**
- 5XX 是「次數」，要看總共發生幾次
- Average 沒意義（平均錯誤次數？）

### 情境 3：CPU 持續高，需要 auto scaling

**問題：** 流量增加，CPU 居高不下

**監控設定：**
```
Metric: CPUUtilization
Condition: Average > 80% for 15 minutes (3 × 5min)
Action 1: SNS 通知團隊
Action 2: Auto Scaling 自動加 task（另外設定）
```

**為什麼 EvaluationPeriods=3：**
- 避免短暫 spike 就觸發
- 15 分鐘持續高才是真的需要擴容

### 情境 4：深夜 on-call 分層通知

```hcl
# 不同嚴重程度用不同 SNS Topic
resource "aws_sns_topic" "warning" {
  name = "prod-warning"   # → Email 通知
}

resource "aws_sns_topic" "critical" {
  name = "prod-critical"  # → SMS + PagerDuty
}

# Warning: CPU > 70%
resource "aws_cloudwatch_metric_alarm" "cpu_warning" {
  # ...
  threshold     = 70
  alarm_actions = [aws_sns_topic.warning.arn]
}

# Critical: CPU > 90%
resource "aws_cloudwatch_metric_alarm" "cpu_critical" {
  # ...
  threshold     = 90
  alarm_actions = [aws_sns_topic.critical.arn]
}
```

---

## Best Practices

### Alarm 設計原則

1. **避免誤報 (Alert Fatigue)**
   - 用 `EvaluationPeriods` 過濾短暫 spike
   - 別把門檻設太低（CPU 50% 就報？太吵了）
   - 用 `DatapointsToAlarm` 允許偶爾超標

2. **分層告警**
   - Warning (70%) → Email，上班時間看
   - Critical (90%) → SMS/PagerDuty，立刻處理

3. **一定要設 OK Actions**
   - ALARM 時通知你有問題
   - OK 時通知你問題已恢復
   - 不然你不知道什麼時候好了

4. **命名規範**
   ```
   {project}-{environment}-{service}-{metric}-{severity}
   例: myapp-prod-api-cpu-warning
   ```

### SNS 設計原則

1. **按環境分 Topic**
   - `prod-alerts`：正式環境，所有人訂閱
   - `dev-alerts`：開發環境，只有開發者訂閱

2. **按嚴重程度分 Topic**
   - `prod-warning`：非緊急，Email
   - `prod-critical`：緊急，SMS + PagerDuty

3. **用 Filter Policy 精細控制**
   ```json
   // 訂閱者只收特定類型的通知
   {
     "severity": ["critical"],
     "service": ["api", "payment"]
   }
   ```

### 該監控什麼？（基本清單）

| 層級 | 監控項目 | 門檻建議 |
|---|---|---|
| **ECS** | CPU Utilization | Warning 70%, Critical 90% |
| **ECS** | Memory Utilization | Warning 80%, Critical 90% |
| **ALB** | 5XX Error Count | > 10/5min |
| **ALB** | HealthyHostCount | < desired count |
| **ALB** | Response Time | > 2s average |
| **RDS** | CPU | Warning 70%, Critical 85% |
| **RDS** | Free Storage | < 20% |
| **RDS** | Database Connections | > 80% of max |

### 除了 Email 還能通知到哪？

| 方式 | 怎麼接 | 適合誰 |
|---|---|---|
| **Email** | SNS → email protocol | 所有人 |
| **Slack** | SNS → Lambda → Slack Webhook | 團隊 channel |
| **Microsoft Teams** | SNS → Lambda → Teams Webhook | 團隊 channel |
| **PagerDuty** | SNS → HTTPS endpoint | On-call 工程師 |
| **SMS** | SNS → sms protocol | 緊急聯絡人 |
| **Lambda** | SNS → Lambda | 自動修復 |

### Slack 整合範例（透過 AWS Chatbot）

```
最簡單的方式: 用 AWS Chatbot (不用自己寫 Lambda)

1. 到 AWS Chatbot Console
2. Configure new client → Slack
3. 授權 AWS 存取你的 Slack workspace
4. Create channel configuration
5. 選擇 SNS topic + Slack channel
6. 完成！Alarm 會自動發到 Slack
```

---

## 與其他筆記的關聯

- **terraform-ecs.md** → Alarm 的 Terraform 寫法整合到 ECS 部署裡
- **notes/aws/ecs.md** → ECS 的 Metrics 從這裡產生
- **notes/aws/alb.md** → ALB 的 Metrics 從這裡產生
- **cicd-pipeline.md** → 部署後自動驗證 alarm 狀態
