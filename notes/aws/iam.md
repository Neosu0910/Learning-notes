# AWS IAM 筆記

IAM（Identity and Access Management）是 AWS 的身份與存取管理服務，控制「**誰**」可以對「**哪些資源**」做「**什麼操作**」。所有 AWS 服務的存取控制都建立在 IAM 之上。

---

## 核心概念

### 四個主要元件

```
IAM User / Role / Group
      ↓ 附加
   IAM Policy（JSON 格式的權限規則）
      ↓ 定義
   允許或拒絕對 AWS 資源的操作
```

| 元件 | 說明 |
|------|------|
| **User** | 代表一個人或一個應用程式，有長期憑證（Access Key 或密碼） |
| **Group** | User 的集合，把 Policy 附加到 Group，Group 裡的 User 都繼承 |
| **Role** | 可以被「扮演」的身份，沒有長期憑證，使用臨時憑證 |
| **Policy** | JSON 格式的權限文件，定義允許或拒絕哪些操作 |

---

## IAM Policy 結構

Policy 是 IAM 的核心，用 JSON 描述權限規則。

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowS3ReadAccess",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::my-bucket",
        "arn:aws:s3:::my-bucket/*"
      ]
    },
    {
      "Sid": "DenyDeleteObject",
      "Effect": "Deny",
      "Action": "s3:DeleteObject",
      "Resource": "arn:aws:s3:::my-bucket/*"
    }
  ]
}
```

**每個 Statement 的欄位：**

| 欄位 | 說明 | 範例 |
|------|------|------|
| `Sid` | Statement ID，可選，用來識別這條規則 | `"AllowS3Read"` |
| `Effect` | `Allow` 或 `Deny` | `"Allow"` |
| `Action` | 允許或拒絕的 API 操作 | `"s3:GetObject"`、`"ec2:*"` |
| `Resource` | 操作對象的 ARN | `"arn:aws:s3:::my-bucket/*"` |
| `Condition` | 附加條件（可選） | 限制來源 IP、MFA 等 |

### Deny 優先原則

IAM 的判斷邏輯：
```
1. 預設全部 Deny（沒有明確 Allow 就是拒絕）
2. 有 Allow → 允許
3. 有 Deny → 無論有沒有 Allow，一律拒絕（Deny 優先）
```

```json
// 即使有 Allow s3:*，這條 Deny 也會讓 DeleteObject 無法執行
{
  "Effect": "Deny",
  "Action": "s3:DeleteObject",
  "Resource": "*"
}
```

### Wildcard（萬用字元）

```json
// Action 萬用字元
"Action": "s3:*"          // S3 的所有操作
"Action": "ec2:Describe*" // 所有 Describe 開頭的 EC2 操作

// Resource 萬用字元
"Resource": "*"                        // 所有資源
"Resource": "arn:aws:s3:::my-bucket/*" // my-bucket 裡的所有物件
```

---

## IAM User

IAM User 代表一個人或服務帳號，有兩種憑證：

| 憑證類型 | 用途 | 注意 |
|---------|------|------|
| 密碼 | 登入 AWS Console | 建議開啟 MFA |
| Access Key（Key ID + Secret） | 程式化存取（CLI、SDK） | 不要放進程式碼或 git |

### 最佳實踐

```bash
# ❌ 不好的做法：把 Access Key 寫死在程式碼裡
import boto3
s3 = boto3.client(
    "s3",
    aws_access_key_id="AKIAIOSFODNN7EXAMPLE",      # 危險！
    aws_secret_access_key="wJalrXUtnFEMI/K7MDENG"  # 危險！
)

# ✅ 好的做法：用環境變數或 IAM Role
# boto3 會自動從環境變數、~/.aws/credentials 或 Instance Metadata 取得憑證
s3 = boto3.client("s3")
```

```bash
# 設定 AWS CLI 憑證（存在 ~/.aws/credentials）
aws configure
# AWS Access Key ID: AKIAIOSFODNN7EXAMPLE
# AWS Secret Access Key: wJalrXUtnFEMI/K7MDENG
# Default region name: ap-northeast-1
# Default output format: json
```

### Root User vs IAM User

| | Root User | IAM User |
|--|-----------|----------|
| 建立方式 | 建立 AWS 帳號時自動產生 | 在 IAM 裡手動建立 |
| 權限 | 無法限制，擁有所有權限 | 可以精細控制 |
| 日常使用 | **不建議**，只用於帳號層級操作 | 日常操作都用 IAM User |
| MFA | 強烈建議開啟 | 建議開啟 |

> Root User 只應該用於：建立第一個 IAM Admin User、修改帳單設定、關閉帳號。

---

## IAM Role

Role 是 IAM 最重要的概念之一。它不屬於任何人，而是一個「可以被扮演的身份」，扮演後取得**臨時憑證**（有效期限通常 1 小時）。

### Role 的使用場景

```
EC2 / Lambda / ECS Task
      ↓ 扮演（Assume Role）
   IAM Role
      ↓ 附加
   Policy（允許存取 S3、DynamoDB 等）
```

**為什麼用 Role 而不是 User + Access Key：**
- Access Key 是長期憑證，洩漏後一直有效
- Role 的臨時憑證有時效，過期自動失效
- 不需要在 instance 上儲存任何憑證

### Trust Policy（信任政策）

每個 Role 都有一個 Trust Policy，定義「誰可以扮演這個 Role」：

```json
// 允許 EC2 服務扮演這個 Role
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

```json
// 允許另一個 AWS 帳號的 User 扮演這個 Role（跨帳號存取）
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::123456789012:root"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

### 常見 Role 類型

| Role 類型 | 說明 | 例子 |
|---------|------|------|
| EC2 Instance Role | 讓 EC2 存取其他 AWS 服務 | EC2 讀取 S3、寫入 CloudWatch |
| Lambda Execution Role | Lambda 函式的執行身份 | Lambda 讀取 DynamoDB、發送 SQS |
| ECS Task Role | ECS 容器的執行身份 | Container 存取 Secrets Manager |
| Cross-Account Role | 跨帳號存取 | A 帳號的 Lambda 讀取 B 帳號的 S3 |
| Service-Linked Role | AWS 服務自動建立，用於服務內部操作 | ECS 自動建立，用於管理 EC2 |

### 用 CLI 扮演 Role（Assume Role）

```bash
# 取得臨時憑證
aws sts assume-role \
  --role-arn "arn:aws:iam::123456789012:role/MyRole" \
  --role-session-name "my-session"

# 輸出：
# {
#   "Credentials": {
#     "AccessKeyId": "ASIAIOSFODNN7EXAMPLE",
#     "SecretAccessKey": "wJalrXUtnFEMI...",
#     "SessionToken": "AQoDYXdzEJr...",
#     "Expiration": "2026-05-13T12:00:00Z"
#   }
# }

# 設定環境變數使用臨時憑證
export AWS_ACCESS_KEY_ID="ASIAIOSFODNN7EXAMPLE"
export AWS_SECRET_ACCESS_KEY="wJalrXUtnFEMI..."
export AWS_SESSION_TOKEN="AQoDYXdzEJr..."
```

```python
# Python boto3 扮演 Role
import boto3

sts = boto3.client("sts")
response = sts.assume_role(
    RoleArn="arn:aws:iam::123456789012:role/MyRole",
    RoleSessionName="my-session"
)

credentials = response["Credentials"]

# 用臨時憑證建立 client
s3 = boto3.client(
    "s3",
    aws_access_key_id=credentials["AccessKeyId"],
    aws_secret_access_key=credentials["SecretAccessKey"],
    aws_session_token=credentials["SessionToken"]
)
```

---

## IAM Group

Group 是 User 的集合，方便批量管理權限。

```
Developers Group
  ├── Policy: AmazonEC2FullAccess
  ├── Policy: AmazonS3ReadOnlyAccess
  └── Users: alice, bob, charlie

Admins Group
  ├── Policy: AdministratorAccess
  └── Users: neo
```

```bash
# 建立 Group 並附加 Policy
aws iam create-group --group-name Developers

aws iam attach-group-policy \
  --group-name Developers \
  --policy-arn arn:aws:iam::aws:policy/AmazonEC2FullAccess

# 把 User 加入 Group
aws iam add-user-to-group \
  --group-name Developers \
  --user-name alice
```

---

## Policy 類型

| 類型 | 說明 | 管理方 |
|------|------|--------|
| AWS Managed Policy | AWS 預先建立的常用 Policy | AWS |
| Customer Managed Policy | 你自己建立的 Policy，可重複使用 | 你 |
| Inline Policy | 直接嵌入在 User/Group/Role 裡，不能共用 | 你 |

**常用的 AWS Managed Policy：**

| Policy 名稱 | 說明 |
|------------|------|
| `AdministratorAccess` | 完整管理員權限（`*:*`） |
| `ReadOnlyAccess` | 所有服務的唯讀權限 |
| `AmazonS3FullAccess` | S3 完整存取 |
| `AmazonS3ReadOnlyAccess` | S3 唯讀 |
| `AmazonEC2FullAccess` | EC2 完整存取 |
| `AWSLambdaBasicExecutionRole` | Lambda 基本執行（寫 CloudWatch Logs）|
| `CloudWatchLogsFullAccess` | CloudWatch Logs 完整存取 |

---

## Condition（條件）

Policy 可以加上 Condition，讓權限更精細：

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "s3:*",
      "Resource": "*",
      "Condition": {
        "IpAddress": {
          "aws:SourceIp": ["203.0.113.0/24", "198.51.100.0/24"]
        }
      }
    }
  ]
}
```

```json
// 只有開啟 MFA 才能執行敏感操作
{
  "Effect": "Allow",
  "Action": [
    "ec2:StopInstances",
    "ec2:TerminateInstances"
  ],
  "Resource": "*",
  "Condition": {
    "Bool": {
      "aws:MultiFactorAuthPresent": "true"
    }
  }
}
```

```json
// 只允許在特定 Region 操作
{
  "Effect": "Deny",
  "Action": "*",
  "Resource": "*",
  "Condition": {
    "StringNotEquals": {
      "aws:RequestedRegion": ["ap-northeast-1", "us-east-1"]
    }
  }
}
```

**常用 Condition Key：**

| Condition Key | 說明 |
|--------------|------|
| `aws:SourceIp` | 請求來源 IP |
| `aws:MultiFactorAuthPresent` | 是否有 MFA |
| `aws:RequestedRegion` | 請求的 Region |
| `aws:CurrentTime` | 請求時間 |
| `s3:prefix` | S3 物件的前綴 |
| `ec2:Region` | EC2 的 Region |

---

## ARN（Amazon Resource Name）

ARN 是 AWS 資源的唯一識別符，格式如下：

```
arn:partition:service:region:account-id:resource
 │      │        │       │        │         │
 │      │        │       │        │         └── 資源識別（類型/名稱）
 │      │        │       │        └──────────── AWS 帳號 ID（12 位數字）
 │      │        │       └───────────────────── Region（如 ap-northeast-1）
 │      │        └───────────────────────────── 服務（如 s3、ec2、iam）
 │      └────────────────────────────────────── Partition（aws、aws-cn、aws-us-gov）
 └───────────────────────────────────────────── 固定前綴
```

**常見 ARN 範例：**

```
# IAM User
arn:aws:iam::123456789012:user/alice

# IAM Role
arn:aws:iam::123456789012:role/MyLambdaRole

# IAM Policy
arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess   # AWS Managed（帳號 ID 是 aws）
arn:aws:iam::123456789012:policy/MyCustomPolicy   # Customer Managed

# S3 Bucket
arn:aws:s3:::my-bucket          # S3 沒有 Region 和帳號 ID
arn:aws:s3:::my-bucket/*        # Bucket 裡的所有物件

# EC2 Instance
arn:aws:ec2:ap-northeast-1:123456789012:instance/i-1234567890abcdef0

# Lambda Function
arn:aws:lambda:ap-northeast-1:123456789012:function:my-function
```

---

## 實際架構情境

### 情境一：Lambda 存取 DynamoDB 和 S3

```
Lambda Function
  └── Execution Role（IAM Role）
        ├── Policy: 允許讀寫 DynamoDB Table
        ├── Policy: 允許讀取 S3 Bucket
        └── Policy: AWSLambdaBasicExecutionRole（寫 CloudWatch Logs）
```

```json
// Lambda Execution Role 的 Policy
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:UpdateItem",
        "dynamodb:Query"
      ],
      "Resource": "arn:aws:dynamodb:ap-northeast-1:123456789012:table/orders"
    },
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject"],
      "Resource": "arn:aws:s3:::my-assets-bucket/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    }
  ]
}
```

### 情境二：ECS Task 存取 Secrets Manager

```
ECS Task
  └── Task Role（IAM Role）
        └── Policy: 允許讀取特定 Secret
```

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue"
      ],
      "Resource": "arn:aws:secretsmanager:ap-northeast-1:123456789012:secret:prod/db-password-*"
    }
  ]
}
```

```python
# 應用程式從 Secrets Manager 取得密碼
import boto3
import json

def get_db_password():
    client = boto3.client("secretsmanager", region_name="ap-northeast-1")
    response = client.get_secret_value(SecretId="prod/db-password")
    secret = json.loads(response["SecretString"])
    return secret["password"]
    # ECS Task Role 會自動提供憑證，不需要 Access Key
```

### 情境三：跨帳號存取（Cross-Account）

```
帳號 A（開發）                    帳號 B（生產）
  └── Lambda / EC2                  └── IAM Role: CrossAccountRole
        ↓ Assume Role                     ├── Trust Policy: 允許帳號 A 扮演
        └──────────────────────────────→  └── Policy: 允許讀取 S3
```

```bash
# 帳號 B 建立 Role，Trust Policy 允許帳號 A
# 帳號 A 的 Lambda 扮演帳號 B 的 Role 來存取帳號 B 的 S3
aws sts assume-role \
  --role-arn "arn:aws:iam::ACCOUNT_B_ID:role/CrossAccountRole" \
  --role-session-name "cross-account-session"
```

---

## 常用 CLI 指令

```bash
# 查看當前身份
aws sts get-caller-identity
# 輸出：帳號 ID、User ARN、User ID

# 列出所有 User
aws iam list-users

# 列出所有 Role
aws iam list-roles

# 查看 User 附加的 Policy
aws iam list-attached-user-policies --user-name alice

# 查看 Role 附加的 Policy
aws iam list-attached-role-policies --role-name MyRole

# 建立 Policy
aws iam create-policy \
  --policy-name MyS3ReadPolicy \
  --policy-document file://policy.json

# 附加 Policy 到 Role
aws iam attach-role-policy \
  --role-name MyRole \
  --policy-arn arn:aws:iam::123456789012:policy/MyS3ReadPolicy

# 模擬 Policy（測試權限，不實際執行）
aws iam simulate-principal-policy \
  --policy-source-arn arn:aws:iam::123456789012:role/MyRole \
  --action-names s3:GetObject \
  --resource-arns arn:aws:s3:::my-bucket/test.txt
```

---

## 最小權限原則（Least Privilege）

IAM 的核心設計原則：**只給需要的最小權限，不多給。**

```
❌ 不好的做法：
  給 Lambda 附加 AdministratorAccess
  → Lambda 可以刪除任何資源、建立 IAM User、修改帳單...

✅ 好的做法：
  只給 Lambda 需要的操作：
  → dynamodb:GetItem、dynamodb:PutItem（只有這張 Table）
  → s3:GetObject（只有這個 Bucket）
  → logs:PutLogEvents（只有這個 Log Group）
```

**實作最小權限的步驟：**
1. 先給 `*` 讓功能跑起來
2. 用 CloudTrail 或 IAM Access Analyzer 查看實際用到哪些 API
3. 把 Policy 縮小到只包含實際用到的操作和資源
4. 定期審查，移除不再需要的權限

---

## IAM Access Analyzer

AWS 提供的工具，幫你找出過度開放的權限：

- **外部存取分析**：找出哪些資源（S3、IAM Role 等）可以被外部帳號存取
- **未使用的存取**：找出 User 或 Role 有哪些權限從來沒用過
- **Policy 驗證**：在建立 Policy 前先驗證語法和邏輯

```bash
# 建立 Analyzer
aws accessanalyzer create-analyzer \
  --analyzer-name my-analyzer \
  --type ACCOUNT

# 列出發現的問題
aws accessanalyzer list-findings \
  --analyzer-name my-analyzer
```
