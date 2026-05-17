# AWS ECS 筆記

ECS（Elastic Container Service）是 AWS 的容器編排服務，讓你可以在 AWS 上跑 Docker 容器，不需要自己管理 Kubernetes 叢集。它負責幫你決定容器要跑在哪台機器上、掛掉時自動重啟、以及根據流量自動擴縮。

---

## 核心概念

### ECS vs 自己管 Docker

```
自己管 Docker：
  你要負責 → 哪台機器跑哪個容器、容器掛掉要重啟、機器不夠要加機器

ECS：
  你只需要說 → 「我要跑這個 Image，給它 0.5 CPU 和 512MB 記憶體」
  ECS 負責 → 找機器、排程、健康檢查、自動重啟、擴縮
```

### 四個核心元件

```
ECS Cluster（叢集）
  └── ECS Service（服務）
        └── Task Definition（任務定義）
              └── Task（任務，實際跑的容器）
```

---

## 啟動類型：EC2 vs Fargate

ECS 有兩種啟動方式，差別在於你要不要管底層機器：

| | EC2 Launch Type | Fargate Launch Type |
|--|-----------------|---------------------|
| 底層機器 | 你管（EC2 instance）| AWS 管（Serverless）|
| 費用 | 按 EC2 instance 計費 | 按容器用的 CPU/記憶體計費 |
| 控制程度 | 高（可以 SSH 進去）| 低（看不到底層機器）|
| 適合場景 | 需要 GPU、特殊網路設定 | 大多數 Web 應用、API |
| 啟動速度 | 快（機器已在跑）| 稍慢（每次都要分配資源）|

> 新專案建議直接用 **Fargate**，省去管理 EC2 的麻煩。

---

## Task Definition（任務定義）

Task Definition 是容器的「設計圖」，定義要跑什麼 Image、給多少資源、環境變數、Log 設定等。類似 `docker-compose.yml`。

```json
{
  "family": "my-api",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::...:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::...:role/myAppTaskRole",
  "containerDefinitions": [
    {
      "name": "api",
      "image": "123456789.dkr.ecr.ap-northeast-1.amazonaws.com/my-api:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {"name": "ENV", "value": "production"},
        {"name": "DB_HOST", "value": "mydb.xxx.rds.amazonaws.com"}
      ],
      "secrets": [
        {
          "name": "DB_PASSWORD",
          "valueFrom": "arn:aws:secretsmanager:...:secret:my-db-password"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/my-api",
          "awslogs-region": "ap-northeast-1",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3
      }
    }
  ]
}
```

**兩個 IAM Role 的差別：**
| Role | 用途 |
|------|------|
| `executionRoleArn` | ECS 本身需要的權限：拉 ECR Image、寫 CloudWatch Log、讀 Secrets Manager |
| `taskRoleArn` | 你的應用程式需要的權限：存取 S3、DynamoDB、SQS 等 |

---

## ECS Service（服務）

Service 確保指定數量的 Task 持續運行。如果某個 Task 掛掉，Service 會自動啟動新的來補。

```bash
# 建立 ECS Service
aws ecs create-service \
  --cluster my-cluster \
  --service-name my-api-service \
  --task-definition my-api:3 \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={
    subnets=[subnet-aaa,subnet-bbb],
    securityGroups=[sg-xxx],
    assignPublicIp=DISABLED
  }" \
  --load-balancers "targetGroupArn=arn:...,containerName=api,containerPort=8000"
```

**更新部署（Rolling Update）：**
```bash
# 更新 Task Definition 後，強制重新部署
aws ecs update-service \
  --cluster my-cluster \
  --service my-api-service \
  --task-definition my-api:4 \
  --force-new-deployment
```

ECS 預設用 Rolling Update 部署：先啟動新版本的 Task，確認健康後再停掉舊版本，不會中斷服務。

---

## ECR（Elastic Container Registry）

ECR 是 AWS 的 Docker Image 倉庫，類似 Docker Hub，但在 AWS 內部，速度更快、整合更好。

```bash
# 登入 ECR
aws ecr get-login-password --region ap-northeast-1 | \
  docker login --username AWS --password-stdin \
  123456789.dkr.ecr.ap-northeast-1.amazonaws.com

# 建立 Repository
aws ecr create-repository --repository-name my-api

# Build 並推送 Image
docker build -t my-api .
docker tag my-api:latest 123456789.dkr.ecr.ap-northeast-1.amazonaws.com/my-api:latest
docker push 123456789.dkr.ecr.ap-northeast-1.amazonaws.com/my-api:latest
```

**ECR 的優點：**
- 和 ECS、IAM 深度整合，不需要額外設定認證
- Image 存在 AWS 內部，拉取速度快（不走公網）
- 支援 Image 掃描（自動偵測已知漏洞）
- 可設定 Lifecycle Policy 自動清理舊 Image

---

## 網路模式：awsvpc

Fargate 和 EC2 Launch Type 的 Task 都建議用 `awsvpc` 網路模式：每個 Task 有自己獨立的 ENI 和 Private IP，就像一台獨立的機器。

```
VPC
├── Public Subnet
│   └── ALB（接收外部流量）
└── Private Subnet
    ├── ECS Task A（有自己的 ENI: 10.0.1.10）
    ├── ECS Task B（有自己的 ENI: 10.0.1.11）
    └── ECS Task C（有自己的 ENI: 10.0.1.12）
```

**Security Group 設定：**
```
ALB Security Group:
  Inbound: TCP/443 from 0.0.0.0/0

ECS Task Security Group:
  Inbound: TCP/8000 from ALB Security Group
  Outbound: 全部允許（讓容器能存取 RDS、S3 等）
```

---

## Auto Scaling

ECS Service 可以根據指標自動調整 Task 數量：

```bash
# 設定 Auto Scaling
aws application-autoscaling register-scalable-target \
  --service-namespace ecs \
  --resource-id service/my-cluster/my-api-service \
  --scalable-dimension ecs:service:DesiredCount \
  --min-capacity 2 \
  --max-capacity 20

# 依 CPU 使用率自動擴縮（目標追蹤策略）
aws application-autoscaling put-scaling-policy \
  --service-namespace ecs \
  --resource-id service/my-cluster/my-api-service \
  --scalable-dimension ecs:service:DesiredCount \
  --policy-name cpu-scaling \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration '{
    "TargetValue": 70.0,
    "PredefinedMetricSpecification": {
      "PredefinedMetricType": "ECSServiceAverageCPUUtilization"
    },
    "ScaleInCooldown": 300,
    "ScaleOutCooldown": 60
  }'
```

這個設定的意思：維持平均 CPU 在 70%，低於時縮減 Task，高於時增加 Task。

---

## Log 收集

ECS Task 的 Log 透過 `awslogs` driver 自動送到 CloudWatch Logs：

```bash
# 查看 ECS Service 的 Log
aws logs tail /ecs/my-api --follow

# 或在 CloudWatch Console 找到對應的 Log Group
# Log Group 名稱：/ecs/my-api
# Log Stream 名稱：ecs/api/<task-id>
```

---

## 完整部署流程（CI/CD）

```
1. 開發者 push 程式碼到 GitHub
        ↓
2. GitHub Actions 觸發
        ↓
3. docker build → docker push 到 ECR
        ↓
4. 更新 Task Definition（新的 Image tag）
        ↓
5. aws ecs update-service --force-new-deployment
        ↓
6. ECS 執行 Rolling Update
   - 啟動新版本 Task
   - ALB Health Check 通過
   - 停掉舊版本 Task
        ↓
7. 部署完成，零停機
```

```yaml
# GitHub Actions 範例
- name: Deploy to ECS
  run: |
    # 更新 Task Definition 裡的 Image
    NEW_IMAGE="$ECR_REGISTRY/my-api:${{ github.sha }}"
    
    # 取得現有 Task Definition 並更新 Image
    TASK_DEF=$(aws ecs describe-task-definition --task-definition my-api)
    NEW_TASK_DEF=$(echo $TASK_DEF | jq --arg IMAGE "$NEW_IMAGE" \
      '.taskDefinition | .containerDefinitions[0].image = $IMAGE | 
       del(.taskDefinitionArn, .revision, .status, .requiresAttributes, 
           .compatibilities, .registeredAt, .registeredBy)')
    
    # 註冊新版本 Task Definition
    NEW_TASK_ARN=$(aws ecs register-task-definition \
      --cli-input-json "$NEW_TASK_DEF" \
      --query 'taskDefinition.taskDefinitionArn' --output text)
    
    # 更新 Service
    aws ecs update-service \
      --cluster my-cluster \
      --service my-api-service \
      --task-definition $NEW_TASK_ARN
```

---

## 常見架構

### 標準 Web API 架構

```
Internet
  └── ALB（Public Subnet）
        └── ECS Service（Fargate, Private Subnet）
              └── Task: FastAPI 容器
                    ├── RDS PostgreSQL（Private Subnet）
                    ├── ElastiCache Redis（Private Subnet）
                    └── S3（透過 VPC Endpoint）
```

### 多服務微服務架構

```
ALB
├── /api/users/*  → ECS Service: user-service
├── /api/orders/* → ECS Service: order-service
└── /api/notify/* → ECS Service: notification-service
                          └── SQS Queue
                                └── ECS Service: worker（背景處理）
```

---

## 常見問題排查

| 問題 | 可能原因 | 排查方式 |
|------|---------|---------|
| Task 一直重啟 | 容器啟動後立刻 crash | 看 CloudWatch Logs 的錯誤訊息 |
| Task 停在 PENDING | 資源不足或網路設定錯誤 | 檢查 Subnet、Security Group、IAM Role |
| Health Check 失敗 | `/health` 端點沒有回應 200 | 確認容器有正確啟動、Port 設定正確 |
| 拉不到 ECR Image | `executionRole` 沒有 ECR 權限 | 確認 `ecsTaskExecutionRole` 有 `AmazonECRReadOnly` Policy |
| 容器無法存取 RDS | Security Group 沒有設定 | 確認 RDS Security Group 允許來自 ECS Task Security Group 的流量 |

**查看 Task 停止原因：**
```bash
# 列出最近停止的 Task
aws ecs list-tasks \
  --cluster my-cluster \
  --service-name my-api-service \
  --desired-status STOPPED

# 查看停止原因
aws ecs describe-tasks \
  --cluster my-cluster \
  --tasks <task-id> \
  --query 'tasks[0].stoppedReason'
```
