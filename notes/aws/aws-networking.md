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

TCP（Transmission Control Protocol）是一種網路傳輸協定，負責確保資料完整、有序地送達。

特性：
- 建立連線前先握手（三次握手）
- 資料送達後對方要回確認，掉包會重傳
- 適合需要可靠傳輸的場景：網頁、API、資料庫連線

對比 UDP：不確認送達、速度快，適合影音串流、遊戲。

### Port 是什麼

Port（連接埠）是一個數字，用來區分同一台機器上不同的服務。

> 類比：IP 是大樓地址，Port 是房間號碼。

瀏覽器輸入 `http://example.com` 時，預設就是連到那台機器的 **Port 80**。

### 常見 Port 對照表

| Port | 協定 | 用途 |
|------|------|------|
| 22 | TCP | SSH（遠端登入 EC2） |
| 80 | TCP | HTTP（網頁，未加密） |
| 443 | TCP | HTTPS（網頁，加密） |
| 3306 | TCP | MySQL |
| 5432 | TCP | PostgreSQL |

### 在 Security Group 的意義

設定 `TCP / 80` 的 Inbound rule = **允許外部用 HTTP 連進這台 EC2**。
