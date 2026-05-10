# AWS EC2 筆記

EC2（Elastic Compute Cloud）是 AWS 提供的虛擬機器服務，讓你可以在雲端租用計算資源，按需啟動、停止、調整規格。

---

## 核心概念

### Instance（實例）

EC2 Instance 就是一台虛擬機器，運行在 AWS 的實體伺服器上。你可以選擇：
- **作業系統**：Amazon Linux、Ubuntu、Windows Server 等
- **規格（Instance Type）**：CPU、記憶體、網路頻寬的組合
- **儲存**：EBS（持久化磁碟）或 Instance Store（臨時儲存）

### AMI（Amazon Machine Image）

AMI 是啟動 EC2 的**模板**，包含：
- 作業系統
- 預裝的軟體和設定
- 根磁碟的快照

> 類比：AMI 是虛擬機器的「安裝光碟」，每次啟動新 instance 都從這個模板複製出來。

你可以使用 AWS 官方 AMI、Marketplace 上的第三方 AMI，或自己建立自訂 AMI（把現有 instance 打包成 AMI，方便快速複製相同環境）。

---

## Instance Type 命名規則

```
m5.xlarge
│ │  └── 大小（nano, micro, small, medium, large, xlarge, 2xlarge...）
│ └──── 世代（數字越大越新）
└────── 系列（代表用途）
```

### 常見系列

| 系列 | 用途 | 適合場景 |
|------|------|----------|
| `t` | 通用，可突發（Burstable） | 開發環境、低流量網站、小型 API |
| `m` | 通用，平衡 CPU/記憶體 | 一般 Web Server、應用程式伺服器 |
| `c` | 運算優化（Compute Optimized） | 高 CPU 需求：影像處理、批次運算 |
| `r` | 記憶體優化（Memory Optimized） | 大型資料庫、記憶體快取（Redis） |
| `g` / `p` | GPU 加速 | 機器學習訓練、圖形渲染 |
| `i` | 儲存優化（Storage Optimized） | 高 IOPS 需求：NoSQL DB、資料倉儲 |

### T 系列的 CPU Credit 機制

`t3`、`t4g` 等 T 系列 instance 有**突發（Burst）**機制：

- 平時 CPU 使用率低時，累積 **CPU Credit**
- 需要高 CPU 時，消耗 Credit 來突發到 100%
- Credit 用完後，CPU 會被限制在基準效能（例如 t3.micro 是 10%）

適合流量不穩定的場景，但不適合持續高 CPU 的工作負載。

---

## 儲存類型

### EBS（Elastic Block Store）

EBS 是**持久化**的網路磁碟，instance 停止後資料不會消失。

| 類型 | 說明 | 適用場景 |
|------|------|----------|
| `gp3` | 通用 SSD（推薦） | 大多數工作負載，可獨立調整 IOPS |
| `gp2` | 通用 SSD（舊版） | 舊有環境，建議遷移到 gp3 |
| `io2` | 高效能 SSD | 需要極高 IOPS 的資料庫（如 Oracle） |
| `st1` | 吞吐量優化 HDD | 大量循序讀寫：Log、資料倉儲 |
| `sc1` | 冷儲存 HDD | 很少存取的資料，成本最低 |

**EBS 特性：**
- 只能掛載到**同一個 AZ** 的 instance
- 可以建立 Snapshot 備份到 S3
- 可以跨 AZ 複製 Snapshot 來遷移資料

### Instance Store

Instance Store 是**臨時**的本地磁碟，直接連接到實體主機：
- 速度極快（本地 NVMe SSD）
- Instance 停止或終止後，**資料全部消失**
- 適合暫存資料、快取、Shuffle 資料（如 Spark 運算）

---

## 網路相關

### Public IP vs Elastic IP

| 項目 | Public IP | Elastic IP（EIP） |
|------|-----------|-------------------|
| 分配方式 | 啟動時自動分配 | 手動申請，綁定到你的帳號 |
| 重啟後 | **會改變** | **不會改變** |
| 費用 | 免費 | 綁定到運行中的 instance 免費；閒置收費 |
| 適用場景 | 開發測試 | 需要固定 IP 的生產環境 |

> 如果你的 EC2 重啟後 IP 改變，DNS 設定就會失效。生產環境通常用 EIP 或搭配 Load Balancer + Route 53。

### ENI（Elastic Network Interface）

ENI 是虛擬網路卡，每個 EC2 至少有一個 ENI（Primary ENI）。

- 每個 ENI 有自己的 Private IP、Public IP（可選）、Security Group
- 可以把 ENI 從一台 instance 移到另一台（用於快速故障轉移）
- 一台 instance 可以掛多個 ENI（用於多網路介面場景）

### Placement Group（置放群組）

控制 instance 在實體硬體上的分佈方式：

| 類型 | 說明 | 適用場景 |
|------|------|----------|
| Cluster | 同一個 AZ 的同一個機架，低延遲 | HPC、需要極低網路延遲的叢集 |
| Spread | 分散到不同實體硬體，最多 7 個/AZ | 高可用性，避免單點故障 |
| Partition | 分成多個 partition，每個 partition 獨立機架 | Kafka、Cassandra 等分散式系統 |

---

## 生命週期與狀態

```
pending → running → stopping → stopped → terminated
                 ↘ shutting-down → terminated
```

| 狀態 | 說明 | 計費 |
|------|------|------|
| `pending` | 正在啟動中 | 不計費 |
| `running` | 運行中 | **計費** |
| `stopping` | 正在停止 | 不計費 |
| `stopped` | 已停止（EBS 資料保留） | 不計費（但 EBS 仍計費） |
| `terminated` | 已終止，instance 永久刪除 | 不計費 |

> **Stop vs Terminate 的差別**：Stop 是關機，資料保留，可以再啟動；Terminate 是刪除，預設 EBS 也會一起刪除（除非設定 `DeleteOnTermination: false`）。

---

## 購買方式

| 類型 | 說明 | 折扣 | 適用場景 |
|------|------|------|----------|
| On-Demand | 按小時/秒計費，隨時啟停 | 無 | 開發測試、不可預測的流量 |
| Reserved Instance | 預付 1 或 3 年 | 最高 72% | 穩定的生產環境 |
| Savings Plans | 承諾每小時消費金額，更彈性 | 最高 66% | 跨 instance type 的彈性節省 |
| Spot Instance | 競標閒置資源，AWS 可隨時收回 | 最高 90% | 批次運算、容錯性高的工作負載 |
| Dedicated Host | 獨占實體主機 | 無（但可用 RI） | 授權合規（如 Windows Server 授權） |

### Spot Instance 注意事項

Spot Instance 被 AWS 收回前會有 **2 分鐘警告**（Interruption Notice），你的應用需要能處理這個情況：
- 儲存 checkpoint，讓任務可以從中斷點繼續
- 搭配 Auto Scaling Group 使用，被收回後自動補充

---

## User Data（啟動腳本）

啟動 EC2 時可以傳入 User Data，instance 第一次啟動時會自動執行（以 root 身份）：

```bash
#!/bin/bash
# 安裝並啟動 Nginx
yum update -y
yum install -y nginx
systemctl start nginx
systemctl enable nginx

# 安裝 Python 和 pip
yum install -y python3 python3-pip
```

用途：
- 自動安裝軟體
- 設定環境變數
- 拉取程式碼並啟動服務
- 搭配 AMI 使用，讓 AMI 保持乾淨，動態設定在 User Data 裡

---

## IAM Role for EC2

EC2 需要存取其他 AWS 服務（如 S3、DynamoDB）時，**不要把 Access Key 放在 instance 上**，而是掛上 IAM Role：

```
EC2 Instance
  └── IAM Instance Profile
        └── IAM Role
              └── Policy（允許存取 S3、CloudWatch 等）
```

EC2 上的程式可以透過 **Instance Metadata Service（IMDS）** 自動取得臨時憑證：

```bash
# 取得臨時憑證（IMDSv2）
TOKEN=$(curl -X PUT "http://169.254.169.254/latest/api/token" \
  -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")

curl -H "X-aws-ec2-metadata-token: $TOKEN" \
  http://169.254.169.254/latest/meta-data/iam/security-credentials/<role-name>
```

AWS SDK（boto3、AWS CLI）會自動處理這個流程，你不需要手動呼叫 IMDS。

---

## 常見架構情境

### 情境一：單台 EC2 跑 Web API

```
Internet → Internet Gateway → Public Subnet → EC2 (FastAPI)
                                                  └── EBS (gp3, 20GB)
                                                  └── Security Group
                                                        ├── Inbound: TCP/443 from 0.0.0.0/0
                                                        └── Inbound: TCP/22 from 你的 IP
```

### 情境二：高可用架構（Multi-AZ）

```
Internet
  └── Application Load Balancer（跨 AZ）
        ├── AZ-a: EC2 (Private Subnet)
        └── AZ-b: EC2 (Private Subnet)
              └── RDS (Multi-AZ, Private Subnet)
```

- EC2 放在 Private Subnet，不直接對外
- ALB 放在 Public Subnet，負責接收流量並分發
- RDS 開 Multi-AZ，主備自動切換

### 情境三：Auto Scaling Group

```
ALB → Target Group → Auto Scaling Group
                          ├── Min: 2 instances
                          ├── Max: 10 instances
                          └── Scaling Policy: CPU > 70% 就加機器
```

Auto Scaling Group 會根據設定的指標（CPU、記憶體、自訂 CloudWatch Metric）自動增減 instance 數量，搭配 ALB 實現彈性擴展。

---

## 監控與除錯

### CloudWatch Metrics（預設）

| Metric | 說明 |
|--------|------|
| `CPUUtilization` | CPU 使用率（%） |
| `NetworkIn` / `NetworkOut` | 網路流量（bytes） |
| `DiskReadOps` / `DiskWriteOps` | EBS 磁碟 I/O 次數 |
| `StatusCheckFailed` | Instance 或系統狀態檢查失敗 |

> 注意：**記憶體使用率**不在預設 Metrics 裡，需要安裝 **CloudWatch Agent** 才能收集。

### CloudWatch Agent 安裝（Amazon Linux 2）

```bash
# 安裝 CloudWatch Agent
sudo yum install -y amazon-cloudwatch-agent

# 使用設定精靈
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-config-wizard

# 啟動
sudo systemctl start amazon-cloudwatch-agent
sudo systemctl enable amazon-cloudwatch-agent
```

### EC2 Instance Connect vs SSH

| 方式 | 說明 | 需要 |
|------|------|------|
| SSH | 傳統方式，用 key pair | Public IP + Port 22 開放 + .pem 檔 |
| EC2 Instance Connect | AWS Console 直接連線 | Port 22 開放（來源是 AWS IP 範圍） |
| Session Manager | 透過 SSM，不需要 Port 22 | IAM Role + SSM Agent（Amazon Linux 預裝） |

**Session Manager 是最安全的方式**：完全不需要開 Port 22，所有連線記錄都在 CloudTrail 和 Session Manager 歷史記錄中。
