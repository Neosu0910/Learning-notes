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

---

## 0508

**浮點運算子（Floating Point）**

電腦用來表示「有小數點的數字」的方式。因為電腦只懂 0 和 1，無法精確儲存所有小數，所以用一種近似的格式（IEEE 754 標準）來表示，這就是「浮點數」。

**原理：**
浮點數由三個部分組成：
- **符號位**：正數或負數
- **指數**：決定小數點的位置
- **尾數（mantissa）**：實際的數字內容

就像科學記號：`3.14 × 10²` = 314，電腦也是用類似的方式儲存。

**為什麼會有精度問題：**
某些小數在二進位裡是無限循環的，就像 1/3 在十進位是 0.333...，電腦只能截斷，所以會有誤差。

**實作範例：**
```python
# 浮點數精度問題
print(0.1 + 0.2)          # 0.30000000000000004（不是 0.3！）
print(0.1 + 0.2 == 0.3)   # False

# 正確的比較方式
import math
print(math.isclose(0.1 + 0.2, 0.3))  # True

# 需要精確小數時（例如金融計算），用 Decimal
from decimal import Decimal
print(Decimal("0.1") + Decimal("0.2"))  # 0.3（精確）
```

**常見的浮點運算子：**
```python
a = 3.14
b = 2.0

print(a + b)   # 加法：5.140000000000001
print(a - b)   # 減法：1.14
print(a * b)   # 乘法：6.28
print(a / b)   # 除法：1.57
print(a // b)  # 整除：1.0（結果還是 float）
print(a % b)   # 取餘數：1.14
print(a ** b)  # 次方：9.8596
```

**實際情境：**
- 金融系統絕對不能用 float，要用 `Decimal`
- 科學計算可以接受小誤差，用 float 沒問題
- 比較兩個浮點數時，用 `math.isclose()` 而不是 `==`

---

**Spark（Apache Spark）**

一個開源的大數據分散式運算框架，用來處理超大量資料（GB、TB 甚至 PB 等級）。它把資料分散到多台機器上同時處理，速度比傳統的 Hadoop MapReduce 快很多，因為它盡量把資料放在記憶體裡運算，而不是每次都寫到硬碟。

**解決什麼問題：**
當資料量大到一台機器處理不完，或處理速度太慢時，Spark 把工作切成很多小塊，分給一群機器（cluster）同時跑，最後再把結果合併。

**核心概念：**
- **RDD（Resilient Distributed Dataset）**：Spark 的基本資料結構，一個分散在多台機器上的資料集合
- **DataFrame**：類似 pandas DataFrame，但可以分散式處理，是現在最常用的方式
- **Transformation vs Action**：
  - Transformation（如 `filter`、`map`）：懶執行，只是描述要做什麼，不會立刻跑
  - Action（如 `collect`、`count`）：真正觸發執行

**實作範例（PySpark）：**
```python
from pyspark.sql import SparkSession

# 建立 Spark session
spark = SparkSession.builder \
    .appName("MyApp") \
    .getOrCreate()

# 讀取資料（可以是 CSV、Parquet、S3 上的檔案等）
df = spark.read.csv("s3://my-bucket/data.csv", header=True, inferSchema=True)

# 類似 SQL 的操作
df.filter(df["age"] > 25) \
  .groupBy("department") \
  .count() \
  .show()

# 也可以直接寫 SQL
df.createOrReplaceTempView("employees")
spark.sql("SELECT department, COUNT(*) FROM employees WHERE age > 25 GROUP BY department").show()
```

**在 AWS 上的對應服務：**
- **AWS EMR（Elastic MapReduce）**：在 AWS 上跑 Spark cluster 的託管服務
- **AWS Glue**：serverless 的 Spark 環境，不用管 cluster，直接寫 PySpark 腳本

**與 pandas 的差別：**
| | pandas | Spark |
|--|--------|-------|
| 資料量 | 單機記憶體內（幾 GB） | 分散式（TB、PB）|
| 執行方式 | 立刻執行 | 懶執行（lazy evaluation）|
| 學習曲線 | 簡單 | 較複雜 |
| 適合場景 | 資料分析、小資料 | 大數據處理、ETL |

---

**CloudWatch Log Streams**

AWS CloudWatch 是 AWS 的監控與日誌服務。Log Streams 是其中的日誌組織單位之一。

**三層結構：**
```
CloudWatch Logs
└── Log Group（日誌群組）
    └── Log Stream（日誌串流）  ← 你聽到的這個
        └── Log Events（一筆一筆的日誌）
```

- **Log Group**：一個服務或應用的所有日誌的集合，例如 `/aws/lambda/my-function`
- **Log Stream**：Log Group 裡面，來自同一個來源的日誌序列。例如每次 Lambda 啟動一個新的 instance，就會產生一個新的 Log Stream
- **Log Event**：每一筆實際的日誌訊息，有 timestamp 和內容

**為什麼要有 Log Stream：**
當你的服務有多個 instance 同時跑（例如 Lambda 同時被呼叫 100 次），每個 instance 的日誌會分別寫到不同的 Log Stream，這樣才不會混在一起，方便追蹤特定 instance 的行為。

**實際情境：**
```
Log Group: /aws/lambda/order-processor
├── Log Stream: 2026/05/08/[$LATEST]abc123  ← Lambda instance 1 的日誌
├── Log Stream: 2026/05/08/[$LATEST]def456  ← Lambda instance 2 的日誌
└── Log Stream: 2026/05/08/[$LATEST]ghi789  ← Lambda instance 3 的日誌
```

**用 AWS CLI 查看 Log Streams：**
```bash
# 列出某個 Log Group 的所有 Log Streams
aws logs describe-log-streams \
  --log-group-name /aws/lambda/my-function \
  --order-by LastEventTime \
  --descending

# 讀取某個 Log Stream 的內容
aws logs get-log-events \
  --log-group-name /aws/lambda/my-function \
  --log-stream-name "2026/05/08/[\$LATEST]abc123"
```

**用 Python boto3 查看：**
```python
import boto3

client = boto3.client("logs", region_name="ap-northeast-1")

# 取得最新的 log stream
response = client.describe_log_streams(
    logGroupName="/aws/lambda/my-function",
    orderBy="LastEventTime",
    descending=True,
    limit=1
)

latest_stream = response["logStreams"][0]["logStreamName"]

# 讀取日誌內容
events = client.get_log_events(
    logGroupName="/aws/lambda/my-function",
    logStreamName=latest_stream
)

for event in events["events"]:
    print(event["message"])
```

**與 Log Group 的關係總結：**
- 你通常在 CloudWatch Console 先找到 Log Group（對應你的服務）
- 再進去找最新的 Log Stream（對應某次執行或某個 instance）
- 最後看裡面的 Log Events（實際的錯誤訊息或輸出）

## 0509

**Git LFS（Large File Storage）**

Git 本身設計來追蹤程式碼（文字檔），對大型二進位檔案（圖片、影片、模型檔、資料集）非常不友善。Git LFS 是 Git 的擴充套件，專門解決這個問題：它把大檔案的實際內容存到另一個地方（LFS 伺服器），Git repo 裡只保留一個「指標檔案」（pointer file），讓 repo 保持輕量。

**為什麼 Git 不適合大檔案：**
Git 每次 commit 都會儲存整個檔案的快照。如果你 commit 了一個 100MB 的模型檔，之後又修改再 commit，repo 裡就會有兩份 100MB，以此類推，repo 會越來越肥，clone 和 pull 都會很慢。

**Git LFS 的運作方式：**
```
一般 Git：
  repo 裡存 → 實際的大檔案內容（100MB）

Git LFS：
  repo 裡存 → pointer file（幾百 bytes）
  LFS 伺服器存 → 實際的大檔案內容（100MB）
```

pointer file 長這樣：
```
version https://git-lfs.github.com/spec/v1
oid sha256:4d7a214614ab2935c943f9e0ff69d22eadbb8f32b1258daaa5e2ca24d17e2393
size 12345678
```

**實作：**
```bash
# 安裝 Git LFS
brew install git-lfs        # macOS
git lfs install             # 初始化（每台機器只需做一次）

# 在 repo 裡設定要追蹤哪些類型的大檔案
git lfs track "*.psd"
git lfs track "*.mp4"
git lfs track "*.bin"
git lfs track "models/**"

# 這會產生 .gitattributes 檔案，要一起 commit
git add .gitattributes
git commit -m "Add LFS tracking rules"

# 之後正常 add/commit/push，LFS 會自動處理
git add large-model.bin
git commit -m "Add model file"
git push origin main        # 大檔案會上傳到 LFS 伺服器，pointer 進 repo
```

**查看 LFS 狀態：**
```bash
# 查看哪些檔案被 LFS 追蹤
git lfs ls-files

# 查看 LFS 追蹤規則
git lfs track
```

**適用場景：**
- 機器學習模型檔（`.bin`、`.pt`、`.onnx`）
- 設計稿（`.psd`、`.sketch`、`.fig`）
- 影音素材（`.mp4`、`.wav`）
- 資料集（`.csv` 超過幾十 MB 時）

**注意事項：**
- GitHub 免費帳號有 1GB LFS 儲存空間和每月 1GB 頻寬限制，超過要付費
- clone 時預設會下載 LFS 檔案，如果只想要程式碼可以用 `GIT_LFS_SKIP_SMUDGE=1 git clone`

---

**Metadata（元資料）**

Metadata 是「描述資料的資料」，本身不是主要內容，而是關於那份內容的附加資訊。

**直觀理解：**
- 一張照片的 metadata：拍攝時間、GPS 座標、相機型號、解析度
- 一個 MP3 的 metadata：歌手、專輯、年份、曲目編號
- 一個 S3 物件的 metadata：Content-Type、上傳時間、自訂標籤

**Metadata 的分類：**

| 類型 | 說明 | 例子 |
|------|------|------|
| 描述性 Metadata | 描述內容是什麼 | 標題、作者、關鍵字 |
| 結構性 Metadata | 描述資料的格式與結構 | 檔案格式、欄位定義、schema |
| 管理性 Metadata | 用於管理和存取控制 | 建立時間、版本、權限 |
| 技術性 Metadata | 技術規格 | 解析度、編碼格式、檔案大小 |

**在 AWS 的情境：**

S3 物件 Metadata：
```python
import boto3

s3 = boto3.client("s3")

# 上傳時附加 metadata
s3.put_object(
    Bucket="my-bucket",
    Key="report.pdf",
    Body=file_content,
    ContentType="application/pdf",
    Metadata={                          # 自訂 metadata（key-value）
        "author": "neo",
        "department": "engineering",
        "version": "2.0"
    }
)

# 讀取 metadata（不下載檔案本體）
response = s3.head_object(Bucket="my-bucket", Key="report.pdf")
print(response["Metadata"])             # {'author': 'neo', ...}
print(response["ContentType"])          # 'application/pdf'
print(response["LastModified"])         # 最後修改時間
print(response["ContentLength"])        # 檔案大小（bytes）
```

EC2 Instance Metadata（IMDS）：
```bash
# EC2 instance 可以查詢自己的 metadata
TOKEN=$(curl -X PUT "http://169.254.169.254/latest/api/token" \
  -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")

# 查詢 instance ID
curl -H "X-aws-ec2-metadata-token: $TOKEN" \
  http://169.254.169.254/latest/meta-data/instance-id

# 查詢所在的 AZ
curl -H "X-aws-ec2-metadata-token: $TOKEN" \
  http://169.254.169.254/latest/meta-data/placement/availability-zone
```

**在資料庫的情境：**
```sql
-- 資料表本身是資料，資料表的 schema 就是 metadata
-- information_schema 是 PostgreSQL 存放 metadata 的地方

-- 查詢某個資料庫裡所有資料表的 metadata
SELECT table_name, table_type
FROM information_schema.tables
WHERE table_schema = 'public';

-- 查詢某個資料表的欄位 metadata
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'users';
```

**Metadata 的重要性：**
- 不用讀取整個檔案就能知道基本資訊（省時省流量）
- 搜尋和過濾的依據（例如 S3 用 metadata 做標籤搜尋）
- 稽核和合規（記錄誰在什麼時候做了什麼）

---

**Transfer Agent（傳輸代理）**

Transfer Agent 是負責在不同系統、位置或格式之間**搬移和轉換資料**的元件或服務。它扮演中間人的角色，處理資料的讀取、轉換、傳輸、以及寫入目標。

**廣義定義：**
任何負責「把資料從 A 搬到 B」的程式或服務都可以叫 Transfer Agent，重點在於它通常還會處理：
- 協定轉換（例如從 FTP 轉成 HTTPS）
- 格式轉換（例如 CSV 轉 JSON）
- 錯誤重試與斷點續傳
- 傳輸狀態追蹤

**在 AWS 的對應服務：**

**AWS DataSync**（最典型的 Transfer Agent）：
```
本地 NAS / S3 / EFS / FSx
        ↓
   DataSync Agent（安裝在本地或 EC2）
        ↓
   AWS DataSync Service（管理、排程、監控）
        ↓
   目標：S3 / EFS / FSx
```

```bash
# 用 AWS CLI 建立 DataSync 任務
aws datasync create-task \
  --source-location-arn arn:aws:datasync:...:location/loc-xxx \
  --destination-location-arn arn:aws:datasync:...:location/loc-yyy \
  --name "nightly-backup"

# 啟動傳輸任務
aws datasync start-task-execution \
  --task-arn arn:aws:datasync:...:task/task-xxx
```

**AWS Transfer Family**（另一個相關服務）：
提供 SFTP、FTP、FTPS 協定的託管端點，讓外部系統可以用傳統的檔案傳輸協定把資料傳進 S3 或 EFS。

```
外部合作夥伴（用 SFTP 上傳）
        ↓
   AWS Transfer Family（SFTP Server）
        ↓
   S3 Bucket
```

**自己實作一個簡單的 Transfer Agent（Python）：**
```python
import boto3
import os
import time
from pathlib import Path

class SimpleTransferAgent:
    def __init__(self, bucket_name, local_dir, prefix=""):
        self.s3 = boto3.client("s3")
        self.bucket = bucket_name
        self.local_dir = Path(local_dir)
        self.prefix = prefix

    def transfer(self, retry=3):
        """把本地目錄的所有檔案上傳到 S3"""
        for file_path in self.local_dir.rglob("*"):
            if file_path.is_file():
                s3_key = f"{self.prefix}/{file_path.name}"
                for attempt in range(retry):
                    try:
                        self.s3.upload_file(str(file_path), self.bucket, s3_key)
                        print(f"✓ 上傳成功：{file_path.name} → s3://{self.bucket}/{s3_key}")
                        break
                    except Exception as e:
                        if attempt == retry - 1:
                            print(f"✗ 上傳失敗（已重試 {retry} 次）：{file_path.name}，錯誤：{e}")
                        else:
                            time.sleep(2 ** attempt)  # exponential backoff

# 使用
agent = SimpleTransferAgent(
    bucket_name="my-data-bucket",
    local_dir="/data/exports",
    prefix="daily-exports/2026-05-09"
)
agent.transfer()
```

**Transfer Agent 的核心功能：**
| 功能 | 說明 |
|------|------|
| 斷點續傳 | 傳輸中斷後從上次的位置繼續，不用重頭來 |
| 錯誤重試 | 遇到暫時性錯誤自動重試（exponential backoff）|
| 進度追蹤 | 記錄哪些檔案已傳、哪些失敗 |
| 並行傳輸 | 同時傳多個檔案，提升吞吐量 |
| 完整性驗證 | 傳完後比對 checksum，確認資料沒有損壞 |

**常見使用場景：**
- 資料遷移：把本地資料中心的資料搬到 AWS S3
- ETL 管線的第一步：把原始資料從來源傳到 Data Lake
- 合作夥伴資料交換：接收外部廠商定期上傳的報表或資料檔

## 0510

**echo $?（上一個指令的結束碼）**

`$?` 是 Shell 的一個特殊變數，儲存**上一個指令執行完後的結束碼（Exit Code）**。`echo $?` 就是把這個數字印出來。

**Exit Code 的規則：**
- `0` = 成功（指令正常結束）
- 非 `0`（1、2、127 等）= 失敗（不同數字代表不同錯誤類型）

這是 Unix 的慣例，所有程式都應該遵守。

**實作範例：**
```bash
# 成功的指令
ls /tmp
echo $?       # 0（成功）

# 失敗的指令
ls /不存在的路徑
echo $?       # 2（No such file or directory）

# 找不到指令
blahblah
echo $?       # 127（command not found）

# 手動設定 exit code（在 script 裡）
exit 0        # 成功結束
exit 1        # 失敗結束
```

**在 Shell Script 裡的應用：**
```bash
#!/bin/bash

# 方法一：用 $? 判斷
python3 my_script.py
if [ $? -ne 0 ]; then
    echo "Script 執行失敗！"
    exit 1
fi

# 方法二：更簡潔的寫法（直接用指令的結果）
if ! python3 my_script.py; then
    echo "Script 執行失敗！"
    exit 1
fi

# 方法三：失敗就立刻停止整個 script（推薦加在 script 開頭）
set -e          # 任何指令失敗就立刻退出
set -o pipefail # pipe 中任一段失敗也算失敗

python3 step1.py
python3 step2.py   # 如果 step1 失敗，這行不會執行
```

**常見 Exit Code 對照：**
| Code | 意義 |
|------|------|
| 0 | 成功 |
| 1 | 一般性錯誤 |
| 2 | 指令用法錯誤（如參數錯誤） |
| 126 | 指令存在但無法執行（權限不足） |
| 127 | 找不到指令（command not found） |
| 130 | 被 Ctrl+C 中斷（SIGINT） |
| 137 | 被 kill -9 強制終止（SIGKILL） |

**在 CI/CD 的重要性：**
GitHub Actions、Jenkins 等 CI 工具都依賴 exit code 來判斷步驟是否成功。你的程式或 script 一定要在失敗時回傳非 0 的 exit code，否則 CI 會誤以為成功。

---

**mkdir -p（遞迴建立目錄）**

`mkdir` 是建立目錄的指令，`-p`（`--parents`）旗標讓它可以**一次建立多層不存在的目錄**，而且如果目錄已存在也不會報錯。

**沒有 `-p` 的問題：**
```bash
mkdir a/b/c
# 如果 a 或 a/b 不存在，會報錯：
# mkdir: a/b: No such file or directory
```

**有 `-p` 的行為：**
```bash
mkdir -p a/b/c
# 不管 a、a/b 存不存在，一律建立整條路徑
# 如果已存在，靜默跳過，不報錯
```

**實際使用情境：**
```bash
# 建立多層專案目錄結構
mkdir -p project/{src,tests,docs}/{utils,models}
# 展開後等於：
# mkdir -p project/src/utils
# mkdir -p project/src/models
# mkdir -p project/tests/utils
# ... 以此類推

# 建立帶日期的備份目錄
DATE=$(date +%Y-%m-%d)
mkdir -p /backups/$DATE/logs
mkdir -p /backups/$DATE/data

# 在 Shell Script 裡確保目錄存在再寫檔
OUTPUT_DIR="/tmp/reports/$(date +%Y%m%d)"
mkdir -p "$OUTPUT_DIR"
echo "report content" > "$OUTPUT_DIR/report.txt"
```

**在 Dockerfile 裡很常見：**
```dockerfile
# 建立應用程式目錄
RUN mkdir -p /app/logs /app/uploads /app/config

WORKDIR /app
COPY . .
```

**`-p` 的兩個功能總結：**
1. **遞迴建立**：自動建立所有中間層目錄
2. **冪等性（Idempotent）**：執行多次結果相同，不會因為目錄已存在而失敗

冪等性在 script 和自動化部署裡很重要，讓你的 script 可以安全地重複執行。

---

**符號連結（Symbolic Link / Symlink）**

符號連結是一種特殊的檔案，它的內容是**指向另一個檔案或目錄的路徑**。類似 Windows 的「捷徑」，但在 Unix/Linux 裡是一等公民，幾乎所有程式都能透明地使用它。

**兩種連結的比較：**

| | 符號連結（Symbolic Link）| 硬連結（Hard Link）|
|--|--------------------------|-------------------|
| 指向 | 路徑（可跨檔案系統）| inode（同一檔案系統）|
| 原始檔刪除後 | 連結失效（dangling link）| 檔案仍然存在 |
| 可指向目錄 | 可以 | 不行 |
| 跨磁碟/分割區 | 可以 | 不行 |
| 常用程度 | 非常常用 | 較少用 |

**建立符號連結：**
```bash
# ln -s <目標（真實路徑）> <連結名稱>
ln -s /usr/local/bin/python3.11 /usr/local/bin/python3

# 建立後查看
ls -la /usr/local/bin/python3
# lrwxr-xr-x  python3 -> /usr/local/bin/python3.11
# 'l' 開頭代表這是一個 symlink，-> 後面是指向的目標
```

**常見使用情境：**

```bash
# 1. 版本管理：讓 python 指向特定版本
ln -s /usr/bin/python3.11 /usr/local/bin/python
python --version   # Python 3.11.x

# 2. 設定檔管理（dotfiles）：把設定檔放在 git repo，用 symlink 連到家目錄
ln -s ~/dotfiles/.zshrc ~/.zshrc
ln -s ~/dotfiles/.vimrc ~/.vimrc
# 這樣設定檔可以用 git 管理，又能在正確位置生效

# 3. 讓多個路徑指向同一份資料
ln -s /data/shared/models /app/models
ln -s /data/shared/models /ml-service/models
# 兩個服務共用同一份模型，不用複製

# 4. 建立「current」指向最新版本
ln -s /releases/v2.3.0 /releases/current
# 部署新版本時只需更新 symlink，不用改應用程式設定
```

**在 Python 裡操作 symlink：**
```python
import os
from pathlib import Path

# 建立 symlink
os.symlink("/data/models/v2", "/app/models/current")

# 用 pathlib（更現代的寫法）
target = Path("/data/models/v2")
link = Path("/app/models/current")
link.symlink_to(target)

# 判斷是否為 symlink
print(link.is_symlink())    # True

# 讀取 symlink 指向的目標
print(os.readlink("/app/models/current"))   # /data/models/v2
print(link.resolve())                        # 解析成絕對路徑

# 刪除 symlink（只刪連結，不刪原始檔）
link.unlink()
```

**注意事項：**
```bash
# 建立指向目錄的 symlink 時，目標路徑結尾不要加 /
ln -s /data/logs myapp-logs      # ✓ 正確
ln -s /data/logs/ myapp-logs     # ✗ 可能造成非預期行為

# 刪除 symlink 用 rm，不要用 rmdir
rm myapp-logs        # ✓ 只刪連結
rmdir myapp-logs     # ✗ 會報錯（它是 symlink，不是真正的目錄）

# 確認 symlink 是否失效（dangling）
file myapp-logs
# 如果顯示 "broken symbolic link" 代表目標已不存在
```

**在 AWS / Docker 的應用：**
```dockerfile
# Dockerfile 裡常用 symlink 讓 log 輸出到 stdout
RUN ln -sf /dev/stdout /var/log/nginx/access.log \
    && ln -sf /dev/stderr /var/log/nginx/error.log
# 這樣 nginx 的 log 會直接輸出到 container 的 stdout/stderr
# Docker 和 CloudWatch 就能收集到這些 log
```

## 0511

**CD Pipeline（持續部署管線）**

CD 是 Continuous Delivery（持續交付）或 Continuous Deployment（持續部署）的縮寫，Pipeline 是「管線」，整體意思是：把程式碼從寫好到上線的過程，自動化成一條流水線，每個步驟依序執行，確保每次部署都是可重複、可靠的。

**CI vs CD 的區別：**
- **CI（Continuous Integration，持續整合）**：開發者每次 push 程式碼，自動跑測試、建置，確保程式碼沒有問題
- **CD（Continuous Delivery）**：在 CI 之後，自動把程式碼打包、部署到測試環境，但上 production 需要人工確認
- **CD（Continuous Deployment）**：更進一步，連 production 也自動部署，完全不需要人工介入

**一條典型的 CD Pipeline 長這樣：**
```
程式碼 push → CI 測試通過 → 建置 Docker Image → 推送到 Registry
    → 部署到 Staging 環境 → 自動化測試 → 部署到 Production
```

**GitHub Actions 範例（CI/CD Pipeline）：**
```yaml
# .github/workflows/deploy.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          pip install -r requirements.txt
          pytest tests/

  build-and-push:
    needs: test          # 測試通過才執行
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build Docker image
        run: docker build -t my-app:${{ github.sha }} .
      - name: Push to ECR
        run: |
          aws ecr get-login-password | docker login --username AWS --password-stdin $ECR_REGISTRY
          docker push $ECR_REGISTRY/my-app:${{ github.sha }}

  deploy-staging:
    needs: build-and-push
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to ECS Staging
        run: |
          aws ecs update-service \
            --cluster staging \
            --service my-app \
            --force-new-deployment

  deploy-production:
    needs: deploy-staging
    runs-on: ubuntu-latest
    environment: production   # 需要人工在 GitHub 上按確認（Continuous Delivery）
    steps:
      - name: Deploy to ECS Production
        run: |
          aws ecs update-service \
            --cluster production \
            --service my-app \
            --force-new-deployment
```

**在 AWS 上的 CD 工具：**
| 工具 | 說明 |
|------|------|
| AWS CodePipeline | AWS 原生的 Pipeline 服務，串接 CodeBuild、CodeDeploy |
| AWS CodeBuild | 執行建置和測試的服務（類似 GitHub Actions 的 runner）|
| AWS CodeDeploy | 負責把程式碼部署到 EC2、ECS、Lambda |
| GitHub Actions + AWS | 最常見的組合，用 GitHub Actions 跑 CI，部署到 AWS |

**CD Pipeline 的核心價值：**
- **速度**：從 commit 到上線可以縮短到幾分鐘
- **一致性**：每次部署步驟完全相同，不會有「在我電腦上可以跑」的問題
- **可回溯**：每個版本都有對應的 artifact，出問題可以快速 rollback
- **信心**：自動化測試確保每次部署前程式碼是健康的

---

**抽象化（Abstraction）**

抽象化是把「不同事物的共同本質」提取出來，忽略不重要的細節，只保留關鍵的概念。就像你說的例子：一個蘋果加一個蘋果、一個橘子加一個橘子，都可以用 `1 + 1 = 2` 來描述——這就是抽象化，把具體的「蘋果」和「橘子」抽象成「數字」。

**為什麼需要抽象化：**
現實世界太複雜，如果每次都要處理所有細節，人腦和程式都會不堪負荷。抽象化讓我們可以在不同層次思考問題，每一層只關心自己那層的事。

**抽象化的層次（以電腦為例）：**
```
你寫的 Python 程式
    ↓ 抽象
Python 直譯器（把 Python 翻成機器碼）
    ↓ 抽象
作業系統（管理記憶體、檔案、進程）
    ↓ 抽象
CPU 指令集（x86、ARM）
    ↓ 抽象
電晶體（0 和 1）
```
每一層都不需要知道下面那層的細節，只需要透過定義好的介面溝通。

**程式設計中的抽象化：**

```python
# 沒有抽象化：每次都要處理細節
# 計算圓面積
circle_area = 3.14159 * 5 * 5
# 計算另一個圓
circle_area2 = 3.14159 * 10 * 10

# 有抽象化：把「計算圓面積」這個概念抽象成函式
import math

def circle_area(radius):
    return math.pi * radius ** 2

# 使用者不需要知道 π 是多少，只需要知道「給半徑，得面積」
print(circle_area(5))   # 78.53...
print(circle_area(10))  # 314.15...
```

```python
# 更高層的抽象：把「形狀」抽象成一個概念
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self) -> float:
        pass

    @abstractmethod
    def perimeter(self) -> float:
        pass

class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius

    def area(self):
        return math.pi * self.radius ** 2

    def perimeter(self):
        return 2 * math.pi * self.radius

class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height

    def perimeter(self):
        return 2 * (self.width + self.height)

# 使用者只需要知道「形狀有面積和周長」，不需要知道各自怎麼算
shapes = [Circle(5), Rectangle(4, 6), Circle(3)]
for shape in shapes:
    print(f"面積：{shape.area():.2f}")  # 統一介面，不管是哪種形狀
```

**在 AWS 架構中的抽象化：**
- **S3**：把「儲存」抽象化，你不需要知道資料存在哪台硬碟、哪個機房
- **Lambda**：把「執行程式碼」抽象化，你不需要管伺服器、OS、記憶體分配
- **RDS**：把「資料庫管理」抽象化，備份、patch、failover 都幫你處理

**抽象化的好處：**
| 好處 | 說明 |
|------|------|
| 降低複雜度 | 每次只需要思考當前層次的問題 |
| 可重用性 | 抽象出來的概念可以在不同地方使用 |
| 可替換性 | 底層實作可以換掉，上層不受影響 |
| 可讀性 | 程式碼更接近人類語言，更容易理解 |

**抽象化的代價：**
抽象化不是免費的，每一層抽象都有效能開銷（overhead）。過度抽象會讓程式碼難以理解和除錯。好的抽象是「剛好夠用」，不多也不少。

---

**建立假設與驗證假設的 SOP**

這是一套系統性的思考框架，讓你在面對任何問題時，都能有條理地從「觀察現象」到「得出結論」，而不是憑感覺亂猜。這套方法來自科學方法論，但在工程、產品、甚至日常決策中都非常實用。

**核心流程：**
```
描述事實（觀察）
    ↓
建立 Baseline（現況基準）
    ↓
提出假設（可能的原因或解法）
    ↓
設計實驗（如何驗證）
    ↓
執行並收集數據
    ↓
分析結果（假設成立 or 推翻）
    ↓
得出結論 / 調整假設
```

**每個步驟的說明：**

**1. 描述事實（不加主觀判斷）**
只描述你觀察到的現象，不要加入推測或情緒。

```
❌ 不好的描述：「系統很慢，一定是資料庫的問題」
✓ 好的描述：「API /orders 的 P99 延遲從昨天的 200ms 上升到今天的 1500ms，
             發生時間從 14:00 開始，影響約 30% 的請求」
```

**2. 建立 Baseline（問題的基準線）**
Baseline 是「正常狀態應該是什麼」，有了 baseline 才能判斷現在是否異常，以及改善了多少。

```python
# 工程上的 Baseline 範例：效能測試前先建立基準
import time
import statistics

def measure_baseline(func, iterations=100):
    """測量函式的基準效能"""
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        func()
        end = time.perf_counter()
        times.append(end - start)

    return {
        "mean": statistics.mean(times),
        "median": statistics.median(times),
        "p95": sorted(times)[int(len(times) * 0.95)],
        "p99": sorted(times)[int(len(times) * 0.99)],
    }

# 先建立 baseline，再做優化，才能知道優化了多少
baseline = measure_baseline(my_function)
print(f"Baseline P99: {baseline['p99'] * 1000:.2f}ms")

# 做了某個優化後
after_optimization = measure_baseline(my_optimized_function)
print(f"After P99: {after_optimization['p99'] * 1000:.2f}ms")
improvement = (baseline['p99'] - after_optimization['p99']) / baseline['p99'] * 100
print(f"改善了 {improvement:.1f}%")
```

**3. 提出假設（要可被驗證）**
好的假設必須是「可以被證明是錯的」（falsifiable），否則不是假設，是信仰。

```
❌ 不好的假設：「系統可能有問題」（太模糊，無法驗證）
✓ 好的假設：「14:00 部署的新版本引入了 N+1 query 問題，
             導致每個 /orders 請求多發了約 50 次 DB 查詢」
```

**4. 設計實驗（控制變因）**
每次只改一個變因，這樣才能確定是哪個因素造成差異。

```bash
# 例：驗證「是否是新版本造成的」
# 實驗：把流量切回舊版本，看延遲是否恢復

# 用 AWS ALB 做 A/B 測試，10% 流量給舊版本
aws elbv2 modify-rule \
  --rule-arn arn:aws:elasticloadbalancing:... \
  --actions '[
    {"Type": "forward", "ForwardConfig": {
      "TargetGroups": [
        {"TargetGroupArn": "arn:...old-version", "Weight": 10},
        {"TargetGroupArn": "arn:...new-version", "Weight": 90}
      ]
    }}
  ]'
```

**5. 分析結果**
用數據說話，不要用感覺。

```python
# 用 CloudWatch 查詢實驗前後的延遲數據
import boto3
from datetime import datetime, timedelta

cloudwatch = boto3.client("cloudwatch")

def get_p99_latency(start_time, end_time, service_version):
    response = cloudwatch.get_metric_statistics(
        Namespace="MyApp",
        MetricName="APILatency",
        Dimensions=[{"Name": "Version", "Value": service_version}],
        StartTime=start_time,
        EndTime=end_time,
        Period=300,
        Statistics=["p99"],
        ExtendedStatistics=["p99"]
    )
    return response["Datapoints"]

# 比較新舊版本的 P99 延遲
old_latency = get_p99_latency(start, end, "v1.2.3")
new_latency = get_p99_latency(start, end, "v1.2.4")
# 如果舊版本 P99 = 200ms，新版本 P99 = 1500ms → 假設成立
```

**這套 SOP 的實際應用場景：**

| 場景 | 事實描述 | Baseline | 假設 | 驗證方式 |
|------|---------|----------|------|---------|
| 效能問題 | API 延遲從 200ms 升到 1500ms | 過去 7 天 P99 = 200ms | 新版本引入 N+1 query | rollback 看延遲是否恢復 |
| 功能開發 | 用戶結帳流失率 60% | 業界平均 20% | 結帳步驟太多導致放棄 | A/B 測試簡化版結帳流程 |
| 學習新技術 | 不知道 async 是否真的更快 | 同步版本跑 100 個請求需 30 秒 | async 版本應該快 3-5 倍 | 實際跑 benchmark 比較 |

**為什麼這套 SOP 重要：**
- 避免「確認偏誤」：先有結論再找證據的陷阱
- 讓溝通更有效率：跟別人討論時，大家都在同一個框架下思考
- 累積可複用的知識：每次驗證的結果都是下次的 baseline 和參考
- 在不確定的情況下做出有根據的決策，而不是靠直覺賭博


---

**Terraform Variables 與 Outputs**

Terraform 是 Infrastructure as Code（IaC）工具，讓你用程式碼描述並管理雲端資源。Variables 和 Outputs 是讓 Terraform 設定檔可重用、可組合的核心機制。

**Variables（輸入變數）**

Variables 就像函式的參數，讓你把「會變動的值」從設定檔裡抽出來，不同環境（dev/staging/prod）可以傳入不同的值，而不用改程式碼本身。

宣告方式：
```hcl
# variables.tf
variable "instance_type" {
  description = "EC2 instance 的規格"
  type        = string
  default     = "t3.micro"   # 有 default 就不一定要傳值
}

variable "environment" {
  description = "部署環境"
  type        = string
  # 沒有 default，執行時必須提供
}

variable "allowed_ports" {
  description = "允許的 port 清單"
  type        = list(number)
  default     = [80, 443]
}
```

使用方式（在 resource 裡用 `var.` 引用）：
```hcl
# main.tf
resource "aws_instance" "web" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = var.instance_type   # 引用 variable

  tags = {
    Environment = var.environment
  }
}
```

傳入變數的三種方式：
```bash
# 方法一：執行時用 -var 旗標
terraform apply -var="environment=prod" -var="instance_type=t3.small"

# 方法二：用 .tfvars 檔案（推薦，可以 git 管理）
# terraform.tfvars
environment   = "prod"
instance_type = "t3.small"

terraform apply  # 自動讀取 terraform.tfvars

# 方法三：環境變數（前綴 TF_VAR_）
export TF_VAR_environment="prod"
terraform apply
```

**Outputs（輸出值）**

Outputs 讓你在 `terraform apply` 完成後，把重要的資源資訊印出來，或是讓其他 Terraform module 引用。就像函式的 return value。

宣告方式：
```hcl
# outputs.tf
output "instance_public_ip" {
  description = "EC2 instance 的 public IP"
  value       = aws_instance.web.public_ip
}

output "instance_id" {
  description = "EC2 instance ID"
  value       = aws_instance.web.id
}

output "db_endpoint" {
  description = "RDS 資料庫的連線端點"
  value       = aws_db_instance.main.endpoint
  sensitive   = true   # 敏感資訊，不會直接印在 terminal 上
}
```

執行後的輸出：
```bash
terraform apply
# ...（建立資源）...
# Outputs:
# instance_public_ip = "54.123.45.67"
# instance_id        = "i-0abc123def456"
# db_endpoint        = <sensitive>

# 事後也可以單獨查詢
terraform output
terraform output instance_public_ip   # 只查某一個
terraform output -json                # 輸出成 JSON 格式（方便給其他程式用）
```

**Variables 與 Outputs 的關係：**
```
外部（.tfvars / CLI / 環境變數）
        ↓  Variables（輸入）
   Terraform 設定檔（main.tf）
        ↓  Outputs（輸出）
   terminal 顯示 / 其他 module 引用
```

**在 Module 之間傳遞資料：**
Outputs 最重要的用途之一是讓 parent module 取得 child module 建立的資源資訊：
```hcl
# modules/network/outputs.tf
output "vpc_id" {
  value = aws_vpc.main.id
}

# main.tf（parent module）
module "network" {
  source = "./modules/network"
}

module "compute" {
  source = "./modules/compute"
  vpc_id = module.network.vpc_id   # 用 module.<name>.<output> 引用
}
```

**實際情境（AWS 架構）：**
```hcl
# 建立 S3 bucket，output bucket name 給 CI/CD pipeline 用
resource "aws_s3_bucket" "artifacts" {
  bucket = "my-app-artifacts-${var.environment}"
}

output "artifact_bucket_name" {
  value = aws_s3_bucket.artifacts.bucket
}

# CI/CD pipeline 執行：
# terraform output -raw artifact_bucket_name
# → my-app-artifacts-prod
# 然後把這個值傳給 GitHub Actions 做後續部署
```

---

**Terraform Import**

`terraform import` 解決一個常見問題：**已經在 AWS Console 手動建立的資源，如何納入 Terraform 管理？**

如果不 import，Terraform 不知道這個資源存在，下次執行 `terraform apply` 可能會嘗試重複建立，或是在 `terraform destroy` 時漏掉它。

**運作原理：**
```
AWS 上已存在的資源（例如手動建立的 EC2）
        ↓  terraform import
   Terraform state file（.tfstate）
        ↓  之後的 plan/apply/destroy
   Terraform 正常管理這個資源
```

Import 只是把資源的「現況」寫進 state file，**不會自動產生 .tf 設定檔**，你還需要自己補寫對應的 resource block。

**方法一：CLI 指令（傳統方式）**
```bash
# 語法：terraform import <resource_type>.<resource_name> <resource_id>

# 匯入一台已存在的 EC2 instance
terraform import aws_instance.web i-0abc123def456789

# 匯入一個 S3 bucket
terraform import aws_s3_bucket.my_bucket my-existing-bucket-name

# 匯入 Security Group
terraform import aws_security_group.allow_http sg-0123456789abcdef0
```

執行前，你必須先在 .tf 檔案裡寫好對應的 resource block（即使是空的）：
```hcl
# main.tf（先寫好這個，才能 import）
resource "aws_instance" "web" {
  # 先留空，import 後再補齊屬性
}
```

Import 完成後，用 `terraform show` 查看 state，再把屬性補回 .tf 檔：
```bash
terraform show   # 查看 state 裡的資源詳情
terraform plan   # 確認 plan 沒有 diff（代表 .tf 和實際狀態一致）
```

**方法二：Import Block（Terraform 1.5+ 新方式，推薦）**
```hcl
# import.tf
import {
  to = aws_instance.web
  id = "i-0abc123def456789"
}

resource "aws_instance" "web" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t3.micro"
  # ... 其他屬性
}
```

```bash
terraform plan    # 先預覽，確認 import 的內容正確
terraform apply   # 執行 import
```

Import Block 的優點是可以 code review、可以 plan 預覽，比 CLI 指令更安全。

**常見使用情境：**
| 情境 | 說明 |
|------|------|
| 接手舊專案 | 前人手動建的資源，現在要用 Terraform 統一管理 |
| 補救手動操作 | 緊急時在 Console 手動建了資源，事後補 import |
| 遷移到 Terraform | 原本用其他工具（CloudFormation、Pulumi）管理，要換成 Terraform |

**Import 的限制：**
- 一次只能 import 一個資源（CLI 方式）
- 不是所有資源都支援 import（要查 provider 文件）
- Import 後 .tf 設定檔要自己補寫，否則下次 plan 會顯示 diff

**參考資料：** [Terraform 基礎 - 變數 Variables 與輸出 Outputs](https://medium.com/@minghunghsieh/day-11-terraform%E5%9F%BA%E7%A4%8E-%E8%AE%8A%E6%95%B8-variables-%E8%88%87%E8%BC%B8%E5%87%BA-outputs-50e09e793bb7)（Content was rephrased for compliance with licensing restrictions）
