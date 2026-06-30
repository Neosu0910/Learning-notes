# Terraform + AWS ECS 完整學習筆記

## 目錄
1. [Terraform 是什麼](#terraform-是什麼)
2. [核心概念](#核心概念)
3. [基本語法 (HCL)](#基本語法-hcl)
4. [Terraform 工作流程](#terraform-工作流程)
5. [ECS 架構概覽](#ecs-架構概覽)
6. [實作：用 Terraform 部署 ECS Service](#實作用-terraform-部署-ecs-service)
7. [進階主題](#進階主題)
8. [常用指令速查](#常用指令速查)

---

## Terraform 是什麼

**一句話：** 用程式碼定義基礎設施，執行後自動在 AWS 上建立/修改/刪除資源。

### 為什麼需要 Terraform？

| 手動操作 (Console) | Terraform (IaC) |
|---|---|
| 去 AWS Console 點點點建 ECS | 寫 `.tf` 檔案，`terraform apply` 就建好 |
| 忘了上次改了什麼 | git 追蹤每次變更 |
| 環境不一致 (dev/staging/prod) | 同一份 code + 不同 variables = 一致的環境 |
| 刪除資源要一個一個找 | `terraform destroy` 全部清掉 |
| 多人協作容易衝突 | state file + plan 讓你看到變更差異 |

### Terraform vs 其他工具

| 工具 | 定位 |
|---|---|
| **Terraform** | 宣告式 IaC，跨雲 (AWS/GCP/Azure) |
| **CloudFormation** | AWS 原生 IaC，只能用在 AWS |
| **CDK** | 用程式語言 (Python/TS) 產生 CloudFormation |
| **Ansible** | 偏向設定管理 (裝軟體、改 config)，不是建基礎設施 |

---

## 核心概念

### 1. Provider（供應商）
告訴 Terraform 你要管理哪個雲端平台的資源。

```hcl
provider "aws" {
  region = "us-east-1"
}
```

### 2. Resource（資源）
你要建立的東西。每個 resource 有一個 type 和一個自訂名稱。

```hcl
resource "aws_ecs_cluster" "main" {
  name = "my-cluster"
}
```
- `aws_ecs_cluster` → resource type（AWS ECS Cluster）
- `"main"` → 你在 Terraform 裡的代稱（不是 AWS 上的名字）

### 3. Data Source（資料來源）
讀取已經存在的資源（不是建立，而是查詢）。

```hcl
data "aws_vpc" "default" {
  default = true
}
```

### 4. Variable（變數）
讓設定值可以從外部傳入，不用寫死。

```hcl
variable "environment" {
  type    = string
  default = "dev"
}

# 使用: var.environment
```

### 5. Output（輸出）
apply 完後顯示你需要的資訊（例如 ALB 的 DNS）。

```hcl
output "alb_dns" {
  value = aws_lb.main.dns_name
}
```

### 6. State（狀態檔）
Terraform 用 `terraform.tfstate` 記錄「目前 AWS 上有什麼資源」，下次 apply 時比對差異。

⚠️ **重要：state file 包含敏感資訊，不要 commit 到 git！** 團隊協作時放在 S3 backend。

### 7. Module（模組）
把一組相關的 resource 打包成可重用的單位。

```hcl
module "ecs_service" {
  source = "./modules/ecs-service"
  
  cluster_id = aws_ecs_cluster.main.id
  image      = "my-app:latest"
}
```

---

## 基本語法 (HCL)

HCL (HashiCorp Configuration Language) 是 Terraform 的設定語言。

### 基本結構

```hcl
# 這是註解

# Block 語法: type "label1" "label2" { ... }
resource "aws_instance" "web" {
  ami           = "ami-12345"     # 字串
  instance_type = "t3.micro"
  count         = 2               # 數字
  
  tags = {                        # Map
    Name = "web-server"
    Env  = var.environment
  }
}
```

### 型別

```hcl
# 字串
name = "my-app"

# 數字
port = 8080

# 布林
enable_logging = true

# List
subnets = ["subnet-aaa", "subnet-bbb"]

# Map
tags = {
  Name = "my-app"
  Team = "backend"
}
```

### 字串插值

```hcl
name = "${var.project}-${var.environment}-cluster"
# 結果: "myapp-prod-cluster"
```

### 條件表達式

```hcl
instance_type = var.environment == "prod" ? "t3.large" : "t3.micro"
```

### 迴圈 (for_each)

```hcl
variable "services" {
  default = {
    api     = { port = 8080, cpu = 256 }
    worker  = { port = 0,    cpu = 512 }
  }
}

resource "aws_ecs_service" "this" {
  for_each = var.services
  
  name            = each.key          # "api" 或 "worker"
  task_definition = each.value.cpu    # 256 或 512
}
```

### 參照其他資源

```hcl
# 語法: resource_type.resource_name.attribute
resource "aws_ecs_cluster" "main" {
  name = "prod-cluster"
}

resource "aws_ecs_service" "api" {
  cluster = aws_ecs_cluster.main.id    # ← 參照上面的 cluster
}
```

---

## Terraform 工作流程

```
terraform init  →  terraform plan  →  terraform apply  →  terraform destroy
   初始化             預覽變更            實際執行              清除全部
```

### 1. `terraform init`
- 下載 provider plugin（例如 aws provider）
- 初始化 backend（state 存放位置）
- 只需要第一次或加了新 provider 時跑

### 2. `terraform plan`
- 比對 .tf 檔案 vs state file vs 實際 AWS 狀態
- 顯示要 create / update / destroy 什麼
- **不會真的改任何東西**，純預覽

### 3. `terraform apply`
- 執行 plan 裡的變更
- 會先顯示 plan，問你 yes/no
- 執行後更新 state file

### 4. `terraform destroy`
- 刪除所有由這份 Terraform 管理的資源
- 通常只在 dev/test 環境用

### 檔案結構慣例

```
terraform/
├── main.tf          # 主要資源定義
├── variables.tf     # 變數宣告
├── outputs.tf       # 輸出值
├── provider.tf      # Provider 設定
├── terraform.tfvars # 變數的值（不要 commit 敏感資料）
├── backend.tf       # State 存放設定
└── modules/         # 自訂模組
    └── ecs-service/
        ├── main.tf
        ├── variables.tf
        └── outputs.tf
```

---

## ECS 架構概覽

在寫 Terraform 之前，先搞清楚 ECS 的元件關係：

```
ECS Cluster
└── ECS Service (管理 desired count, 滾動更新)
    └── Task Definition (定義 container 規格)
        └── Container Definition (image, port, env vars)

搭配的資源:
├── ALB (Application Load Balancer) → 接外部流量
├── Target Group → ALB 把流量導到哪些 task
├── Security Group → 防火牆規則
├── IAM Role → ECS task 的權限
├── CloudWatch Log Group → container logs
└── ECR Repository → 存放 Docker image
```

### ECS Fargate vs EC2 Launch Type

| | Fargate | EC2 |
|---|---|---|
| 管理 | 不用管 server | 要自己管 EC2 instance |
| 成本 | 按 task 計費，稍貴 | 便宜但要管更多東西 |
| 適用 | 多數情境，尤其剛開始 | 大量穩定 workload |
| Terraform 複雜度 | 低 | 高（要多管 ASG, Launch Template） |

---

## 實作：用 Terraform 部署 ECS Service

### 練習 1：最小可運行 ECS（Fargate）

這是一個完整的例子，部署一個 nginx container 到 ECS Fargate。

```hcl
# ==============================================================
# provider.tf — AWS Provider 設定
# ==============================================================

terraform {
  required_version = ">= 1.5"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}
```

```hcl
# ==============================================================
# variables.tf — 變數定義
# ==============================================================

variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "project" {
  type    = string
  default = "my-app"
}

variable "environment" {
  type    = string
  default = "dev"
}

variable "container_image" {
  type    = string
  default = "nginx:latest"
}

variable "container_port" {
  type    = number
  default = 80
}

variable "task_cpu" {
  type    = number
  default = 256   # 0.25 vCPU
}

variable "task_memory" {
  type    = number
  default = 512   # 512 MB
}

variable "desired_count" {
  type    = number
  default = 2
}
```

```hcl
# ==============================================================
# networking.tf — VPC, Subnets, Security Groups
# ==============================================================

# 使用預設 VPC（練習用，正式環境會自建）
data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

# ALB 的 Security Group — 允許外部 80 port 進來
resource "aws_security_group" "alb" {
  name   = "${var.project}-${var.environment}-alb-sg"
  vpc_id = data.aws_vpc.default.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project}-${var.environment}-alb-sg"
  }
}

# ECS Task 的 Security Group — 只允許從 ALB 進來
resource "aws_security_group" "ecs_task" {
  name   = "${var.project}-${var.environment}-ecs-sg"
  vpc_id = data.aws_vpc.default.id

  ingress {
    from_port       = var.container_port
    to_port         = var.container_port
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]  # ← 只有 ALB 能連
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project}-${var.environment}-ecs-sg"
  }
}
```

```hcl
# ==============================================================
# alb.tf — Application Load Balancer
# ==============================================================

resource "aws_lb" "main" {
  name               = "${var.project}-${var.environment}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = data.aws_subnets.default.ids

  tags = {
    Name = "${var.project}-${var.environment}-alb"
  }
}

resource "aws_lb_target_group" "main" {
  name        = "${var.project}-${var.environment}-tg"
  port        = var.container_port
  protocol    = "HTTP"
  vpc_id      = data.aws_vpc.default.id
  target_type = "ip"   # ← Fargate 必須用 "ip"，不是 "instance"

  health_check {
    path                = "/"
    healthy_threshold   = 2
    unhealthy_threshold = 3
    timeout             = 5
    interval            = 30
  }
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.main.arn
  }
}
```

```hcl
# ==============================================================
# iam.tf — ECS 需要的 IAM Roles
# ==============================================================

# Task Execution Role — ECS 用來拉 image、寫 log
resource "aws_iam_role" "ecs_execution" {
  name = "${var.project}-${var.environment}-ecs-execution"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_execution" {
  role       = aws_iam_role.ecs_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# Task Role — 你的 container 執行時的權限（例如存取 S3, DynamoDB）
resource "aws_iam_role" "ecs_task" {
  name = "${var.project}-${var.environment}-ecs-task"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }
    }]
  })
}

# 如果你的 app 需要存取 S3，在這裡加 policy
# resource "aws_iam_role_policy" "task_s3" {
#   role = aws_iam_role.ecs_task.id
#   policy = jsonencode({ ... })
# }
```

```hcl
# ==============================================================
# ecs.tf — ECS Cluster, Task Definition, Service
# ==============================================================

# CloudWatch Log Group — container 的 log 存這裡
resource "aws_cloudwatch_log_group" "app" {
  name              = "/ecs/${var.project}-${var.environment}"
  retention_in_days = 7
}

# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "${var.project}-${var.environment}"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

# Task Definition — 定義 container 規格
resource "aws_ecs_task_definition" "app" {
  family                   = "${var.project}-${var.environment}"
  network_mode             = "awsvpc"        # Fargate 必須用 awsvpc
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.task_cpu
  memory                   = var.task_memory
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([
    {
      name  = "app"
      image = var.container_image
      
      portMappings = [{
        containerPort = var.container_port
        protocol      = "tcp"
      }]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.app.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }

      environment = [
        { name = "ENV", value = var.environment },
      ]

      # 如果有 secrets (從 Secrets Manager 或 Parameter Store):
      # secrets = [
      #   { name = "DB_PASSWORD", valueFrom = "arn:aws:ssm:..." }
      # ]
    }
  ])
}

# ECS Service — 管理 task 數量和部署策略
resource "aws_ecs_service" "app" {
  name            = "${var.project}-${var.environment}"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.app.arn
  desired_count   = var.desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = data.aws_subnets.default.ids
    security_groups  = [aws_security_group.ecs_task.id]
    assign_public_ip = true   # 用 public subnet 時需要
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.main.arn
    container_name   = "app"
    container_port   = var.container_port
  }

  # 滾動更新設定
  deployment_minimum_healthy_percent = 50
  deployment_maximum_percent         = 200

  # 避免第一次 apply 時 ALB 還沒好就建 service
  depends_on = [aws_lb_listener.http]
}
```

```hcl
# ==============================================================
# outputs.tf — 部署完成後顯示的資訊
# ==============================================================

output "alb_dns_name" {
  description = "ALB 的 DNS 名稱，用瀏覽器打開就能看到你的 app"
  value       = aws_lb.main.dns_name
}

output "cluster_name" {
  value = aws_ecs_cluster.main.name
}

output "service_name" {
  value = aws_ecs_service.app.name
}
```

### 部署步驟

```bash
# 1. 初始化（下載 aws provider）
terraform init

# 2. 預覽要建什麼
terraform plan

# 3. 執行部署（會問你 yes/no）
terraform apply

# 4. 部署完成後看 output
# 用瀏覽器打開 alb_dns_name 的值就能看到 nginx 頁面

# 5. 清除所有資源（練習完記得刪，不然要收費）
terraform destroy
```

---

### 練習 2：更新 Container Image（模擬 CI/CD deploy）

真實情境：你 push 新 code → CI 建好新 image → 需要更新 ECS service。

```bash
# 方法 1: 改 terraform.tfvars 裡的 image tag
# container_image = "123456.dkr.ecr.us-east-1.amazonaws.com/my-app:v2"
terraform apply

# 方法 2: 用 -var 覆蓋（CI/CD pipeline 常用）
terraform apply -var="container_image=my-app:v2"
```

Terraform 偵測到 task definition 的 image 改了 → 建新的 task definition revision → ECS service 自動做 rolling update。

---

### 練習 3：加入 Auto Scaling

```hcl
# ==============================================================
# autoscaling.tf — 根據 CPU 使用率自動調整 task 數量
# ==============================================================

resource "aws_appautoscaling_target" "ecs" {
  max_capacity       = 10
  min_capacity       = 2
  resource_id        = "service/${aws_ecs_cluster.main.name}/${aws_ecs_service.app.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

# CPU > 70% 時加 task
resource "aws_appautoscaling_policy" "cpu" {
  name               = "${var.project}-cpu-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.ecs.resource_id
  scalable_dimension = aws_appautoscaling_target.ecs.scalable_dimension
  service_namespace  = aws_appautoscaling_target.ecs.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    target_value = 70.0
  }
}
```

---

### 練習 4：多環境管理 (dev/staging/prod)

用 `terraform.tfvars` 檔案切換環境：

```
terraform/
├── environments/
│   ├── dev.tfvars        # desired_count=1, task_cpu=256
│   ├── staging.tfvars    # desired_count=2, task_cpu=512
│   └── prod.tfvars       # desired_count=4, task_cpu=1024
└── ...其他 .tf 檔案
```

```bash
# 部署 dev
terraform apply -var-file="environments/dev.tfvars"

# 部署 prod
terraform apply -var-file="environments/prod.tfvars"
```

`dev.tfvars`:
```hcl
environment     = "dev"
desired_count   = 1
task_cpu        = 256
task_memory     = 512
container_image = "my-app:dev-latest"
```

`prod.tfvars`:
```hcl
environment     = "prod"
desired_count   = 4
task_cpu        = 1024
task_memory     = 2048
container_image = "my-app:v1.2.3"
```

---

### 練習 5：Remote State（團隊協作）

```hcl
# backend.tf — 把 state 存在 S3，團隊共用

terraform {
  backend "s3" {
    bucket         = "my-company-terraform-state"
    key            = "ecs/my-app/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-locks"   # 防止同時 apply
    encrypt        = true
  }
}
```

需要先手動建立 S3 bucket 和 DynamoDB table（雞生蛋問題）。

---

## 進階主題

### 1. Terraform Lifecycle

```hcl
resource "aws_ecs_service" "app" {
  # ...

  lifecycle {
    # 忽略外部變更（例如 auto scaling 改了 desired_count）
    ignore_changes = [desired_count]
    
    # 先建新的再刪舊的（避免服務中斷）
    create_before_destroy = true
  }
}
```

### 2. 用 Locals 整理重複邏輯

```hcl
locals {
  name_prefix = "${var.project}-${var.environment}"
  common_tags = {
    Project     = var.project
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

resource "aws_ecs_cluster" "main" {
  name = "${local.name_prefix}-cluster"
  tags = local.common_tags
}
```

### 3. 敏感資料處理

```hcl
# 從 AWS Secrets Manager 拉 secret
data "aws_secretsmanager_secret_version" "db_password" {
  secret_id = "my-app/db-password"
}

# 在 container definition 中引用
secrets = [
  {
    name      = "DB_PASSWORD"
    valueFrom = data.aws_secretsmanager_secret_version.db_password.arn
  }
]
```

### 4. Blue/Green Deployment（搭配 CodeDeploy）

```hcl
resource "aws_ecs_service" "app" {
  # ...
  
  deployment_controller {
    type = "CODE_DEPLOY"   # 改用 CodeDeploy 控制部署
  }
}
```

---

## 常用指令速查

| 指令 | 用途 |
|---|---|
| `terraform init` | 初始化，下載 provider |
| `terraform plan` | 預覽變更，不實際執行 |
| `terraform apply` | 執行變更 |
| `terraform destroy` | 刪除所有資源 |
| `terraform fmt` | 自動格式化 .tf 檔案 |
| `terraform validate` | 檢查語法是否正確 |
| `terraform state list` | 列出目前管理的資源 |
| `terraform state show aws_ecs_cluster.main` | 看某個資源的詳細狀態 |
| `terraform import aws_ecs_cluster.main my-cluster` | 匯入已存在的資源 |
| `terraform output` | 顯示所有 output 值 |
| `terraform plan -target=aws_ecs_service.app` | 只 plan 特定資源 |

---

## 學習路徑建議

1. **先讀懂這份筆記的架構圖** — 理解 Cluster → Service → Task Definition 的關係
2. **在本地跑 `terraform plan`** — 不用真的 apply，看 plan output 理解它要做什麼
3. **用 free tier 或測試帳號跑一次完整 flow** — init → plan → apply → 打開 ALB URL → destroy
4. **練習改 variable 重新 deploy** — 改 image、改 desired_count，觀察 rolling update
5. **加入 autoscaling 和 多環境** — 練習 3 和 4
6. **看你們公司的 Terraform code** — 對照這份筆記理解每個 block 在幹嘛
