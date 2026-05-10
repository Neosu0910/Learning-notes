# 05 每日名詞解釋

## 0507

**traceroute**

一個網路診斷工具，用來追蹤封包從你的電腦到目標主機所經過的每一個路由節點（hop）。每個 hop 代表一台路由器，traceroute 會記錄封包到達每個節點的延遲時間（RTT），讓你看出封包走哪條路、哪段出現延遲或封包遺失。

**原理：**
traceroute 利用 IP 封包的 TTL（Time To Live）欄位。每次送出一個 TTL=1 的封包，第一台路由器收到後 TTL 歸零，回傳 ICMP "Time Exceeded" 訊息，traceroute 就記錄這台路由器的 IP 和延遲。接著送 TTL=2，以此類推，直到封包抵達目標主機。

**實作：**
```bash
# macOS / Linux
traceroute google.com

# Windows
tracert google.com

# 指定使用 TCP（穿透防火牆更有效）
traceroute -T -p 80 google.com
```

**輸出範例：**
```
 1  192.168.1.1 (192.168.1.1)   1.2 ms   # 你的家用路由器
 2  10.0.0.1 (10.0.0.1)         5.4 ms   # ISP 第一跳
 3  * * *                                 # 這台路由器不回應（防火牆擋掉）
 4  142.250.x.x                 12.1 ms  # Google 的節點
```

**使用情境：**
- 網站連不上時，用 traceroute 找出是哪一段斷掉
- 排查高延遲問題，看是哪個 hop 特別慢

---

**IP 跟 Endpoint 的關係**

IP（Internet Protocol Address）是網路層的位址，用來在網路上唯一識別一台機器的位置。Endpoint 是「服務的存取點」，是一個更高層的概念，通常包含 IP + Port，或是一個完整的 URL。

**關係說明：**
- IP 是「地址」，告訴你封包要送到哪台機器
- Port 是「門號」，告訴你要找這台機器上的哪個服務
- Endpoint = IP + Port，或是 URL，是你實際呼叫服務的完整位址

**例子：**
```
IP:       54.230.12.45
Port:     8080
Endpoint: http://54.230.12.45:8080/api/users

# 或是用 domain name
Endpoint: https://api.example.com/v1/orders
```

**在 AWS 的情境：**
- RDS 資料庫的 endpoint：`mydb.xxxxxx.ap-northeast-1.rds.amazonaws.com:5432`
- API Gateway 的 endpoint：`https://abc123.execute-api.ap-northeast-1.amazonaws.com/prod`

---

**ENI 跟上網的關聯性**

ENI（Elastic Network Interface）是 AWS 上的虛擬網路卡，可以掛在 EC2 instance 上。每個 ENI 有自己的私有 IP、MAC address，可選擇性地附加 public IP 或 Elastic IP。

**EC2 要能上網，需要滿足三個條件：**
1. ENI 有 public IP 或 Elastic IP
2. 所在的 subnet 的 route table 有一條 `0.0.0.0/0 → Internet Gateway` 的路由
3. Security Group 允許對外流量

**架構圖概念：**
```
EC2 Instance
  └── ENI (有 public IP: 54.x.x.x)
        └── Subnet (route table: 0.0.0.0/0 → IGW)
              └── Internet Gateway
                    └── Internet
```

**實作：在 AWS Console 建立 ENI 並附加到 EC2**
```bash
# 用 AWS CLI 建立 ENI
aws ec2 create-network-interface \
  --subnet-id subnet-xxxxxxxx \
  --description "My ENI"

# 附加到 EC2
aws ec2 attach-network-interface \
  --network-interface-id eni-xxxxxxxx \
  --instance-id i-xxxxxxxx \
  --device-index 1
```

**ENI 的進階用途：**
- 一台 EC2 掛多個 ENI，每個 ENI 在不同 subnet，實現網路隔離
- ENI 可以從一台 EC2 移到另一台，IP 不變（適合 failover 場景）

---

**Interface Endpoints 跟 Gateway Endpoints 的差別**

兩者都是 AWS VPC Endpoint，讓 VPC 內的資源不用走公網就能存取 AWS 服務，提升安全性並降低流量費用。

| 比較項目 | Gateway Endpoint | Interface Endpoint |
|---------|-----------------|-------------------|
| 支援服務 | 只有 S3、DynamoDB | 大多數 AWS 服務 |
| 實作方式 | 修改 route table | 在 subnet 建立 ENI |
| 費用 | 免費 | 有費用（按小時 + 流量）|
| DNS | 不改變 | 可用 private DNS |
| 跨 VPC | 不支援 | 支援（透過 PrivateLink）|

**Gateway Endpoint 實作：**
```bash
# 建立 S3 的 Gateway Endpoint
aws ec2 create-vpc-endpoint \
  --vpc-id vpc-xxxxxxxx \
  --service-name com.amazonaws.ap-northeast-1.s3 \
  --route-table-ids rtb-xxxxxxxx
# 這會在 route table 自動加一條指向 S3 的路由
```

**Interface Endpoint 實作：**
```bash
# 建立 Secrets Manager 的 Interface Endpoint
aws ec2 create-vpc-endpoint \
  --vpc-id vpc-xxxxxxxx \
  --vpc-endpoint-type Interface \
  --service-name com.amazonaws.ap-northeast-1.secretsmanager \
  --subnet-ids subnet-xxxxxxxx \
  --security-group-ids sg-xxxxxxxx \
  --private-dns-enabled
# 建立後，VPC 內的資源呼叫 secretsmanager API 會自動走內網
```

---

**Interface Endpoint 一定要放在 private subnet 嗎？**

技術上不強制，但最佳實踐是放在 private subnet。

**原因：**
Interface Endpoint 的核心目的是讓 **private subnet 裡的資源**（例如沒有 public IP 的 EC2、Lambda in VPC）能夠存取 AWS 服務，而不需要走 NAT Gateway 或公網。如果放在 public subnet，這些 private 資源還是需要跨 subnet 才能用，而且 public subnet 的資源本來就能直接走公網存取 AWS 服務，放 Interface Endpoint 在那裡意義不大。

**架構建議：**
```
VPC
├── Public Subnet
│   └── NAT Gateway、Load Balancer
└── Private Subnet
    ├── EC2 / Lambda（沒有 public IP）
    └── Interface Endpoint ENI  ← 放這裡，讓 private 資源直接用
```

---

**I/O Bound vs CPU Bound**

描述程式效能瓶頸在哪裡的兩種分類。

**I/O Bound（輸入輸出瓶頸）：**
程式大部分時間在等待 I/O 操作完成，CPU 其實很閒。常見情境：
- 讀寫檔案
- 資料庫查詢
- 呼叫外部 API
- 網路傳輸

**CPU Bound（運算瓶頸）：**
程式大部分時間在做運算，CPU 一直滿載。常見情境：
- 影像/影片處理
- 機器學習訓練
- 加密/解密
- 大量數學運算

**為什麼這個區別重要？**
選擇優化策略時完全不同：

| | I/O Bound | CPU Bound |
|--|-----------|-----------|
| 優化方式 | async/await、多執行緒 | 多進程、分散式運算 |
| Python 工具 | `asyncio`、`threading` | `multiprocessing`、`concurrent.futures` |
| 原因 | 等待期間可切換去做別的事 | 需要真正的平行運算能力 |

**Python 範例：**
```python
import asyncio
import aiohttp

# I/O Bound → 用 async 同時發多個 API 請求
async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()

async def main():
    urls = ["https://api1.com", "https://api2.com", "https://api3.com"]
    async with aiohttp.ClientSession() as session:
        # 三個請求同時發出，不用等第一個完成才發第二個
        results = await asyncio.gather(*[fetch(session, url) for url in urls])
```

```python
from multiprocessing import Pool

# CPU Bound → 用多進程真正平行運算
def heavy_compute(n):
    return sum(i * i for i in range(n))

with Pool(processes=4) as pool:
    results = pool.map(heavy_compute, [10**7, 10**7, 10**7, 10**7])
```

---

**async / await**

非同步程式設計的語法糖，讓你用接近同步的寫法來處理非同步操作，避免 callback hell。

**核心概念：**
- `async def` 宣告一個 coroutine 函式，呼叫它不會立刻執行，而是回傳一個 coroutine 物件
- `await` 暫停當前 coroutine，把控制權交還給 event loop，等操作完成後再繼續
- Event loop 負責調度所有 coroutine，在某個 coroutine 等待時去執行其他的

**Python 完整範例：**
```python
import asyncio

async def boil_water():
    print("開始燒水")
    await asyncio.sleep(3)  # 模擬等待 3 秒（I/O 等待）
    print("水燒好了")
    return "熱水"

async def prepare_tea():
    print("準備茶葉")
    await asyncio.sleep(1)
    print("茶葉準備好了")
    return "茶葉"

async def make_tea():
    # 同時進行燒水和準備茶葉，不用等燒水完才準備茶葉
    water, tea = await asyncio.gather(boil_water(), prepare_tea())
    print(f"泡茶：{water} + {tea}")

asyncio.run(make_tea())
# 總共只需要 3 秒，而不是 3+1=4 秒
```

**FastAPI 中的應用：**
```python
from fastapi import FastAPI
import httpx

app = FastAPI()

@app.get("/data")
async def get_data():
    async with httpx.AsyncClient() as client:
        # 不會阻塞其他請求
        response = await client.get("https://external-api.com/data")
    return response.json()
```

**與同步的對比：**
```python
# 同步版本：總共需要 6 秒
import time
def sync_version():
    time.sleep(3)  # 等燒水
    time.sleep(3)  # 等另一件事
    # 共 6 秒

# 非同步版本：總共只需要 3 秒
async def async_version():
    await asyncio.gather(
        asyncio.sleep(3),
        asyncio.sleep(3)
    )
    # 共 3 秒（同時進行）
```

---

**萬物都是檔案（Everything is a file）**

Unix/Linux 的核心設計哲學。在 Linux 裡，幾乎所有東西都被抽象成「檔案」，用統一的介面（`open/read/write/close`）來操作，不管對象是普通文字檔、硬體裝置、還是網路連線。

**哪些東西是「檔案」：**
| 類型 | 路徑範例 | 說明 |
|------|---------|------|
| 普通檔案 | `/home/user/file.txt` | 一般文字或二進位檔案 |
| 硬體裝置 | `/dev/sda` | 硬碟 |
| 終端機 | `/dev/tty` | 你的終端機輸入輸出 |
| 隨機數 | `/dev/random` | 讀取會得到隨機位元組 |
| 黑洞 | `/dev/null` | 寫入的東西全部丟棄 |
| 進程資訊 | `/proc/1234/status` | PID 1234 的進程狀態 |
| 網路 socket | fd（file descriptor）| 網路連線也是一個 fd |

**實作範例：**
```bash
# 把東西丟進黑洞（不想看到輸出）
command > /dev/null 2>&1

# 讀取 CPU 資訊（其實是讀一個「檔案」）
cat /proc/cpuinfo

# 讀取記憶體使用（也是讀檔案）
cat /proc/meminfo

# 直接對硬碟裝置讀取（dd 讀 /dev/sda）
sudo dd if=/dev/sda of=backup.img bs=4M
```

```python
# Python 中，網路 socket 也可以像檔案一樣操作
import socket

s = socket.socket()
s.connect(("google.com", 80))
s.send(b"GET / HTTP/1.0\r\n\r\n")
response = s.recv(1024)  # 跟讀檔案一樣用 read/recv
s.close()                # 跟關檔案一樣用 close
```

**這個設計的好處：**
- 統一介面，學一套就能操作所有東西
- 可以用 shell 的 pipe（`|`）把任何程式的輸出接到另一個程式
- 權限管理統一，用檔案權限（rwx）控制所有資源的存取
