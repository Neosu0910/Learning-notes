# AWS Networking 筆記

## Public vs. Private Subnet 差異

| 項目 | Public Subnet | Private Subnet |
|------|--------------|----------------|
| Route Table | 有一條 `0.0.0.0/0 → Internet Gateway` | 沒有直接通往 IGW 的路由 |
| 外網可主動連入 | 可以（透過 Public IP / EIP） | 不行 |
| 典型用途 | Load Balancer、Bastion Host、NAT Gateway | App Server、DB、內部服務 |

**核心差異就是 Route Table**：Public Subnet 的路由表有指向 Internet Gateway 的預設路由，Private Subnet 沒有。

---

## 情境題

### 情境一：同個 Private Subnet 的兩台 EC2，僅限彼此互通

用 **Security Group** 來做，這是最精準的方式：

1. 建立一個 SG，例如叫 `sg-internal-pair`
2. 兩台 EC2 都掛上這個 SG
3. Inbound rule 設定：
   - Source：`sg-internal-pair`（引用自己這個 SG）
   - Port：All traffic 或你需要的 port

這樣只有同樣掛著這個 SG 的資源才能互相連線，其他 EC2 即使在同個 Subnet 也進不來。

> Security Group 支援「以另一個 SG 作為 Source」，這是 AWS 網路控制的精髓之一。

---

### 情境二：Private EC2 能出去下載更新，但禁止外網主動連入

用 **NAT Gateway**：

```
Private EC2 → Route Table → NAT Gateway（在 Public Subnet）→ Internet Gateway → 外網
```

設定步驟：
1. 在 Public Subnet 建立 NAT Gateway（需要 EIP）
2. Private Subnet 的 Route Table 加一條：`0.0.0.0/0 → NAT Gateway`
3. Private EC2 的 Security Group 只開 Outbound，不開 Inbound（或只開必要的 Inbound）

NAT Gateway 的特性是**只允許由內往外發起的連線**，外網無法主動穿透進來，因為 NAT 不會保留 inbound 的 mapping。

---

### 情境三：Private EC2 不經過 Internet，安全地傳 Log 到 CloudWatch

用 **VPC Endpoint（Interface Endpoint）**：

```
Private EC2 → VPC Endpoint for CloudWatch Logs → AWS 內部網路 → CloudWatch Logs
```

具體做法：
1. 在 VPC 建立 Interface Endpoint，服務選 `com.amazonaws.<region>.logs`
2. Endpoint 會在你指定的 Subnet 建立一個 ENI（Elastic Network Interface）
3. EC2 上的 CloudWatch Agent 設定好後，流量會走 AWS PrivateLink，完全不出 VPC

優點：
- 流量不經過 Internet，不需要 NAT Gateway
- 更安全，符合合規要求（如金融、醫療）
- 可以搭配 Endpoint Policy 進一步限制哪些資源可以用這個 Endpoint

---

## TCP 與 Port

在 AWS Console 設定 Security Group Inbound rule 時，需要指定 Protocol 和 Port。

### TCP 是什麼

TCP（Transmission Control Protocol）是一種**連線導向**的網路傳輸協定，負責確保資料完整、有序地送達目的地。

#### 核心特性

| 特性 | 說明 |
|------|------|
| 可靠傳輸 | 每個封包都有序號，接收方確認後才算送達 |
| 流量控制 | 根據接收方的緩衝區大小調整發送速率，避免淹沒對方 |
| 壅塞控制 | 偵測網路壅塞時自動降速，避免封包大量遺失 |
| 有序傳遞 | 封包可能亂序抵達，TCP 會重新排列後再交給應用層 |

#### 三次握手（Three-Way Handshake）

建立 TCP 連線必須先完成三次握手，確認雙方都能收發：

```
Client                          Server
  |                               |
  |  ① SYN (seq=x)               |   Client 說：我想連線，我的序號是 x
  |-----------------------------> |
  |                               |
  |  ② SYN-ACK (seq=y, ack=x+1) |   Server 說：好，我的序號是 y，我收到你的 x 了
  | <-----------------------------|
  |                               |
  |  ③ ACK (ack=y+1)             |   Client 說：我也收到你的 y 了，連線建立！
  |-----------------------------> |
  |                               |
  |       [資料傳輸開始]           |
```

- **SYN**（Synchronize）：請求建立連線
- **ACK**（Acknowledge）：確認收到
- 三次握手後，雙方都確認了彼此的序號，可以開始傳資料

#### 四次揮手（Four-Way Handshake）

關閉連線需要四次，因為 TCP 是全雙工（雙向獨立）：

```
Client                          Server
  |                               |
  |  ① FIN                       |   Client 說：我這邊傳完了
  |-----------------------------> |
  |  ② ACK                       |   Server 說：好，我知道了
  | <-----------------------------|
  |  ③ FIN                       |   Server 說：我這邊也傳完了
  | <-----------------------------|
  |  ④ ACK                       |   Client 說：好，連線關閉
  |-----------------------------> |
```

#### TCP vs UDP 比較

| 項目 | TCP | UDP |
|------|-----|-----|
| 連線方式 | 需要握手建立連線 | 無連線，直接發送 |
| 可靠性 | 保證送達、有序 | 不保證，可能遺失或亂序 |
| 速度 | 較慢（有確認機制） | 較快（無額外開銷） |
| 適用場景 | HTTP/S、SSH、資料庫、API | 影音串流、DNS、線上遊戲、VoIP |
| Header 大小 | 20-60 bytes | 8 bytes |

---

### Port 是什麼

Port（連接埠）是一個 **0–65535** 的數字，作業系統用它來區分同一台機器上不同的服務或程序。

> 類比：IP 是大樓地址，Port 是房間號碼。同一棟大樓（同一個 IP）可以有很多房間（很多服務）同時運作。

#### Port 的分類

| 範圍 | 名稱 | 說明 |
|------|------|------|
| 0 – 1023 | Well-Known Ports | 標準服務保留，需要 root 權限才能監聽 |
| 1024 – 49151 | Registered Ports | 常見應用程式使用，如 MySQL (3306) |
| 49152 – 65535 | Dynamic / Ephemeral Ports | 客戶端發起連線時，OS 隨機分配的來源 port |

#### Ephemeral Port（臨時埠）的重要性

當你的瀏覽器連到 `http://example.com:80` 時，實際上：

```
你的電腦 (IP: 192.168.1.5, Port: 54321)  →  Server (IP: 93.184.216.34, Port: 80)
```

- Port 80 是 Server 的目的地 port（固定）
- Port 54321 是你電腦 OS 隨機分配的**來源 port**（臨時，用完就釋放）

**這在 AWS Security Group 設定上很重要**：如果你只開 Inbound 80，Server 回應時要能送回到你的臨時 port（49152–65535），所以 Outbound 要允許這個範圍，或直接開 All traffic。

#### 常見 Port 對照表

| Port | 協定 | 用途 |
|------|------|------|
| 22 | TCP | SSH（遠端登入 EC2） |
| 25 | TCP | SMTP（發送 Email） |
| 53 | TCP/UDP | DNS（域名解析） |
| 80 | TCP | HTTP（網頁，未加密） |
| 443 | TCP | HTTPS（網頁，TLS 加密） |
| 3306 | TCP | MySQL / Aurora MySQL |
| 5432 | TCP | PostgreSQL / Aurora PostgreSQL |
| 6379 | TCP | Redis（ElastiCache） |
| 8080 | TCP | 常見的 HTTP 替代 port（開發用） |
| 27017 | TCP | MongoDB |

---

### 在 Security Group 的意義

Security Group 是 AWS 的**虛擬防火牆**，運作在 instance 層級，規則是 stateful（有狀態）的。

#### Stateful 的含義

> 你只需要開 Inbound，對應的 Outbound 回應流量會**自動放行**，不需要另外設定。

```
外部請求 → [Inbound Rule: TCP/443 允許] → EC2
EC2 回應 → [自動允許，不需要 Outbound Rule] → 外部
```

這和 Network ACL（NACL）不同，NACL 是 stateless，進出都要明確設定。

#### 實際設定範例

**情境：一台跑 FastAPI 的 EC2，需要讓外部 HTTPS 連入，並能連到 RDS PostgreSQL**

Inbound Rules：
| Type | Protocol | Port | Source | 說明 |
|------|----------|------|--------|------|
| HTTPS | TCP | 443 | 0.0.0.0/0 | 允許所有人用 HTTPS 連入 |
| SSH | TCP | 22 | 你的 IP/32 | 只允許你自己 SSH 進來 |

Outbound Rules（通常預設 All traffic，不需改）：
| Type | Protocol | Port | Destination | 說明 |
|------|----------|------|-------------|------|
| PostgreSQL | TCP | 5432 | RDS SG | 連到 RDS 的 Security Group |

**RDS 的 Security Group Inbound Rules：**
| Type | Protocol | Port | Source | 說明 |
|------|----------|------|--------|------|
| PostgreSQL | TCP | 5432 | EC2 的 SG | 只允許 EC2 連入，不對外開放 |

#### Security Group vs NACL 比較

| 項目 | Security Group | Network ACL |
|------|---------------|-------------|
| 作用層級 | Instance（ENI）層級 | Subnet 層級 |
| 狀態 | Stateful（有狀態） | Stateless（無狀態） |
| 規則方向 | Inbound / Outbound 分開設 | Inbound / Outbound 都要設 |
| 規則評估 | 所有規則都評估，取聯集 | 按編號順序，第一個符合就停 |
| 預設行為 | 預設拒絕所有 Inbound | 預設允許所有（可自訂） |
| 適用場景 | 精細控制單一 instance | 子網路層級的粗粒度控制 |
