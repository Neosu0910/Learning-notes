# 計算機網路基礎

## 1. 為什麼需要網路協定？

兩台電腦要溝通，需要事先約定好「說話的規則」，否則一台說中文、一台說英文，根本聽不懂。這些規則就叫**協定（Protocol）**。

網路協定是分層的，每一層只負責自己的事，不管其他層怎麼實作。

---

## 2. TCP/IP 四層模型

實際工程上最常用的是 TCP/IP 四層模型：

```
┌─────────────────────────────────────────┐
│  應用層（Application）                   │  HTTP、HTTPS、DNS、FTP、SSH
├─────────────────────────────────────────┤
│  傳輸層（Transport）                     │  TCP、UDP
├─────────────────────────────────────────┤
│  網路層（Internet）                      │  IP（IPv4、IPv6）
├─────────────────────────────────────────┤
│  網路存取層（Network Access）            │  乙太網路、Wi-Fi、MAC address
└─────────────────────────────────────────┘
```

你傳一個 HTTP 請求，實際上是這樣包裝的：

```
HTTP 資料
  → 被 TCP 包起來（加上 port 資訊）
    → 被 IP 包起來（加上來源/目的 IP）
      → 被乙太網路包起來（加上 MAC address）
        → 變成電訊號送出去
```

對方收到後，反向一層一層拆開，最後拿到 HTTP 資料。

---

## 3. IP 位址（IPv4）

IP 位址是網路上每台機器的「地址」，用來找到對方在哪裡。

### IPv4 格式

```
192.168.1.100
```

四個數字，每個 0～255，用點分隔。總共 32 bits，約 43 億個位址。

### 公有 IP vs 私有 IP

| 類型 | 範圍 | 說明 |
|------|------|------|
| 私有 IP | `10.0.0.0/8`、`172.16.0.0/12`、`192.168.0.0/16` | 只在內網用，不能直接上網 |
| 公有 IP | 其他 | 全球唯一，可以在網際網路上被找到 |

你家路由器有一個公有 IP（ISP 給的），你的電腦、手機有私有 IP（路由器分配的）。

### CIDR 表示法

`192.168.1.0/24` 表示一個網段：
- `/24` 代表前 24 bits 是網路部分，後 8 bits 是主機部分
- 這個網段可以有 256 個位址（192.168.1.0 ～ 192.168.1.255）
- 實際可用 254 個（第一個是網路位址，最後一個是廣播位址）

```
/8  → 16,777,216 個位址（A 類）
/16 → 65,536 個位址（B 類）
/24 → 256 個位址（C 類，最常見）
/32 → 1 個位址（單一主機）
```

### IPv6

IPv4 的 43 億個位址已經不夠用，IPv6 用 128 bits，位址數量幾乎無限。

```
IPv4：192.168.1.1
IPv6：2001:0db8:85a3:0000:0000:8a2e:0370:7334
```

---

## 4. Port（埠號）

IP 找到機器，Port 找到機器上的哪個服務。

類比：IP 是大樓地址，Port 是幾號房間。

```
http://192.168.1.100:8080/api/users
                     ^^^^
                     Port 8080
```

### 常見 Port

| Port | 服務 | 說明 |
|------|------|------|
| 22 | SSH | 遠端連線到伺服器 |
| 80 | HTTP | 網頁（未加密）|
| 443 | HTTPS | 網頁（加密）|
| 3306 | MySQL | MySQL 資料庫 |
| 5432 | PostgreSQL | PostgreSQL 資料庫 |
| 6379 | Redis | Redis 快取 |
| 8080 | 自訂 | 開發時常用的替代 HTTP port |

Port 範圍：
- `0～1023`：Well-known ports，需要 root 權限才能使用
- `1024～49151`：Registered ports，常見應用程式使用
- `49152～65535`：Dynamic ports，系統動態分配給客戶端連線用

---

## 5. TCP vs UDP

兩種傳輸層協定，差別在於「可靠性」和「速度」的取捨。

### TCP（Transmission Control Protocol）

**可靠、有序、慢一點**

- 建立連線前要先「三次握手」
- 每個封包都要確認收到，沒收到會重傳
- 保證資料順序正確
- 適合：HTTP、資料庫連線、檔案傳輸

**三次握手：**
```
客戶端 → SYN（我要連線）→ 伺服器
客戶端 ← SYN-ACK（好，我準備好了）← 伺服器
客戶端 → ACK（收到，開始傳）→ 伺服器
（連線建立，開始傳資料）
```

### UDP（User Datagram Protocol）

**不可靠、無序、快**

- 直接送出去，不管對方有沒有收到
- 沒有重傳機制
- 適合：影音串流、線上遊戲、DNS 查詢

| | TCP | UDP |
|--|-----|-----|
| 可靠性 | 保證送達 | 不保證 |
| 順序 | 保證順序 | 不保證 |
| 速度 | 較慢（有握手、確認）| 較快 |
| 適合 | HTTP、資料庫、SSH | 影音、遊戲、DNS |

---

## 6. HTTP vs HTTPS

### HTTP

明文傳輸，中間人可以看到所有內容。

```
你的電腦 → 路由器 → ISP → 目標伺服器
          （任何中間節點都能看到你傳的內容）
```

### HTTPS

HTTP + TLS（加密層），傳輸內容加密，中間人看不懂。

```
你的電腦 → [加密] → 路由器 → ISP → [解密] → 目標伺服器
          （中間節點只看到亂碼）
```

**TLS 握手流程（簡化版）：**
```
1. 客戶端：我支援這些加密方式
2. 伺服器：用這個，這是我的憑證（SSL Certificate）
3. 客戶端：驗證憑證合法（由 CA 簽發）
4. 雙方：協商出一個對稱加密金鑰
5. 之後的通訊都用這個金鑰加密
```

**SSL Certificate（SSL 憑證）：**
- 由 CA（Certificate Authority，憑證機構）簽發，證明「這個網站真的是它說的那個網站」
- 瀏覽器看到 🔒 就是因為憑證驗證通過
- Let's Encrypt 提供免費憑證

---

## 7. DNS（Domain Name System）

DNS 是網路的「電話簿」，把人類看得懂的網域名稱轉換成 IP 位址。

```
你輸入：google.com
DNS 查詢：google.com → 142.250.x.x
瀏覽器連線到：142.250.x.x
```

### DNS 查詢流程

```
瀏覽器
  → 先查本機 cache（/etc/hosts 或瀏覽器 cache）
  → 沒有 → 問 Local DNS（通常是路由器或 ISP）
  → 沒有 → 問 Root DNS Server（.）
  → 問 TLD DNS Server（.com）
  → 問 Authoritative DNS Server（google.com 的 DNS）
  → 得到 IP，回傳給瀏覽器
```

### 常見 DNS 記錄類型

| 類型 | 說明 | 例子 |
|------|------|------|
| A | 網域 → IPv4 | `google.com → 142.250.x.x` |
| AAAA | 網域 → IPv6 | `google.com → 2607:f8b0:...` |
| CNAME | 網域 → 另一個網域（別名）| `www.example.com → example.com` |
| MX | 郵件伺服器 | `example.com → mail.example.com` |
| TXT | 文字記錄（驗證用）| SPF、DKIM 等 |

---

## 8. NAT（Network Address Translation）

NAT 讓多台私有 IP 的機器共用一個公有 IP 上網。

```
家裡的設備（私有 IP）：
  電腦：192.168.1.2  ─┐
  手機：192.168.1.3  ─┤→ 路由器（NAT）→ 公有 IP: 1.2.3.4 → 網際網路
  平板：192.168.1.4  ─┘
```

路由器維護一張 NAT 表，記錄「哪個私有 IP + Port 對應到哪個外部連線」，這樣回來的封包才知道要送給誰。

**在 AWS 的對應：**
- NAT Gateway：讓 private subnet 的 EC2 可以對外連線，但外部無法主動連進來

---

## 9. 防火牆與 Security Group

防火牆根據規則決定「哪些封包可以通過」。

規則通常基於：
- 來源 IP
- 目的 IP
- Port
- 協定（TCP/UDP）
- 方向（inbound/outbound）

**在 AWS 的對應：**

Security Group 就是 EC2 的防火牆：
```
Inbound rules（進來的流量）：
  允許 TCP port 443 from 0.0.0.0/0   ← 任何人都能連 HTTPS
  允許 TCP port 22 from 1.2.3.4/32   ← 只有這個 IP 能 SSH

Outbound rules（出去的流量）：
  允許所有流量 to 0.0.0.0/0          ← 可以連到任何地方
```

---

## 10. 常見網路工具指令

```bash
# 查詢 DNS，看網域對應到哪個 IP
nslookup google.com
dig google.com

# 測試能不能連到某個 IP（ICMP）
ping 8.8.8.8

# 追蹤封包走哪條路
traceroute google.com

# 查看本機網路介面和 IP
ifconfig        # macOS/Linux
ip addr show    # Linux

# 查看目前的網路連線和 port 使用狀況
netstat -an
ss -tlnp        # Linux，看哪些 port 在監聽

# 測試某個 port 是否開著
telnet google.com 443
nc -zv google.com 443

# 發送 HTTP 請求
curl https://api.example.com/users
curl -X POST https://api.example.com/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Neo"}'
```

---

## 11. 一個 HTTP 請求的完整旅程

你在瀏覽器輸入 `https://api.example.com/users`，背後發生了什麼：

```
1. DNS 查詢
   api.example.com → 54.230.12.45

2. TCP 三次握手
   你的電腦 ←→ 54.230.12.45:443 建立連線

3. TLS 握手
   交換憑證、協商加密金鑰

4. HTTP 請求送出（加密）
   GET /users HTTP/1.1
   Host: api.example.com

5. 伺服器處理請求
   查資料庫、組裝回應

6. HTTP 回應（加密）
   HTTP/1.1 200 OK
   [{"id": 1, "name": "Neo"}]

7. TCP 四次揮手
   關閉連線
```

---

## 重點整理

| 概念 | 一句話說明 |
|------|-----------|
| IP | 網路上機器的地址 |
| Port | 機器上哪個服務的門號 |
| TCP | 可靠傳輸，有握手確認 |
| UDP | 快速傳輸，不保證送達 |
| HTTP | 應用層的溝通協定，明文 |
| HTTPS | HTTP + TLS 加密 |
| DNS | 網域名稱轉 IP 的電話簿 |
| NAT | 多台私有 IP 共用一個公有 IP |
| 防火牆 | 根據規則過濾封包 |
