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

## 0512

**nginx**

nginx（讀作 "engine-x"）是一個高效能的開源 Web 伺服器，同時也常被用作反向代理（Reverse Proxy）、負載均衡器（Load Balancer）和 HTTP 快取。它的設計目標是處理大量並發連線，在高流量場景下比傳統的 Apache 更省記憶體。

**原理：**
nginx 採用事件驅動（event-driven）、非同步（asynchronous）的架構。傳統 Web 伺服器（如 Apache）每個請求開一個 thread 或 process，當連線數很多時記憶體消耗巨大。nginx 用少量的 worker process，每個 worker 用 event loop 同時處理數千個連線，類似 Node.js 的概念。

```
Client 請求
    ↓
nginx（反向代理）
    ↓
後端服務（FastAPI / Node.js / Django）
```

**常見使用情境：**
1. **靜態檔案伺服器**：直接提供 HTML、CSS、JS、圖片
2. **反向代理**：把外部請求轉發給後端 App Server
3. **負載均衡**：把流量分散到多台後端伺服器
4. **SSL 終止**：在 nginx 層處理 HTTPS，後端只需處理 HTTP
5. **限流（Rate Limiting）**：防止某個 IP 發太多請求

**實作：基本設定檔**
```nginx
# /etc/nginx/nginx.conf 或 /etc/nginx/conf.d/myapp.conf

server {
    listen 80;
    server_name example.com;

    # 靜態檔案
    location /static/ {
        root /var/www/myapp;
        expires 30d;   # 快取 30 天
    }

    # 反向代理到後端 FastAPI
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}

# 負載均衡設定
upstream backend_pool {
    server 10.0.1.10:8000 weight=3;   # 這台分到 3/5 的流量
    server 10.0.1.11:8000 weight=2;   # 這台分到 2/5 的流量
    server 10.0.1.12:8000 backup;     # 備用，前兩台都掛才啟用
}

server {
    listen 80;
    location / {
        proxy_pass http://backend_pool;
    }
}
```

**常用指令：**
```bash
# 啟動 / 停止 / 重啟
sudo systemctl start nginx
sudo systemctl stop nginx
sudo systemctl reload nginx   # 重新載入設定（不中斷連線）

# 測試設定檔語法是否正確（改完設定一定要先跑這個）
sudo nginx -t

# 查看 access log
tail -f /var/log/nginx/access.log

# 查看 error log
tail -f /var/log/nginx/error.log
```

**在 Docker 裡使用 nginx：**
```dockerfile
FROM nginx:alpine

# 複製自訂設定檔
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 複製靜態網站檔案
COPY dist/ /usr/share/nginx/html/

EXPOSE 80
```

**與 AWS 的關聯：**
- EC2 上常用 nginx 作為 App Server 前面的反向代理
- 在 ECS 容器裡，nginx 常和 FastAPI/Node.js 容器一起部署（sidecar pattern）
- ALB（Application Load Balancer）在 AWS 層面做了類似 nginx 負載均衡的事，但 nginx 更靈活，可以做細粒度的路由規則

---

**diff（比較差異的工具）**

`diff` 是 Unix/Linux 的指令，用來比較兩個檔案（或目錄）之間的差異，輸出哪些行被新增、刪除或修改。Git 的 `git diff` 就是基於這個概念。

**基本用法：**
```bash
# 比較兩個檔案
diff file1.txt file2.txt

# 輸出格式說明：
# < 代表 file1 有、file2 沒有（被刪除的行）
# > 代表 file2 有、file1 沒有（被新增的行）
# --- 分隔線

# 範例輸出：
# 3c3          ← 第 3 行被修改（c = change）
# < hello world
# ---
# > hello nginx
# 5d4          ← 第 5 行被刪除（d = delete）
# < old line
# 7a8          ← 在第 7 行後新增（a = add）
# > new line
```

**更好讀的格式（unified diff）：**
```bash
# -u 輸出 unified 格式（git diff 預設就是這個格式）
diff -u file1.txt file2.txt

# 輸出範例：
# --- file1.txt   2026-05-12 10:00:00
# +++ file2.txt   2026-05-12 10:05:00
# @@ -1,5 +1,5 @@
#  不變的行
# -被刪除的行（紅色）
# +被新增的行（綠色）
#  不變的行
```

**比較目錄：**
```bash
# 遞迴比較兩個目錄的所有檔案
diff -r dir1/ dir2/

# 只顯示哪些檔案不同，不顯示內容
diff -rq dir1/ dir2/
```

**實際使用情境：**
```bash
# 1. 查看 git 的修改內容
git diff                    # 工作區 vs 暫存區
git diff --staged           # 暫存區 vs 最新 commit
git diff HEAD~1 HEAD        # 最新兩個 commit 的差異

# 2. 比較設定檔的差異（部署前確認改了什麼）
diff /etc/nginx/nginx.conf.bak /etc/nginx/nginx.conf

# 3. 產生 patch 檔（把差異儲存起來，之後套用到其他地方）
diff -u original.py modified.py > my_changes.patch

# 套用 patch
patch original.py < my_changes.patch
```

**在 Python 裡做 diff：**
```python
import difflib

text1 = """line 1
line 2
line 3
line 4""".splitlines()

text2 = """line 1
line 2 modified
line 3
line 5 new""".splitlines()

# unified diff（類似 git diff 的輸出）
diff = difflib.unified_diff(text1, text2, lineterm="", fromfile="before", tofile="after")
print("\n".join(diff))

# HTML 格式的 diff（可以在網頁上顯示）
html_diff = difflib.HtmlDiff()
html = html_diff.make_file(text1, text2)
with open("diff.html", "w") as f:
    f.write(html)
```

**與 patch 的關係：**
`diff` 產生差異，`patch` 套用差異。這是 Linux 核心開發早期的協作方式：開發者用 `diff` 產生 patch 檔，用 email 寄給 Linus Torvalds，Linus 用 `patch` 套用。Git 的出現讓這個流程更自動化，但底層概念相同。

---

**OpenResty（resty）與 Docker 的關聯**

OpenResty 是一個基於 nginx 的 Web 平台，它把 nginx 和 LuaJIT（Lua 語言的即時編譯器）整合在一起，讓你可以用 Lua 腳本直接在 nginx 裡寫業務邏輯，不需要另外起一個 App Server。`resty` 是 OpenResty 提供的命令列工具，用來執行 Lua 腳本。

**OpenResty = nginx + Lua**

```
一般架構：
Client → nginx（反向代理）→ Python/Node.js App Server → 資料庫

OpenResty 架構：
Client → OpenResty（nginx + Lua 業務邏輯）→ 資料庫
         （省掉了 App Server 這一層）
```

**為什麼要用 OpenResty：**
- 在 nginx 層就能處理請求，不用轉發到後端，延遲更低
- 適合做 API Gateway、認證、限流、快取等「橫切關注點」
- 比純 nginx 設定更靈活，比起一個完整的 App Server 更輕量

**resty 指令的用途：**
```bash
# resty 是 OpenResty 的 CLI，可以直接執行 Lua 腳本
resty -e 'print("Hello from OpenResty")'

# 執行一個 Lua 腳本檔案
resty my_script.lua

# 常用於測試 OpenResty 的 Lua 邏輯
```

**OpenResty 設定範例（在 nginx.conf 裡寫 Lua）：**
```nginx
server {
    listen 8080;

    location /api/auth {
        # 在 nginx 請求處理階段執行 Lua 程式碼
        access_by_lua_block {
            local token = ngx.req.get_headers()["Authorization"]
            if not token or token ~= "Bearer secret123" then
                ngx.status = 401
                ngx.say('{"error": "Unauthorized"}')
                return ngx.exit(401)
            end
        }

        proxy_pass http://backend:8000;
    }

    location /rate-limit {
        # 用 Lua 實作限流
        access_by_lua_block {
            local limit = require "resty.limit.req"
            -- 每秒最多 10 個請求
            local lim, err = limit.new("my_limit_store", 10, 5)
            local key = ngx.var.remote_addr
            local delay, err = lim:incoming(key, true)
            if not delay then
                if err == "rejected" then
                    return ngx.exit(429)  -- Too Many Requests
                end
            end
        }
        proxy_pass http://backend:8000;
    }
}
```

**OpenResty 與 Docker 的關聯：**
OpenResty 有官方的 Docker image，在容器化部署中很常見，尤其是作為 API Gateway 或邊緣代理。

```dockerfile
# 使用 OpenResty 官方 Docker image
FROM openresty/openresty:alpine

# 複製 nginx 設定（包含 Lua 邏輯）
COPY nginx.conf /usr/local/openresty/nginx/conf/nginx.conf

# 複製 Lua 腳本
COPY lua/ /usr/local/openresty/lualib/

EXPOSE 80 443
```

```yaml
# docker-compose.yml：OpenResty 作為 API Gateway
version: "3"
services:
  gateway:
    image: openresty/openresty:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/usr/local/openresty/nginx/conf/nginx.conf
    depends_on:
      - api

  api:
    build: ./api
    expose:
      - "8000"
```

**常見使用場景：**
- **API Gateway**：統一入口，做認證、限流、路由
- **邊緣快取**：在 nginx 層快取 API 回應，減少後端壓力
- **A/B 測試**：用 Lua 腳本根據條件把流量導向不同版本
- **Kong API Gateway**：知名的開源 API Gateway，底層就是基於 OpenResty

**與純 nginx 的差別：**
| | nginx | OpenResty |
|--|-------|-----------|
| 邏輯能力 | 只能用設定檔語法 | 可以寫完整的 Lua 程式 |
| 靈活性 | 有限 | 非常高 |
| 學習曲線 | 低 | 需要學 Lua |
| 適合場景 | 靜態代理、負載均衡 | API Gateway、複雜路由邏輯 |

---

**沙盒（Sandbox）**

沙盒是一個隔離的執行環境，讓程式在裡面跑，但無法影響外部系統。就像小孩在沙盒裡玩沙，沙不會跑到外面去。核心概念是「隔離」和「限制」：沙盒內的程式碼即使有惡意行為或 bug，也無法破壞宿主系統。

**為什麼需要沙盒：**
- 執行不信任的程式碼（用戶上傳的腳本、第三方插件）
- 測試環境與生產環境隔離
- 瀏覽器執行 JavaScript（每個 tab 是一個沙盒）
- 安全研究：在沙盒裡分析惡意軟體

**沙盒的實現方式（從輕量到重量）：**

```
輕量 ←————————————————————————→ 重量
進程隔離 → 容器（Docker）→ VM → 實體機器
（隔離程度越高，效能開銷越大）
```

**1. 進程層級的沙盒（Linux seccomp）：**
```python
# Python 的 RestrictedPython：限制 Python 程式碼能做的事
from RestrictedPython import compile_restricted, safe_globals

user_code = """
result = 1 + 1
print(result)
"""

# 在受限環境中執行（無法 import os、無法讀寫檔案）
byte_code = compile_restricted(user_code)
exec(byte_code, safe_globals)
```

**2. 容器沙盒（Docker）：**
Docker 本身就是一種沙盒，容器內的進程無法直接存取宿主機的檔案系統或網路（除非明確掛載）。

```bash
# 用 Docker 執行不信任的程式碼
# --network none：完全隔離網路
# --read-only：檔案系統唯讀
# --memory 128m：限制記憶體
# --cpus 0.5：限制 CPU
docker run \
  --network none \
  --read-only \
  --memory 128m \
  --cpus 0.5 \
  --rm \
  python:3.11-slim \
  python -c "print('hello from sandbox')"
```

**3. gVisor（Google 的容器沙盒）：**
比 Docker 更安全的容器沙盒，在容器和 Linux kernel 之間加了一層攔截，即使容器逃逸也無法直接存取 kernel。

```yaml
# 在 Kubernetes 上使用 gVisor（RuntimeClass）
apiVersion: node.k8s.io/v1
kind: RuntimeClass
metadata:
  name: gvisor
handler: runsc   # gVisor 的 runtime

---
apiVersion: v1
kind: Pod
spec:
  runtimeClassName: gvisor   # 這個 Pod 用 gVisor 沙盒執行
  containers:
  - name: untrusted-app
    image: my-app:latest
```

**在 AWS 的沙盒概念：**
- **Lambda**：每次執行都在獨立的沙盒環境，執行完就銷毀，天然隔離
- **Firecracker**：AWS 開發的輕量 VM，Lambda 和 Fargate 底層用的就是 Firecracker，每個函式執行在獨立的 microVM 裡
- **AWS Sandbox Account**：AWS 組織裡專門用來實驗的帳號，和生產環境完全隔離

```python
# AWS Lambda 的沙盒特性
# 每次 cold start 都是全新的沙盒環境
# 但同一個 execution environment 可能被重用（warm start）

import boto3

def lambda_handler(event, context):
    # 這段程式碼在 Lambda 的沙盒裡執行
    # 無法存取其他 Lambda 的記憶體
    # 無法存取宿主機的檔案系統（只有 /tmp 可寫）
    
    with open("/tmp/temp_file.txt", "w") as f:
        f.write("只有 /tmp 可以寫入")
    
    return {"statusCode": 200}
```

**沙盒的限制與代價：**
| 面向 | 說明 |
|------|------|
| 效能 | 隔離層帶來額外開銷，越嚴格越慢 |
| 功能限制 | 沙盒內可能無法使用某些系統呼叫 |
| 複雜度 | 設定和維護沙盒環境需要額外工作 |
| 逃逸風險 | 沙盒不是 100% 安全，有 kernel 漏洞就可能被逃逸 |

---

**Guardrails（護欄）**

Guardrails 字面意思是「護欄」，在技術領域有兩個主要用法：一是 **AWS Bedrock Guardrails**（AI 安全護欄），二是泛指系統中的「防護機制」，防止程式或使用者做出不符合預期的行為。

**1. AWS Bedrock Guardrails（AI 護欄）**

AWS Bedrock Guardrails 是 AWS 提供的服務，讓你在 AI 應用上設定安全邊界，控制 LLM（大型語言模型）的輸入和輸出，防止有害內容、資料外洩、或偏離主題的回應。

**解決什麼問題：**
直接使用 LLM 有風險：用戶可能問出有害問題、模型可能洩漏敏感資訊、或回答超出業務範圍的問題。Guardrails 在 LLM 前後加了一層過濾。

```
用戶輸入
    ↓
Guardrails（輸入過濾）
    ↓
LLM（Claude / Llama 等）
    ↓
Guardrails（輸出過濾）
    ↓
回傳給用戶
```

**AWS Bedrock Guardrails 的功能：**
- **內容過濾**：過濾仇恨言論、暴力、色情等有害內容
- **話題拒絕**：設定禁止討論的話題（例如競爭對手、政治）
- **敏感資訊遮罩**：自動偵測並遮罩 PII（個人識別資訊）如信用卡號、身分證號
- **幻覺偵測（Grounding）**：確保模型回答有根據，不是憑空捏造

**實作（Python boto3）：**
```python
import boto3

bedrock = boto3.client("bedrock", region_name="us-east-1")

# 建立 Guardrail
response = bedrock.create_guardrail(
    name="my-app-guardrail",
    description="防止有害內容和 PII 外洩",
    
    # 內容過濾設定
    contentPolicyConfig={
        "filtersConfig": [
            {"type": "HATE", "inputStrength": "HIGH", "outputStrength": "HIGH"},
            {"type": "VIOLENCE", "inputStrength": "MEDIUM", "outputStrength": "HIGH"},
        ]
    },
    
    # 敏感資訊遮罩
    sensitiveInformationPolicyConfig={
        "piiEntitiesConfig": [
            {"type": "CREDIT_DEBIT_CARD_NUMBER", "action": "BLOCK"},
            {"type": "EMAIL", "action": "ANONYMIZE"},
            {"type": "PHONE", "action": "ANONYMIZE"},
        ]
    },
    
    # 禁止討論的話題
    topicPolicyConfig={
        "topicsConfig": [
            {
                "name": "competitor-products",
                "definition": "討論競爭對手的產品或服務",
                "type": "DENY"
            }
        ]
    }
)

guardrail_id = response["guardrailId"]

# 使用 Guardrail 呼叫模型
bedrock_runtime = boto3.client("bedrock-runtime", region_name="us-east-1")

response = bedrock_runtime.invoke_model(
    modelId="anthropic.claude-3-sonnet-20240229-v1:0",
    guardrailIdentifier=guardrail_id,
    guardrailVersion="DRAFT",
    body=json.dumps({
        "messages": [{"role": "user", "content": "幫我寫一封詐騙信"}]
    })
)
# Guardrails 會攔截這個請求，回傳被拒絕的訊息
```

**2. 泛指的 Guardrails（系統護欄）**

在更廣泛的工程語境中，guardrails 指任何防止系統或使用者越界的機制：

```python
# 例：API 的 guardrails
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, validator

app = FastAPI()

class OrderRequest(BaseModel):
    quantity: int
    price: float

    @validator("quantity")
    def quantity_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("數量必須大於 0")  # ← 這就是一個 guardrail
        if v > 10000:
            raise ValueError("單次訂單不能超過 10000 件")  # ← 防止異常大單
        return v

    @validator("price")
    def price_must_be_reasonable(cls, v):
        if v < 0.01:
            raise ValueError("價格不能低於 0.01")
        if v > 1_000_000:
            raise ValueError("價格異常，請確認")
        return v
```

```python
# Terraform 的 guardrails：用 AWS Service Control Policy（SCP）
# 防止任何人在組織內刪除 CloudTrail（稽核日誌）
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Deny",
            "Action": [
                "cloudtrail:DeleteTrail",
                "cloudtrail:StopLogging"
            ],
            "Resource": "*"
        }
    ]
}
```

**Guardrails 的核心思想：**
與其依賴「每個人都做對的事」，不如在系統層面設置護欄，讓錯誤的操作根本無法發生。這是「防禦性設計」（defensive design）的體現。

**常見的 Guardrails 類型：**
| 類型 | 例子 |
|------|------|
| 輸入驗證 | API 參數範圍限制、型別檢查 |
| 權限控制 | IAM Policy、SCP 阻止危險操作 |
| 速率限制 | API Rate Limiting，防止濫用 |
| AI 安全 | AWS Bedrock Guardrails，過濾有害內容 |
| 預算護欄 | AWS Budget Alert，超過費用上限自動通知或停止 |
| 部署護欄 | 藍綠部署的自動 rollback 條件 |

---

---

**反向代理（Reverse Proxy）**

反向代理是一台位於客戶端和後端伺服器之間的中間伺服器。客戶端以為自己在直接跟目標伺服器溝通，但實際上所有請求都先到反向代理，由它決定要轉發給哪台後端。

**正向代理 vs 反向代理的差別：**

| | 正向代理（Forward Proxy）| 反向代理（Reverse Proxy）|
|--|--------------------------|--------------------------|
| 代理誰 | 代理**客戶端**（幫客戶端出去） | 代理**伺服器**（幫伺服器接進來）|
| 客戶端知道嗎 | 客戶端知道自己在用代理 | 客戶端不知道後面有幾台伺服器 |
| 常見用途 | VPN、翻牆、企業內網出口 | nginx、CDN、API Gateway |

**反向代理能做什麼：**
```
客戶端
    ↓ 請求 https://api.example.com/orders
反向代理（nginx）
    ├── /orders → 轉發給 order-service:8001
    ├── /users  → 轉發給 user-service:8002
    └── /static → 直接從本地磁碟回傳靜態檔案
```

1. **路由分發**：根據 URL 路徑把請求導向不同後端服務
2. **負載均衡**：把流量分散到多台後端，避免單點過載
3. **SSL 終止**：在反向代理層處理 HTTPS，後端只需處理 HTTP
4. **快取**：把常見回應快取起來，不用每次都打後端
5. **隱藏後端**：外部看不到後端的 IP、port、架構

**nginx 作為反向代理的設定：**
```nginx
server {
    listen 443 ssl;
    server_name api.example.com;

    # SSL 憑證（在反向代理層終止 HTTPS）
    ssl_certificate     /etc/ssl/certs/example.com.crt;
    ssl_certificate_key /etc/ssl/private/example.com.key;

    # 把所有請求轉發給後端 FastAPI（後端只跑 HTTP）
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        # 告訴後端原始請求是 HTTPS
        proxy_set_header X-Forwarded-Proto https;
    }
}
```

**在 AWS 的對應：**
- **ALB（Application Load Balancer）**：AWS 託管的反向代理 + 負載均衡器
- **CloudFront**：AWS 的 CDN，也是一種反向代理，把請求導向 S3 或 EC2
- **API Gateway**：專門為 API 設計的反向代理，可以做認證、限流、轉換

---

**SSL / TLS（加密傳輸協定）**

SSL（Secure Sockets Layer）是早期的加密傳輸協定，現在實際上已被 TLS（Transport Layer Security）取代，但大家習慣還是叫 SSL。你看到 `https://` 的網站，背後用的就是 TLS。

**解決什麼問題：**
HTTP 是明文傳輸，中間任何人都能看到你傳的內容（密碼、信用卡號等）。SSL/TLS 在 HTTP 上加了一層加密，讓傳輸內容只有客戶端和伺服器能看懂。

**TLS 握手流程（簡化版）：**
```
客戶端                          伺服器
   |                               |
   |── 1. ClientHello ────────────>|  我支援哪些加密方式
   |<── 2. ServerHello ────────────|  我選這個加密方式
   |<── 3. 憑證（Certificate）─────|  這是我的身份證明
   |── 4. 驗證憑證（CA 簽名）       |  確認憑證是可信的
   |── 5. 交換金鑰 ───────────────>|  協商出一個對稱金鑰
   |<══════ 加密通訊開始 ══════════>|  之後都用對稱加密
```

**憑證（Certificate）是什麼：**
憑證是由 CA（Certificate Authority，憑證授權機構）簽發的「身份證」，證明這個網域確實屬於這個組織。瀏覽器內建了一份信任的 CA 清單，如果憑證是這些 CA 簽的，就顯示綠色鎖頭。

**實作：用 Let's Encrypt 免費取得 SSL 憑證**
```bash
# 安裝 certbot（Let's Encrypt 的工具）
sudo apt install certbot python3-certbot-nginx

# 自動取得憑證並設定 nginx
sudo certbot --nginx -d example.com -d www.example.com

# certbot 會自動修改 nginx 設定，加上 SSL 相關設定
# 憑證有效期 90 天，certbot 會自動續期

# 手動續期（測試用）
sudo certbot renew --dry-run
```

**在 AWS 的對應：**
```
AWS Certificate Manager（ACM）
    ↓ 免費提供 SSL 憑證
ALB / CloudFront / API Gateway
    ↓ 自動掛上憑證，處理 HTTPS
後端 EC2 / ECS（只需處理 HTTP）
```

```bash
# 用 AWS CLI 申請 ACM 憑證
aws acm request-certificate \
  --domain-name example.com \
  --subject-alternative-names "*.example.com" \
  --validation-method DNS

# 之後在 Route 53 加上驗證用的 DNS 記錄，ACM 就會自動核發憑證
```

**HTTP vs HTTPS 的差別：**
| | HTTP | HTTPS |
|--|------|-------|
| 傳輸 | 明文 | 加密（TLS）|
| Port | 80 | 443 |
| 速度 | 稍快 | 稍慢（握手有開銷，但現代硬體幾乎感覺不到）|
| SEO | 較差 | Google 優先排名 |
| 現代標準 | 不建議 | 必須 |

**常見的 SSL 相關名詞：**
- **憑證（Certificate / Cert）**：伺服器的身份證明文件
- **私鑰（Private Key）**：只有伺服器自己知道，用來解密
- **CA（Certificate Authority）**：簽發憑證的機構，如 Let's Encrypt、DigiCert
- **SNI（Server Name Indication）**：讓一台伺服器用同一個 IP 服務多個不同域名的 HTTPS

---

**Lua**

Lua 是一個輕量、快速、可嵌入的腳本語言，設計目標是被嵌入到其他程式裡使用，而不是獨立運行。它的語法簡單，執行速度快，記憶體佔用小，所以常被用在遊戲引擎、嵌入式系統、和高效能伺服器軟體裡。

**為什麼在 nginx / OpenResty 裡用 Lua：**
nginx 本身只能用設定檔語法，邏輯能力有限。把 Lua 嵌入 nginx（也就是 OpenResty 做的事），就能在 nginx 的請求處理流程裡寫完整的程式邏輯，而不需要另外起一個 App Server。

**Lua 基本語法：**
```lua
-- 這是註解（用 -- 開頭）

-- 變數（不需要宣告型別）
local name = "neo"
local age = 25
local is_admin = true

-- 字串串接用 ..
print("Hello, " .. name)

-- if / else
if age >= 18 then
    print("成年")
elseif age >= 13 then
    print("青少年")
else
    print("兒童")
end

-- 迴圈
for i = 1, 5 do
    print(i)
end

-- table（Lua 的核心資料結構，同時是 array 和 dictionary）
local fruits = {"apple", "banana", "orange"}   -- array
print(fruits[1])   -- Lua 的 index 從 1 開始（不是 0！）

local person = {name = "neo", age = 25}        -- dictionary
print(person.name)

-- 函式
local function add(a, b)
    return a + b
end
print(add(3, 4))   -- 7
```

**在 OpenResty（nginx）裡的 Lua：**
```nginx
server {
    listen 8080;

    location /hello {
        content_by_lua_block {
            -- 這段 Lua 程式碼在 nginx 處理請求時執行
            local name = ngx.var.arg_name or "World"
            ngx.say("Hello, " .. name .. "!")
            -- 訪問 /hello?name=Neo 會回傳 "Hello, Neo!"
        }
    }

    location /check-token {
        access_by_lua_block {
            -- 在請求進入前做認證
            local token = ngx.req.get_headers()["Authorization"]
            if not token then
                ngx.status = 401
                ngx.say('{"error": "Missing token"}')
                return ngx.exit(401)
            end
            -- 通過認證，繼續處理請求
        }
        proxy_pass http://backend:8000;
    }
}
```

**Lua 的特色：**
| 特色 | 說明 |
|------|------|
| 輕量 | 整個直譯器只有幾百 KB |
| 快速 | LuaJIT 的速度接近 C |
| 可嵌入 | 設計來被嵌入 C/C++ 程式裡 |
| 簡單 | 語法規則少，容易學 |
| index 從 1 開始 | 跟大多數語言不同，常見踩坑點 |

**常見使用場景：**
- **遊戲**：World of Warcraft 的插件、Roblox 的腳本都是 Lua
- **OpenResty / Kong**：在 nginx 裡寫業務邏輯
- **Redis**：Redis 支援用 Lua 腳本做原子性操作
- **嵌入式系統**：路由器韌體（如 OpenWrt）

**Redis 裡用 Lua 的例子：**
```python
import redis

r = redis.Redis()

# 用 Lua 腳本做原子性的「檢查再設定」操作
# 這樣不會有 race condition
lua_script = """
local current = redis.call('GET', KEYS[1])
if current == false then
    redis.call('SET', KEYS[1], ARGV[1])
    return 1
else
    return 0
end
"""

result = r.eval(lua_script, 1, "my_key", "my_value")
print(result)  # 1 = 設定成功，0 = key 已存在
```

---

## 0513

**可以被執行的東西，電腦的邏輯**

電腦本質上只做一件事：執行指令。所謂「可以被執行的東西」，就是符合 CPU 能理解的格式的二進位指令序列（機器碼）。從你寫的 Python 程式到 shell script，最終都要被翻譯成 CPU 能執行的 0 和 1。

**電腦執行的層次：**
```
你寫的程式碼（Python / JavaScript / C）
    ↓ 編譯器 / 直譯器
組合語言（Assembly）
    ↓ 組譯器（Assembler）
機器碼（0 和 1，CPU 直接執行）
```

**什麼東西「可以被執行」：**

| 類型 | 說明 | 例子 |
|------|------|------|
| 可執行檔（binary） | 已編譯成機器碼，CPU 直接跑 | `/usr/bin/python3`、`./my-app` |
| Shell Script | 由 shell 直譯，一行一行執行 | `#!/bin/bash` 開頭的 `.sh` 檔 |
| 直譯語言程式 | 由直譯器翻譯後執行 | Python、JavaScript、Ruby |
| Bytecode | 編譯成中間格式，由 VM 執行 | Java `.class` 檔、Python `.pyc` |

**電腦執行的核心邏輯（Fetch-Decode-Execute Cycle）：**
```
1. Fetch（取指令）：CPU 從記憶體讀取下一條指令
2. Decode（解碼）：CPU 解析這條指令要做什麼
3. Execute（執行）：CPU 實際執行（加法、比較、跳轉等）
4. 回到步驟 1，無限循環
```

**實作：讓一個檔案「可以被執行」**
```bash
# 寫一個 Python script
cat > hello.py << 'EOF'
#!/usr/bin/env python3
print("Hello, World!")
EOF

# 預設沒有執行權限
ls -la hello.py
# -rw-r--r--  hello.py   ← 沒有 x（execute）權限

# 加上執行權限
chmod +x hello.py

ls -la hello.py
# -rwxr-xr-x  hello.py   ← 有 x 了

# 現在可以直接執行
./hello.py
# Hello, World!
```

**為什麼需要 `./`：**
Shell 不會在當前目錄找可執行檔（安全考量），必須明確指定路徑。`./` 代表「當前目錄」。

**電腦邏輯的本質：**
所有程式，不管多複雜，最終都只是這幾種基本操作的組合：
- **運算**：加減乘除、位元運算
- **比較**：大於、小於、等於
- **跳轉**：if/else、迴圈（改變下一條要執行的指令位置）
- **記憶體存取**：讀取和寫入資料

---

**Imperative vs Declarative（命令式 vs 宣告式）**

這是兩種截然不同的程式設計或系統描述風格，核心差別在於：你是在告訴電腦「**怎麼做**」還是「**做什麼**」。

**命令式（Imperative）：告訴電腦每一步怎麼做**
你明確描述執行的步驟和順序，電腦照著你說的一步一步執行。

**宣告式（Declarative）：告訴電腦你要的結果是什麼**
你描述「期望的最終狀態」，讓工具自己決定怎麼達到那個狀態。

**用 Terraform vs Shell Script 的差別來理解：**

```bash
# ❶ 命令式（Shell Script）：你要告訴它每一步怎麼做
#!/bin/bash

# 先檢查 VPC 存不存在
VPC_ID=$(aws ec2 describe-vpcs --filters "Name=tag:Name,Values=my-vpc" \
  --query "Vpcs[0].VpcId" --output text)

if [ "$VPC_ID" == "None" ]; then
  # 不存在才建立
  VPC_ID=$(aws ec2 create-vpc --cidr-block 10.0.0.0/16 \
    --query "Vpc.VpcId" --output text)
  aws ec2 create-tags --resources $VPC_ID --tags Key=Name,Value=my-vpc
fi

# 再檢查 Subnet 存不存在
SUBNET_ID=$(aws ec2 describe-subnets --filters "Name=tag:Name,Values=my-subnet" \
  --query "Subnets[0].SubnetId" --output text)

if [ "$SUBNET_ID" == "None" ]; then
  SUBNET_ID=$(aws ec2 create-subnet --vpc-id $VPC_ID \
    --cidr-block 10.0.1.0/24 --query "Subnet.SubnetId" --output text)
  # ... 以此類推，每一步都要自己處理
fi
```

```hcl
# ❷ 宣告式（Terraform）：你只描述「我要什麼」
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
  tags = { Name = "my-vpc" }
}

resource "aws_subnet" "main" {
  vpc_id     = aws_vpc.main.id
  cidr_block = "10.0.1.0/24"
}

# Terraform 自己決定：
# - 這些資源存不存在？
# - 要建立、更新還是刪除？
# - 執行順序是什麼？
```

**更多對比範例：**

```python
# 命令式：過濾偶數
numbers = [1, 2, 3, 4, 5, 6]
evens = []
for n in numbers:
    if n % 2 == 0:
        evens.append(n)

# 宣告式：過濾偶數（list comprehension / filter）
evens = [n for n in numbers if n % 2 == 0]
evens = list(filter(lambda n: n % 2 == 0, numbers))
```

```sql
-- SQL 是宣告式的典型例子
-- 你只說「我要什麼」，資料庫自己決定怎麼查
SELECT name, age FROM users WHERE age > 25 ORDER BY age;
-- 你不需要告訴資料庫要用哪個 index、怎麼排序、怎麼掃描
```

**兩種風格的比較：**

| | 命令式 | 宣告式 |
|--|--------|--------|
| 描述 | 怎麼做（步驟）| 做什麼（結果）|
| 例子 | Shell Script、Python for loop | Terraform、SQL、HTML、React |
| 優點 | 完全掌控執行細節 | 簡潔、可讀性高、工具幫你優化 |
| 缺點 | 冗長、需要處理邊界情況 | 除錯較難、需要信任工具 |
| 冪等性 | 需要自己實作 | 通常內建（Terraform plan/apply）|

**Terraform 宣告式的核心優勢：**
```bash
# 第一次執行：建立所有資源
terraform apply   # 建立 VPC、Subnet、EC2...

# 第二次執行（什麼都沒改）：什麼都不做
terraform apply   # No changes. Infrastructure is up-to-date.

# 修改了某個設定後執行：只更新有差異的部分
terraform apply   # 只修改那個資源，其他不動
```
這就是宣告式的冪等性：你描述「期望狀態」，工具負責讓現實符合期望，不管現在狀態是什麼。

---

**terraform state list / state rm / target**

Terraform 的 state 是它追蹤「現實世界資源狀態」的核心機制。這三個指令都是用來操作或查看這個 state 的。

**什麼是 Terraform State：**
Terraform 在 `terraform.tfstate` 檔案（或遠端 backend）裡記錄它管理的每個資源的當前狀態。每次 `terraform apply`，它會比對 state 和你的設定檔，決定要新增、修改還是刪除什麼。

**terraform state list（列出所有被管理的資源）**

```bash
# 列出 state 裡所有資源
terraform state list

# 輸出範例：
# aws_vpc.main
# aws_subnet.public[0]
# aws_subnet.public[1]
# aws_subnet.private[0]
# aws_instance.web
# aws_security_group.web_sg
# module.rds.aws_db_instance.main

# 過濾特定資源
terraform state list | grep aws_subnet
terraform state list | grep module.rds
```

**terraform state rm（從 state 移除資源，但不刪除實際資源）**

```bash
# 把某個資源從 Terraform 管理中移除
# 注意：只是讓 Terraform「忘記」這個資源，實際的 AWS 資源不會被刪除
terraform state rm aws_instance.web

# 移除整個 module
terraform state rm module.rds

# 使用情境：
# 1. 你想手動管理某個資源，不讓 Terraform 碰它
# 2. 資源已經被手動刪除，但 state 裡還有記錄，造成 apply 報錯
# 3. 把資源從一個 Terraform 設定移到另一個設定管理
```

**terraform target（只對特定資源執行 plan/apply）**

```bash
# 只 plan 特定資源
terraform plan -target=aws_instance.web

# 只 apply 特定資源（不影響其他資源）
terraform apply -target=aws_instance.web

# 可以指定多個 target
terraform apply \
  -target=aws_instance.web \
  -target=aws_security_group.web_sg

# 指定 module
terraform apply -target=module.rds
```

**什麼時候用 -target：**
```bash
# 情境 1：只想先建立某個資源，其他的之後再說
terraform apply -target=aws_vpc.main
terraform apply -target=aws_subnet.public  # 等 VPC 建好再建 subnet

# 情境 2：大型設定檔，只想測試某個部分
terraform plan -target=module.new_feature

# 情境 3：緊急修復，只想更新某個資源，不想動其他的
terraform apply -target=aws_security_group.web_sg
```

**⚠️ 注意事項：**
```bash
# -target 是緊急工具，不建議常規使用
# 因為它可能讓 state 和實際設定不一致
# Terraform 官方建議：如果常常需要用 -target，代表你的設定檔需要重構

# 正確的做法是把設定拆成更小的模組或獨立的 state
```

**三個指令的使用場景總結：**

| 指令 | 用途 | 注意 |
|------|------|------|
| `state list` | 查看 Terraform 管理哪些資源 | 只讀，安全 |
| `state rm` | 讓 Terraform 忘記某個資源 | 不刪實際資源，但之後 apply 可能重建 |
| `-target` | 只操作特定資源 | 緊急用，避免常規使用 |

---

**Race Condition（競態條件）**

Race Condition 是指程式的行為取決於多個操作的**執行順序**，而這個順序是不確定的（取決於 CPU 排程、網路延遲等），導致有時結果正確、有時結果錯誤，難以重現和除錯。

**直觀理解：**
兩個人同時看到銀行帳戶有 1000 元，都決定提領 800 元。如果系統沒有保護機制，兩個人都通過了「餘額 >= 800」的檢查，最後帳戶變成 -600 元。

**程式碼範例：**

```python
import threading

# 有 Race Condition 的版本
balance = 1000

def withdraw(amount):
    global balance
    if balance >= amount:          # ← 步驟 1：檢查餘額
        # 如果兩個 thread 同時到這裡，都看到 balance = 1000
        balance = balance - amount  # ← 步驟 2：扣款（可能被另一個 thread 覆蓋）
        print(f"提領 {amount}，餘額：{balance}")
    else:
        print(f"餘額不足，無法提領 {amount}")

# 兩個 thread 同時提領
t1 = threading.Thread(target=withdraw, args=(800,))
t2 = threading.Thread(target=withdraw, args=(800,))
t1.start()
t2.start()
t1.join()
t2.join()
# 可能輸出：
# 提領 800，餘額：200
# 提領 800，餘額：-600  ← Race Condition！
```

```python
import threading

# 用 Lock 解決 Race Condition
balance = 1000
lock = threading.Lock()

def withdraw_safe(amount):
    global balance
    with lock:                     # ← 同一時間只有一個 thread 能進入
        if balance >= amount:
            balance = balance - amount
            print(f"提領 {amount}，餘額：{balance}")
        else:
            print(f"餘額不足，無法提領 {amount}")

t1 = threading.Thread(target=withdraw_safe, args=(800,))
t2 = threading.Thread(target=withdraw_safe, args=(800,))
t1.start()
t2.start()
t1.join()
t2.join()
# 正確輸出：
# 提領 800，餘額：200
# 餘額不足，無法提領 800
```

**在資料庫的 Race Condition（更常見）：**

```sql
-- 有問題的版本（兩個 transaction 同時執行）
-- Transaction A                    Transaction B
SELECT balance FROM accounts        SELECT balance FROM accounts
WHERE id = 1;  -- 得到 1000        WHERE id = 1;  -- 也得到 1000

UPDATE accounts SET balance = 200   UPDATE accounts SET balance = 200
WHERE id = 1;                       WHERE id = 1;
-- 兩個都成功，但應該只有一個能成功！
```

```sql
-- 解法 1：SELECT FOR UPDATE（悲觀鎖）
BEGIN;
SELECT balance FROM accounts WHERE id = 1 FOR UPDATE;
-- 其他 transaction 想讀這行會被阻塞，直到這個 transaction 結束
UPDATE accounts SET balance = balance - 800 WHERE id = 1;
COMMIT;

-- 解法 2：樂觀鎖（用版本號）
UPDATE accounts
SET balance = balance - 800, version = version + 1
WHERE id = 1 AND version = 5;  -- 只有 version 還是 5 才更新
-- 如果另一個 transaction 先更新了，version 變成 6，這個 UPDATE 影響 0 行
-- 應用層檢查影響行數，如果是 0 就重試
```

**在 AWS / 分散式系統的 Race Condition：**

```python
import boto3

# 有問題：兩個 Lambda 同時讀取並更新 DynamoDB
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("inventory")

def decrement_stock(item_id, quantity):
    # 讀取
    response = table.get_item(Key={"item_id": item_id})
    current_stock = response["Item"]["stock"]

    # 如果兩個 Lambda 同時讀到 stock = 5，都通過了這個檢查
    if current_stock >= quantity:
        # 兩個都寫入，最後 stock 可能是負數
        table.update_item(
            Key={"item_id": item_id},
            UpdateExpression="SET stock = :new_stock",
            ExpressionAttributeValues={":new_stock": current_stock - quantity}
        )
```

```python
# 正確：用 DynamoDB 的條件表達式（原子操作）
def decrement_stock_safe(item_id, quantity):
    try:
        table.update_item(
            Key={"item_id": item_id},
            UpdateExpression="SET stock = stock - :qty",
            ConditionExpression="stock >= :qty",  # 原子性地檢查並更新
            ExpressionAttributeValues={":qty": quantity}
        )
    except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
        print("庫存不足")
```

**Race Condition 的常見解法：**

| 解法 | 說明 | 適用場景 |
|------|------|---------|
| Mutex / Lock | 同一時間只有一個 thread 能執行 | 單機多執行緒 |
| 資料庫鎖（FOR UPDATE）| 鎖定資料庫行 | 資料庫操作 |
| 樂觀鎖（版本號）| 更新時檢查版本，失敗就重試 | 衝突少的場景 |
| 原子操作 | 讀取和更新在一個不可分割的操作裡完成 | Redis、DynamoDB |
| 訊息佇列（SQS）| 把操作序列化，一次只處理一個 | 分散式系統 |

---

**du（Disk Usage，磁碟使用量）**

`du` 是 Linux/macOS 的指令，用來查看**檔案或目錄佔用了多少磁碟空間**。名稱來自 "Disk Usage"。

**基本用法：**

```bash
# 查看當前目錄的磁碟使用量（預設以 512-byte block 為單位，不直觀）
du

# 用人類可讀的格式（KB、MB、GB）
du -h

# 只顯示總計（不列出每個子目錄）
du -sh /path/to/directory
# 例：du -sh /var/log
# 輸出：2.3G    /var/log

# 查看當前目錄下每個子目錄的大小，並排序
du -sh * | sort -h
# 輸出：
# 4.0K    config.yml
# 128K    scripts
# 1.2M    logs
# 3.4G    data

# 只顯示到第 1 層深度（不遞迴展開）
du -h --max-depth=1 /var
# macOS 用 -d 1
du -h -d 1 /var
```

**常用選項：**

```bash
# -s：只顯示總計（summarize）
du -sh /home/user

# -h：人類可讀格式（human-readable）
du -h /var/log

# -c：最後加上總計行
du -sh /var/log /tmp -c
# 輸出：
# 2.3G    /var/log
# 512M    /tmp
# 2.8G    total

# --exclude：排除特定目錄
du -sh /home --exclude=".git"

# 找出最大的目錄（常用的排查技巧）
du -h /var | sort -rh | head -20
```

**du vs df 的差別：**

```bash
# du：查看「某個目錄/檔案」佔用多少空間
du -sh /var/log    # /var/log 這個目錄用了多少

# df：查看「整個磁碟/分割區」的使用狀況
df -h
# 輸出：
# Filesystem      Size  Used Avail Use% Mounted on
# /dev/xvda1       20G   15G  4.5G  77% /
# tmpfs           2.0G     0  2.0G   0% /dev/shm
```

**實際使用情境：**

```bash
# 情境 1：磁碟快滿了，找出哪個目錄最大
df -h          # 先確認哪個分割區快滿
du -h / --max-depth=2 2>/dev/null | sort -rh | head -20
# 找出最佔空間的目錄

# 情境 2：清理 Docker 前先看看佔了多少
du -sh /var/lib/docker

# 情境 3：查看 log 目錄有多大
du -sh /var/log/*

# 情境 4：在 CI/CD 裡監控 build artifact 大小
BUILD_SIZE=$(du -sb ./dist | cut -f1)
echo "Build size: $BUILD_SIZE bytes"
if [ $BUILD_SIZE -gt 104857600 ]; then  # 100MB
    echo "Warning: Build size exceeds 100MB"
fi
```

**在 AWS EC2 上的常見用法：**

```bash
# EC2 磁碟快滿時的排查流程
df -h                          # 1. 確認哪個分割區快滿
du -h / -d 2 2>/dev/null | sort -rh | head -20  # 2. 找最大的目錄
du -sh /var/log/*              # 3. 通常是 log 太大
sudo journalctl --disk-usage   # 4. 查看 systemd journal 佔用
sudo journalctl --vacuum-size=500M  # 5. 清理 journal，只保留 500MB
```

**與相關指令的關聯：**
- `df`：看整個磁碟的使用率（disk free）
- `ls -lh`：看單個檔案的大小
- `du`：看目錄樹的磁碟使用量（disk usage）
- `ncdu`：互動式的 du，更好用（需要安裝：`brew install ncdu`）

```bash
# ncdu 是 du 的互動式版本，可以用方向鍵瀏覽
ncdu /var
# 會顯示一個互動介面，讓你一層一層往下找最大的目錄
```

---

**Bundle（打包）**

Bundle 是把多個檔案、模組、或依賴項目**打包成一個（或少數幾個）輸出檔案**的過程。目的是讓程式更容易分發、部署，或讓瀏覽器載入更有效率。

**為什麼需要 Bundle：**
現代前端專案可能有幾百個 JavaScript 模組，如果瀏覽器要一個一個請求，會發出幾百個 HTTP 請求，速度很慢。Bundle 工具把這些模組合併成一個或幾個檔案，大幅減少請求數。

**不同情境下的 Bundle：**

```
前端（JavaScript）：
  src/
  ├── index.js
  ├── utils.js
  ├── components/Button.js
  └── node_modules/（幾千個檔案）
        ↓ webpack / vite / esbuild
  dist/
  └── bundle.js（一個檔案，包含所有程式碼）
```

```
Python 應用部署：
  app/
  ├── main.py
  ├── requirements.txt
  └── ...
        ↓ PyInstaller / Docker
  my-app（可執行檔，包含 Python 直譯器和所有依賴）
  或
  Docker Image（包含 OS、Python、所有套件）
```

**常見的 Bundle 工具：**

| 工具 | 語言/用途 | 說明 |
|------|----------|------|
| webpack | JavaScript | 最老牌，功能最完整 |
| Vite | JavaScript | 現代前端，開發時超快 |
| esbuild | JavaScript | 用 Go 寫的，速度極快 |
| PyInstaller | Python | 把 Python 程式打包成可執行檔 |
| Docker | 任何語言 | 把應用和環境一起打包成 Image |

**在 AWS 的情境：**
```bash
# Lambda 部署包就是一種 bundle
# 把你的程式碼和依賴打包成 zip
pip install -r requirements.txt -t ./package
cd package && zip -r ../lambda.zip .
cd .. && zip lambda.zip lambda_function.py

# 上傳到 Lambda
aws lambda update-function-code \
  --function-name my-function \
  --zip-file fileb://lambda.zip
```

**Bundle 的相關概念：**
- **Tree Shaking**：打包時自動移除沒有用到的程式碼，縮小 bundle 大小
- **Code Splitting**：把 bundle 拆成多個小塊，按需載入（lazy loading）
- **Minification**：壓縮程式碼（移除空白、縮短變數名），進一步縮小大小

---

**Fine-tuning（微調）**

Fine-tuning 是在一個已經預訓練好的大型模型（Pre-trained Model）基礎上，用你自己的特定資料繼續訓練，讓模型在特定任務或領域上表現更好。

**為什麼需要 Fine-tuning：**
從頭訓練一個大型語言模型需要幾千萬美元和幾個月時間。Fine-tuning 讓你用少量資料和計算資源，把一個通用模型調整成適合你特定需求的模型。

**Fine-tuning 的概念：**
```
預訓練模型（已學會語言的通用知識）
        ↓ 用你的資料繼續訓練（通常只需要幾百到幾千筆）
Fine-tuned 模型（保留通用知識 + 學會你的特定風格/領域）
```

**什麼時候用 Fine-tuning：**
- 你需要模型用特定的語氣或格式回答（例如：客服機器人的口吻）
- 你有大量領域專業知識要讓模型學習（例如：法律文件、醫療記錄）
- 你需要模型輸出特定的結構化格式（例如：永遠輸出 JSON）
- Prompt Engineering 已經無法達到你要的效果

**Fine-tuning vs Prompt Engineering vs RAG：**

| 方法 | 說明 | 適用場景 |
|------|------|---------|
| Prompt Engineering | 用好的 prompt 引導模型 | 快速、不需要資料、效果有限 |
| RAG（檢索增強）| 查詢外部知識庫後再回答 | 需要最新資訊、大量文件 |
| Fine-tuning | 用資料重新訓練模型 | 需要特定風格、格式、或深度領域知識 |

**在 AWS 上 Fine-tuning（Bedrock）：**
```python
import boto3

bedrock = boto3.client("bedrock", region_name="us-east-1")

# 建立 Fine-tuning Job
response = bedrock.create_model_customization_job(
    jobName="my-finetune-job",
    customModelName="my-custom-model",
    roleArn="arn:aws:iam::...:role/BedrockFineTuneRole",
    baseModelIdentifier="amazon.titan-text-express-v1",
    customizationType="FINE_TUNING",
    trainingDataConfig={
        "s3Uri": "s3://my-bucket/training-data.jsonl"
    },
    outputDataConfig={
        "s3Uri": "s3://my-bucket/output/"
    }
)
```

訓練資料格式（JSONL）：
```jsonl
{"prompt": "客戶說：我的訂單在哪裡？", "completion": "您好！感謝您的詢問，我馬上幫您查詢訂單狀態..."}
{"prompt": "客戶說：我要退款", "completion": "非常抱歉造成您的不便，我們的退款流程是..."}
```

---

**開源 vs 閉源模型（Open Source vs Closed Source Models）**

AI 語言模型依照是否公開模型權重（weights），分為開源和閉源兩類。

**閉源模型（Closed Source）：**
模型的訓練資料、架構細節、和權重都不公開。你只能透過 API 呼叫，無法自己部署或修改。

| 模型 | 公司 | 存取方式 |
|------|------|---------|
| GPT-4 / GPT-4o | OpenAI | API |
| Claude 3.x | Anthropic | API / AWS Bedrock |
| Gemini | Google | API |
| Command R+ | Cohere | API |

**開源模型（Open Source）：**
模型權重公開，你可以下載、自己部署、甚至修改和 Fine-tune。

| 模型 | 公司 | 特色 |
|------|------|------|
| Llama 3 | Meta | 目前最強的開源模型之一 |
| Mistral / Mixtral | Mistral AI | 輕量但效能好 |
| Gemma | Google | 小型但高效 |
| Phi-3 | Microsoft | 小模型，適合邊緣部署 |
| Qwen | Alibaba | 多語言支援好 |

**兩者的比較：**

| | 閉源 | 開源 |
|--|------|------|
| 效能 | 通常較強（GPT-4、Claude）| 追趕中，Llama 3 已很接近 |
| 隱私 | 資料送到第三方 API | 可以完全在自己的環境跑 |
| 成本 | 按 token 計費，量大很貴 | 自己跑硬體成本，量大反而便宜 |
| 客製化 | 有限（只能 Fine-tune API）| 完全自由，可以改架構 |
| 部署 | 不需要管基礎設施 | 需要自己管 GPU 伺服器 |
| 合規 | 資料可能跨境 | 資料完全在自己掌控 |

**在 AWS 上使用開源模型：**
```python
import boto3
import json

bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

# 在 AWS Bedrock 上跑 Meta Llama 3（開源模型，但透過 AWS 託管）
response = bedrock.invoke_model(
    modelId="meta.llama3-70b-instruct-v1:0",
    body=json.dumps({
        "prompt": "<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n你好<|eot_id|>",
        "max_gen_len": 512,
        "temperature": 0.7
    })
)

result = json.loads(response["body"].read())
print(result["generation"])
```

---

**Temperature（溫度，AI 模型參數）**

Temperature 是控制 AI 語言模型**輸出隨機程度**的參數，數值通常在 0 到 1 之間（有些模型到 2）。

**直觀理解：**
- **Temperature = 0**：每次輸出幾乎相同，選擇機率最高的詞，非常確定、保守
- **Temperature = 1**：按照模型原始的機率分佈輸出，有一定隨機性
- **Temperature > 1**：更隨機、更有創意，但也更容易胡說

```
Temperature 低（0.1）：
  問：「天空是什麼顏色？」
  答：「藍色。」（每次都一樣）

Temperature 高（0.9）：
  問：「天空是什麼顏色？」
  答：「藍色，但在日落時會變成橙紅色，有時也會是灰色...」（每次可能不同）
```

**技術原理：**
模型輸出時，對每個可能的下一個詞都有一個機率分佈。Temperature 會調整這個分佈的「尖銳程度」：

```python
import numpy as np

# 假設模型對下一個詞的原始分數（logits）
logits = np.array([2.0, 1.0, 0.5, 0.1])  # 對應詞：["藍", "紅", "綠", "黃"]

def softmax_with_temperature(logits, temperature):
    scaled = logits / temperature
    exp_scaled = np.exp(scaled - np.max(scaled))
    return exp_scaled / exp_scaled.sum()

# Temperature = 0.1（非常確定）
print(softmax_with_temperature(logits, 0.1))
# [0.999, 0.001, 0.000, 0.000]  ← 幾乎只選「藍」

# Temperature = 1.0（正常）
print(softmax_with_temperature(logits, 1.0))
# [0.619, 0.228, 0.138, 0.015]  ← 主要選「藍」，偶爾選其他

# Temperature = 2.0（很隨機）
print(softmax_with_temperature(logits, 2.0))
# [0.432, 0.290, 0.220, 0.058]  ← 各詞機率更接近，更隨機
```

**實際使用建議：**

| 用途 | 建議 Temperature | 原因 |
|------|-----------------|------|
| 程式碼生成 | 0.0 ~ 0.2 | 需要精確，不要亂猜 |
| 事實問答 | 0.0 ~ 0.3 | 需要準確，不要創意 |
| 一般對話 | 0.5 ~ 0.7 | 平衡準確和自然 |
| 創意寫作 | 0.8 ~ 1.0 | 需要多樣性和創意 |
| 腦力激盪 | 0.9 ~ 1.2 | 越多樣越好 |

**在 AWS Bedrock 設定 Temperature：**
```python
import boto3
import json

bedrock = boto3.client("bedrock-runtime")

response = bedrock.invoke_model(
    modelId="anthropic.claude-3-sonnet-20240229-v1:0",
    body=json.dumps({
        "messages": [{"role": "user", "content": "幫我寫一首詩"}],
        "max_tokens": 500,
        "temperature": 0.9,   # 創意寫作用高 temperature
        "top_p": 0.9          # 另一個相關參數，控制候選詞的範圍
    })
)
```

**相關參數：**
- **Top-p（nucleus sampling）**：只從累積機率達到 p 的詞裡選，和 temperature 類似但不同機制
- **Top-k**：只從機率最高的 k 個詞裡選
- **Max tokens**：限制輸出長度

---

**Rule Source（規則來源）**

在 AI 和系統設計的語境中，Rule Source 指的是**規則或指令的來源**，決定系統的行為邊界。在 LLM 應用裡，最常見的是指 System Prompt 或 Guardrails 的規則從哪裡來、由誰定義。

**在 AWS Bedrock Guardrails 的語境：**
Rule Source 指定了 Guardrails 的規則是來自哪個設定，讓你知道某個請求被攔截是因為哪條規則觸發了。

```python
import boto3
import json

bedrock_runtime = boto3.client("bedrock-runtime")

response = bedrock_runtime.invoke_model(
    modelId="anthropic.claude-3-sonnet-20240229-v1:0",
    guardrailIdentifier="my-guardrail-id",
    guardrailVersion="1",
    body=json.dumps({
        "messages": [{"role": "user", "content": "..."}]
    })
)

# 回應裡會包含 guardrail 的觸發資訊
result = json.loads(response["body"].read())

# 如果被 guardrail 攔截，會有 amazon-bedrock-guardrailAction
if "amazon-bedrock-guardrailAction" in response.get("ResponseMetadata", {}):
    # 可以看到是哪個規則（rule source）觸發了攔截
    pass
```

**更廣義的 Rule Source 概念：**

在系統設計中，規則可以來自不同來源，各有優先順序：

```
規則來源的層次（由高到低優先）：
1. 硬編碼規則（Code）：寫死在程式裡，最高優先
2. 設定檔（Config）：可以不改程式碼就調整
3. 資料庫規則：動態載入，可以即時更新
4. 外部服務（如 Guardrails）：由第三方服務決定
5. 使用者輸入：最低優先，最不可信
```

```python
# 範例：多層規則來源
class RuleEngine:
    def check(self, request):
        # 1. 硬編碼規則（最高優先）
        if request.contains_pii():
            return "BLOCK"  # 永遠不允許，不管其他規則怎麼說

        # 2. 設定檔規則
        if request.topic in config.blocked_topics:
            return "BLOCK"

        # 3. 資料庫動態規則（可以即時更新）
        db_rules = db.get_rules_for_user(request.user_id)
        for rule in db_rules:
            if rule.matches(request):
                return rule.action

        # 4. 預設允許
        return "ALLOW"
```

---

**下個 Section 會用到什麼？（解決任務前的 Context 規劃）**

這是一種思考框架：在開始做一件事之前，先問自己「完成這個任務需要哪些 context（背景知識、資源、工具）？」，提前準備好，避免中途卡住。

**為什麼這個思維很重要：**
工程師常見的問題是「埋頭做，做到一半才發現缺少某個關鍵資訊」，導致要中斷、回頭找資料，打斷思路。提前規劃 context 可以讓工作更流暢。

**實際應用：開始寫程式前的 Context 清單**

```
任務：實作一個 API，讓用戶可以查詢訂單狀態

需要的 Context：
□ 資料庫 schema（orders 表有哪些欄位？）
□ 認證機制（這個 API 需要 JWT 還是 API Key？）
□ 現有的 API 風格（RESTful？回傳格式是什麼？）
□ 錯誤處理規範（404 怎麼回？500 怎麼回？）
□ 測試環境（有沒有測試資料庫？）
□ 部署方式（直接 push 還是要開 PR？）
```

**在 AI 應用開發的語境（LLM Context Window）：**

LLM 有 context window 的限制（能記住的對話長度有限）。在設計 AI 應用時，需要規劃「每個步驟需要哪些 context 放進 prompt」：

```python
# 不好的做法：把所有東西都塞進 context
prompt = f"""
{entire_codebase}  # 幾萬行程式碼
{all_documentation}  # 幾百頁文件
{full_conversation_history}  # 幾百輪對話
請幫我修這個 bug。
"""
# context 太長，模型注意力分散，效果反而差

# 好的做法：只放這個任務需要的 context
relevant_code = get_relevant_files(bug_description)  # 只取相關檔案
recent_history = conversation[-5:]  # 只取最近 5 輪

prompt = f"""
相關程式碼：
{relevant_code}

最近的對話：
{recent_history}

問題描述：{bug_description}
請幫我修這個 bug。
"""
```

**這個思維的 SOP：**

```
1. 描述任務：「我要做什麼？」
2. 列出需要的 context：「做這件事需要知道什麼？」
3. 確認 context 是否齊全：「哪些我已經有？哪些需要去找？」
4. 排除不需要的 context：「哪些資訊是多餘的，會造成干擾？」
5. 開始執行
```

這個思維在 AI 時代特別重要，因為你給 AI 的 context 品質直接決定輸出品質。

---

**SSE（Server-Sent Events，伺服器推送事件）**

SSE 是一種讓伺服器主動向客戶端**持續推送資料**的技術，基於 HTTP 協定，單向（伺服器 → 客戶端）。你在 ChatGPT 看到文字一個字一個字出現，背後就是 SSE。

**SSE vs WebSocket vs Polling 的差別：**

| | SSE | WebSocket | Long Polling |
|--|-----|-----------|-------------|
| 方向 | 單向（Server → Client）| 雙向 | 單向（模擬）|
| 協定 | HTTP | WS（獨立協定）| HTTP |
| 複雜度 | 簡單 | 較複雜 | 簡單但低效 |
| 自動重連 | 內建 | 需要自己實作 | 需要自己實作 |
| 適用場景 | 即時通知、串流輸出 | 聊天室、遊戲 | 相容性要求高 |

**SSE 的資料格式：**

```
HTTP Response Headers:
  Content-Type: text/event-stream
  Cache-Control: no-cache
  Connection: keep-alive

Response Body（持續串流）：
  data: 第一段文字\n\n
  data: 第二段文字\n\n
  data: {"type": "done"}\n\n
```

每個事件以 `data:` 開頭，兩個換行（`\n\n`）代表一個事件結束。

**FastAPI 實作 SSE（LLM 串流輸出）：**

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import asyncio
import json

app = FastAPI()

async def generate_stream(prompt: str):
    """模擬 LLM 串流輸出"""
    words = f"這是對 '{prompt}' 的回答，一個字一個字出現".split()

    for word in words:
        # SSE 格式：data: <內容>\n\n
        yield f"data: {json.dumps({'text': word + ' '})}\n\n"
        await asyncio.sleep(0.1)  # 模擬 LLM 生成延遲

    # 結束訊號
    yield f"data: {json.dumps({'done': True})}\n\n"

@app.get("/stream")
async def stream_response(prompt: str):
    return StreamingResponse(
        generate_stream(prompt),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"  # 告訴 nginx 不要緩衝
        }
    )
```

**前端接收 SSE：**

```javascript
// 瀏覽器原生支援 EventSource
const eventSource = new EventSource('/stream?prompt=你好');

eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);

    if (data.done) {
        eventSource.close();  // 關閉連線
        return;
    }

    // 把文字 append 到畫面上
    document.getElementById('output').textContent += data.text;
};

eventSource.onerror = (error) => {
    console.error('SSE error:', error);
    eventSource.close();
};
```

**用 AWS Bedrock 做真實的 LLM 串流：**

```python
import boto3
import json
from fastapi.responses import StreamingResponse

bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

async def stream_bedrock(prompt: str):
    response = bedrock.invoke_model_with_response_stream(
        modelId="anthropic.claude-3-sonnet-20240229-v1:0",
        body=json.dumps({
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1000
        })
    )

    for event in response["body"]:
        chunk = json.loads(event["chunk"]["bytes"])
        if chunk["type"] == "content_block_delta":
            text = chunk["delta"].get("text", "")
            if text:
                yield f"data: {json.dumps({'text': text})}\n\n"

    yield f"data: {json.dumps({'done': True})}\n\n"

@app.get("/chat")
async def chat(prompt: str):
    return StreamingResponse(
        stream_bedrock(prompt),
        media_type="text/event-stream"
    )
```

**nginx 設定（避免緩衝造成串流延遲）：**

```nginx
location /stream {
    proxy_pass http://backend:8000;
    proxy_buffering off;          # 關閉緩衝，讓資料即時傳到客戶端
    proxy_cache off;
    proxy_set_header Connection '';
    proxy_http_version 1.1;
    chunked_transfer_encoding on;
}
```

**SSE 的限制：**
- 只能伺服器推送，客戶端無法透過同一個連線回傳資料
- 瀏覽器對同一個 domain 的 SSE 連線數有限制（HTTP/1.1 約 6 個）
- 需要伺服器保持長連線，高並發時要注意資源消耗

---

## 0517

**Integration Test（整合測試）**

整合測試是在「單元測試」之上的一層測試，目的是驗證多個元件**組合在一起**時能否正確運作。單元測試只測一個函式或類別，整合測試則測「這個 API endpoint 呼叫資料庫、呼叫外部服務，整個流程跑起來是否正確」。

**測試金字塔：**
```
        /\
       /  \
      / E2E \        ← 最少，最慢，最貴（模擬真實使用者）
     /--------\
    / Integration\   ← 中間層，測元件之間的協作
   /--------------\
  /   Unit Tests   \ ← 最多，最快，最便宜（測單一函式）
 /------------------\
```

**單元測試 vs 整合測試的差別：**

| | 單元測試 | 整合測試 |
|--|---------|---------|
| 測試範圍 | 單一函式/類別 | 多個元件協作 |
| 外部依賴 | 全部 mock 掉 | 使用真實或接近真實的依賴 |
| 速度 | 非常快（毫秒）| 較慢（秒級）|
| 目的 | 邏輯正確性 | 元件間介面正確性 |

**FastAPI 整合測試範例：**
```python
# tests/test_integration.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import get_db, Base

# 使用測試用的 SQLite 資料庫（不影響正式資料）
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(bind=engine)

# 覆蓋 dependency，讓 app 使用測試資料庫
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)   # 建立資料表
    yield
    Base.metadata.drop_all(bind=engine)     # 測試後清除

client = TestClient(app)

def test_create_and_get_user():
    # 整合測試：測試「建立用戶」→「查詢用戶」整個流程
    # 1. 建立用戶
    response = client.post("/users", json={"name": "Neo", "email": "neo@example.com"})
    assert response.status_code == 201
    user_id = response.json()["id"]

    # 2. 查詢剛建立的用戶（測試資料庫寫入是否成功）
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Neo"
```

**整合測試的策略：**
- 使用 in-memory 資料庫（SQLite）或 Docker 起一個測試用的 PostgreSQL
- 每個測試前後清空資料，確保測試之間互不影響
- 不需要 mock 所有東西，但外部 API（第三方服務）通常還是要 mock

---

**FastAPI TestClient 的用法**

`TestClient` 是 FastAPI（底層用 Starlette）提供的測試工具，讓你在不啟動真實 HTTP server 的情況下，直接對 FastAPI app 發送請求，用於撰寫整合測試。

**底層原理：**
TestClient 使用 `httpx` 或 `requests` 的 transport 層，直接把請求送進 ASGI app，繞過網路層，所以速度很快，也不需要佔用 port。

**基本用法：**
```python
from fastapi import FastAPI
from fastapi.testclient import TestClient

app = FastAPI()

@app.get("/hello")
def hello(name: str = "World"):
    return {"message": f"Hello, {name}!"}

@app.post("/items")
def create_item(item: dict):
    return {"id": 1, **item}

# 建立 TestClient
client = TestClient(app)

def test_hello():
    response = client.get("/hello")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, World!"}

def test_hello_with_name():
    response = client.get("/hello", params={"name": "Neo"})
    assert response.json() == {"message": "Hello, Neo!"}

def test_create_item():
    response = client.post("/items", json={"name": "book", "price": 99})
    assert response.status_code == 200
    assert response.json()["name"] == "book"
```

**測試需要認證的 endpoint：**
```python
def test_protected_endpoint():
    # 帶上 Authorization header
    response = client.get(
        "/protected",
        headers={"Authorization": "Bearer my-test-token"}
    )
    assert response.status_code == 200
```

**測試非同步 endpoint（async def）：**
TestClient 內部會自動處理 async，你不需要在測試裡用 `await`，直接呼叫就好：
```python
@app.get("/async-data")
async def get_async_data():
    # 即使是 async endpoint，TestClient 也能直接測
    return {"data": "async result"}

def test_async_endpoint():
    response = client.get("/async-data")   # 不需要 await
    assert response.status_code == 200
```

**用 pytest fixture 管理 client 生命週期：**
```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c   # 使用 context manager 確保 lifespan 事件（startup/shutdown）被觸發

def test_something(client):
    response = client.get("/")
    assert response.status_code == 200
```

---

**MockWorkflow 的概念**

MockWorkflow 是一種測試設計模式，在整合測試或單元測試中，用一個「假的工作流程實作」來替換真實的工作流程，讓測試可以在不依賴外部系統（資料庫、第三方 API、訊息佇列）的情況下驗證業務邏輯。

**為什麼需要 MockWorkflow：**
真實的 Workflow 可能會：
- 呼叫外部 API（慢、不穩定、有費用）
- 寫入資料庫（需要清理、可能影響其他測試）
- 觸發非同步任務（難以在測試中等待結果）

MockWorkflow 把這些副作用全部替換成可預測的假行為。

**實作範例：**
```python
# app/workflows/order_workflow.py
class OrderWorkflow:
    async def process_payment(self, order_id: str, amount: float) -> dict:
        # 真實實作：呼叫金流 API
        result = await payment_gateway.charge(order_id, amount)
        return result

    async def send_confirmation_email(self, email: str, order_id: str):
        # 真實實作：呼叫 SES 發信
        await ses_client.send_email(email, f"訂單 {order_id} 確認")

# tests/mocks/mock_order_workflow.py
class MockOrderWorkflow:
    def __init__(self):
        self.processed_payments = []   # 記錄被呼叫的參數，方便斷言
        self.sent_emails = []

    async def process_payment(self, order_id: str, amount: float) -> dict:
        # 假實作：直接回傳成功，不呼叫真實 API
        self.processed_payments.append({"order_id": order_id, "amount": amount})
        return {"status": "success", "transaction_id": "mock-txn-123"}

    async def send_confirmation_email(self, email: str, order_id: str):
        self.sent_emails.append({"email": email, "order_id": order_id})

# tests/test_order_service.py
import pytest
from app.services.order_service import OrderService
from tests.mocks.mock_order_workflow import MockOrderWorkflow

@pytest.fixture
def mock_workflow():
    return MockOrderWorkflow()

@pytest.fixture
def order_service(mock_workflow):
    return OrderService(workflow=mock_workflow)   # 注入 mock

async def test_place_order(order_service, mock_workflow):
    await order_service.place_order(
        order_id="order-001",
        amount=500.0,
        email="user@example.com"
    )

    # 驗證 workflow 被正確呼叫
    assert len(mock_workflow.processed_payments) == 1
    assert mock_workflow.processed_payments[0]["amount"] == 500.0
    assert mock_workflow.sent_emails[0]["email"] == "user@example.com"
```

**`workflow_mode=mock/integration` 的設計：**
有些系統會用環境變數或設定來切換 workflow 模式：
```python
import os
from app.workflows.order_workflow import OrderWorkflow
from tests.mocks.mock_order_workflow import MockOrderWorkflow

def get_workflow():
    mode = os.getenv("WORKFLOW_MODE", "integration")
    if mode == "mock":
        return MockOrderWorkflow()
    return OrderWorkflow()

# 測試時設定環境變數
# WORKFLOW_MODE=mock pytest tests/
```

---

**pytest、asyncio、AsyncMock**

這三個工具組合在一起，是 Python 非同步程式碼測試的標準配備。

**pytest**
Python 最主流的測試框架，提供 fixture、參數化測試、豐富的 assert 訊息等功能。

```bash
pip install pytest pytest-asyncio
```

**pytest-asyncio**
讓 pytest 能夠執行 `async def` 的測試函式。

```python
# pytest.ini 或 pyproject.toml 設定
[pytest]
asyncio_mode = auto   # 自動把所有 async test 當成 asyncio 測試

# 或是在每個測試加裝飾器
import pytest

@pytest.mark.asyncio
async def test_async_function():
    result = await some_async_function()
    assert result == "expected"
```

**AsyncMock**
`unittest.mock.AsyncMock` 是 Python 3.8+ 內建的工具，用來 mock `async def` 函式。普通的 `Mock` 無法被 `await`，所以需要 `AsyncMock`。

```python
from unittest.mock import AsyncMock, patch
import pytest

# 被測試的函式
async def fetch_user(user_id: str, http_client):
    response = await http_client.get(f"/users/{user_id}")
    return response.json()

# 測試
@pytest.mark.asyncio
async def test_fetch_user():
    # 建立 AsyncMock
    mock_client = AsyncMock()
    mock_client.get.return_value.json.return_value = {"id": "123", "name": "Neo"}

    result = await fetch_user("123", mock_client)

    assert result["name"] == "Neo"
    mock_client.get.assert_called_once_with("/users/123")   # 驗證呼叫參數
```

**用 `patch` 替換模組層級的 async 函式：**
```python
from unittest.mock import patch, AsyncMock

@pytest.mark.asyncio
async def test_with_patch():
    with patch("app.services.send_email", new_callable=AsyncMock) as mock_send:
        mock_send.return_value = {"status": "sent"}

        await some_service_that_calls_send_email()

        mock_send.assert_called_once()
```

**AsyncMock 的常用屬性：**
```python
mock = AsyncMock()

# 設定回傳值
mock.return_value = "result"

# 設定拋出例外
mock.side_effect = ValueError("something went wrong")

# 設定每次呼叫回傳不同值
mock.side_effect = ["first", "second", "third"]

# 驗證呼叫次數
mock.assert_called_once()
mock.assert_called_with("arg1", key="value")
print(mock.call_count)   # 被呼叫幾次
```

---

**Optimistic Locking（樂觀鎖）**

樂觀鎖是一種並發控制策略，假設「大多數情況下不會發生衝突」，所以讀取資料時不加鎖，只在**寫入時才檢查資料是否被別人改過**。如果發現衝突，就拒絕這次更新，讓呼叫方重試。

**與悲觀鎖（Pessimistic Locking）的對比：**

| | 樂觀鎖 | 悲觀鎖 |
|--|--------|--------|
| 假設 | 衝突很少發生 | 衝突很常發生 |
| 鎖定時機 | 寫入時才檢查 | 讀取時就鎖定 |
| 實作方式 | version 欄位或 timestamp | `SELECT FOR UPDATE` |
| 效能 | 高（無鎖讀取）| 較低（持有鎖期間其他人等待）|
| 適合場景 | 讀多寫少 | 寫衝突頻繁 |

**實作原理（version 欄位）：**
```sql
-- 資料表加一個 version 欄位
CREATE TABLE products (
    id      SERIAL PRIMARY KEY,
    name    VARCHAR(100),
    stock   INTEGER,
    version INTEGER DEFAULT 0   -- 每次更新 +1
);
```

```python
# 讀取時記錄 version
product = db.query("SELECT id, stock, version FROM products WHERE id = 1")
# 得到：{id: 1, stock: 100, version: 5}

# 更新時帶上 version，確保沒有人在這期間改過
rows_affected = db.execute("""
    UPDATE products
    SET stock = :new_stock, version = version + 1
    WHERE id = :id AND version = :expected_version
""", {"new_stock": 99, "id": 1, "expected_version": 5})

if rows_affected == 0:
    # version 不符合，代表有人搶先更新了
    raise OptimisticLockError("資料已被其他人修改，請重新讀取後再試")
```

**SQLAlchemy 的樂觀鎖實作：**
```python
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

class Product(Base):
    __tablename__ = "products"

    id      = Column(Integer, primary_key=True)
    name    = Column(String)
    stock   = Column(Integer)
    version = Column(Integer, default=0)

    __mapper_args__ = {
        "version_id_col": version   # 告訴 SQLAlchemy 用這個欄位做樂觀鎖
    }

# SQLAlchemy 會自動在 UPDATE 時加上 version 條件，並在衝突時拋出 StaleDataError
from sqlalchemy.orm.exc import StaleDataError

try:
    product.stock -= 1
    session.commit()
except StaleDataError:
    session.rollback()
    # 重新讀取並重試
```

**使用情境：**
- 電商庫存扣減（多人同時下單同一商品）
- 文件協作編輯（多人同時編輯同一份文件）
- 金融帳戶餘額更新

---

**EIG（Elastic IP Gateway / Egress-only Internet Gateway）**

在 AWS 語境中，EIG 通常指 **Egress-Only Internet Gateway**，是專門為 **IPv6** 設計的閘道器，讓 VPC 內的資源可以**主動對外發起連線**，但外部無法主動連進來。

**為什麼需要 Egress-Only Internet Gateway：**
IPv4 的私有 IP 靠 NAT Gateway 來上網（NAT 本身就是單向的）。但 IPv6 沒有 NAT 的概念，每個資源都有公開的 IPv6 位址，如果直接用 Internet Gateway，外部就能主動連進來，有安全疑慮。Egress-Only IGW 解決了這個問題：允許出去，但擋掉外部進來的連線。

**架構對比：**
```
IPv4 私有資源上網：
  EC2 (private IPv4) → NAT Gateway → Internet Gateway → Internet

IPv6 資源上網（只出不進）：
  EC2 (IPv6) → Egress-Only Internet Gateway → Internet
  Internet → Egress-Only IGW → ✗ 擋掉（無法主動連進來）
```

**設定方式：**
```bash
# 建立 Egress-Only Internet Gateway
aws ec2 create-egress-only-internet-gateway \
  --vpc-id vpc-xxxxxxxx

# 在 route table 加上 IPv6 的出口路由
aws ec2 create-route \
  --route-table-id rtb-xxxxxxxx \
  --destination-ipv6-cidr-block ::/0 \
  --egress-only-internet-gateway-id eigw-xxxxxxxx
```

**與 NAT Gateway 的對比：**
| | NAT Gateway | Egress-Only IGW |
|--|-------------|-----------------|
| 適用協定 | IPv4 | IPv6 |
| 方向 | 出去（NAT 轉換）| 出去（無 NAT）|
| 費用 | 有費用 | 免費 |
| 外部能否主動連入 | 不行 | 不行 |

---

**traceparent（分散式追蹤標頭）**

`traceparent` 是 W3C Trace Context 規範定義的 HTTP 標頭，用於在**分散式系統**中追蹤一個請求跨越多個服務的完整路徑。當一個請求從 Service A 呼叫 Service B 再呼叫 Service C，`traceparent` 讓你能把這三段日誌串在一起，看到完整的呼叫鏈。

**格式：**
```
traceparent: {version}-{trace-id}-{parent-id}-{flags}

例子：
traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01

- 00          : version（目前固定是 00）
- 4bf92f3...  : trace-id（16 bytes，整個請求鏈的唯一 ID）
- 00f067aa... : parent-id（8 bytes，當前這一段的 span ID）
- 01          : flags（01 = 要採樣記錄，00 = 不採樣）
```

**運作方式：**
```
用戶請求
    ↓
Service A（產生 trace-id: abc123，span-id: 111）
    ↓ 呼叫時帶上 traceparent: 00-abc123-111-01
Service B（繼承 trace-id: abc123，產生新 span-id: 222）
    ↓ 呼叫時帶上 traceparent: 00-abc123-222-01
Service C（繼承 trace-id: abc123，產生新 span-id: 333）
```

所有服務都用同一個 `trace-id`，在 Jaeger、Zipkin、AWS X-Ray 等工具裡就能把這三段日誌串成一條完整的追蹤鏈。

**Python 實作（用 opentelemetry）：**
```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor
from opentelemetry.propagate import inject, extract
import httpx

# 設定 tracer
provider = TracerProvider()
provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)

# 發送請求時自動注入 traceparent
async def call_downstream_service(url: str):
    with tracer.start_as_current_span("call-downstream"):
        headers = {}
        inject(headers)   # 自動把 traceparent 加進 headers
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
        return response

# 接收請求時提取 traceparent
from fastapi import FastAPI, Request

app = FastAPI()

@app.get("/process")
async def process(request: Request):
    # 從 incoming request 提取 trace context
    context = extract(dict(request.headers))
    with tracer.start_as_current_span("process", context=context):
        # 這個 span 會自動連結到上游的 trace
        return {"status": "processed"}
```

**在 AWS 的對應：**
- **AWS X-Ray**：AWS 的分散式追蹤服務，使用 `X-Amzn-Trace-Id` 標頭（概念相同，格式不同）
- **AWS Distro for OpenTelemetry (ADOT)**：讓你用標準的 OpenTelemetry（包含 traceparent）把追蹤資料送到 X-Ray

---

**SubAgent 是什麼**

SubAgent 是 AI Agent 系統中的一種架構模式。在一個複雜的 AI 任務中，主 Agent（Orchestrator）會把任務拆解成子任務，然後把每個子任務委派給專門的 SubAgent 去執行，最後再把結果彙整。

**為什麼需要 SubAgent：**
- 單一 Agent 的 context window 有限，複雜任務容易超出限制
- 不同子任務可以平行執行，提升效率
- 每個 SubAgent 可以專注在自己的領域（例如：一個負責寫程式碼、一個負責查文件、一個負責測試）

**架構示意：**
```
用戶請求
    ↓
Orchestrator Agent（主 Agent）
    ├── SubAgent A：負責需求分析
    ├── SubAgent B：負責程式碼生成
    ├── SubAgent C：負責測試撰寫
    └── SubAgent D：負責文件生成
    ↓
彙整結果回傳給用戶
```

**與 MCP Gateway 的關係：**
SubAgent 通常透過 MCP（Model Context Protocol）來存取工具和資源。MCP Gateway 是一個中間層，統一管理多個 MCP Server，讓 SubAgent 不需要直接連接每個工具，只需要透過 Gateway 就能存取所有工具。

```
SubAgent
    ↓
MCP Gateway（統一入口）
    ├── MCP Server: 資料庫工具
    ├── MCP Server: 檔案系統工具
    ├── MCP Server: 網路搜尋工具
    └── MCP Server: 程式碼執行工具
```

---

**MCP Gateway 是什麼**

MCP（Model Context Protocol）是 Anthropic 提出的開放協定，定義了 AI 模型如何與外部工具、資料來源互動的標準介面。MCP Gateway 則是在多個 MCP Server 前面的統一代理層。

**MCP 的核心概念：**
- **MCP Server**：提供特定工具或資源的服務（例如：一個 MCP Server 提供資料庫查詢工具）
- **MCP Client**：AI Agent，透過 MCP 協定呼叫 MCP Server 的工具
- **MCP Gateway**：聚合多個 MCP Server，提供統一的存取點、認證、路由

**MCP Gateway 解決的問題：**
```
沒有 Gateway（每個 Agent 直連每個 Server）：
Agent A ──→ DB Server
Agent A ──→ File Server
Agent A ──→ Search Server
Agent B ──→ DB Server
Agent B ──→ File Server
（連線管理複雜，認證分散）

有 Gateway（統一入口）：
Agent A ──→ MCP Gateway ──→ DB Server
Agent B ──→ MCP Gateway ──→ File Server
                         ──→ Search Server
（統一認證、路由、監控、限流）
```

**MCP Gateway 的功能：**
| 功能 | 說明 |
|------|------|
| 路由 | 根據工具名稱把請求轉發到對應的 MCP Server |
| 認證 | 統一管理 API Key，Agent 只需要一組憑證 |
| 限流 | 控制每個 Agent 的呼叫頻率 |
| 監控 | 記錄所有工具呼叫，方便除錯和審計 |
| 工具發現 | Agent 可以查詢 Gateway 知道有哪些工具可用 |

**實際使用情境：**
在 Kiro 這類 AI 開發環境中，MCP Gateway 讓 AI Agent 能夠統一存取：檔案系統、終端機、瀏覽器、資料庫等各種工具，而不需要為每個工具單獨設定連線。

---

## 0518

**CIDR（Classless Inter-Domain Routing）**

CIDR 是一種表示 IP 網段範圍的方式，格式是 `IP位址/前綴長度`，用來描述「這個網段包含哪些 IP」。

**格式說明：**
```
192.168.1.0/24

192.168.1.0  → 網段的起始 IP
/24          → 前 24 bits 是網路部分，後 8 bits 是主機部分
              → 代表這個網段有 2^8 = 256 個 IP（192.168.1.0 ～ 192.168.1.255）
```

**常見的 CIDR 大小：**

| CIDR | 可用 IP 數 | 說明 |
|------|-----------|------|
| /32 | 1 | 單一主機 |
| /24 | 256（可用 254）| 小型網段，最常見 |
| /16 | 65,536 | 中型網段 |
| /8 | 16,777,216 | 大型網段 |
| /0 | 全部 IP | `0.0.0.0/0` 代表「所有 IP」|

**`0.0.0.0/0` 的特殊意義：**
在 AWS Security Group 或 Route Table 裡，`0.0.0.0/0` 代表「任何 IP」，常用於：
- 允許所有人連進來（開放 80/443）
- 預設路由（所有流量都走這條）

**在 AWS 的實際應用：**
```
VPC CIDR：10.0.0.0/16（整個 VPC 的 IP 範圍）
  ├── Public Subnet：10.0.1.0/24（256 個 IP）
  ├── Private Subnet：10.0.2.0/24（256 個 IP）
  └── DB Subnet：10.0.3.0/24（256 個 IP）
```

```bash
# AWS CLI 建立 VPC 時指定 CIDR
aws ec2 create-vpc --cidr-block 10.0.0.0/16

# 建立 Subnet
aws ec2 create-subnet \
  --vpc-id vpc-xxxxxxxx \
  --cidr-block 10.0.1.0/24 \
  --availability-zone ap-northeast-1a
```

**判斷某個 IP 是否在某個 CIDR 內（Python）：**
```python
import ipaddress

network = ipaddress.ip_network("10.0.1.0/24")
ip = ipaddress.ip_address("10.0.1.50")

print(ip in network)   # True
print(ipaddress.ip_address("10.0.2.1") in network)   # False
```

---

**OpenTelemetry**

OpenTelemetry（簡稱 OTel）是一個開源的可觀測性（Observability）框架，提供統一的標準和工具來收集三種遙測資料：

| 資料類型 | 說明 | 例子 |
|---------|------|------|
| **Traces（追蹤）** | 一個請求跨越多個服務的完整路徑 | traceparent、span |
| **Metrics（指標）** | 數值型的效能資料 | 請求數、延遲、錯誤率 |
| **Logs（日誌）** | 事件記錄 | 錯誤訊息、操作記錄 |

**為什麼需要 OpenTelemetry：**
以前每個監控工具（Datadog、Jaeger、Zipkin、AWS X-Ray）都有自己的 SDK，換工具就要改程式碼。OpenTelemetry 提供統一的 API，你只需要寫一次，要送到哪個後端只需要換 exporter。

**架構：**
```
你的程式碼
  → OpenTelemetry SDK（收集資料）
    → Exporter（送出去）
      → Jaeger / Zipkin / AWS X-Ray / Datadog / ...
```

**Python 快速上手：**
```bash
pip install opentelemetry-api opentelemetry-sdk
pip install opentelemetry-instrumentation-fastapi
```

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, BatchSpanProcessor

provider = TracerProvider()
provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
trace.set_tracer_provider(provider)

tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("my-operation") as span:
    span.set_attribute("user.id", "123")
    span.set_attribute("request.path", "/api/orders")
    result = process_order()
    span.set_attribute("order.id", result["id"])
```

**FastAPI 自動埋點：**
```python
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from fastapi import FastAPI

app = FastAPI()
FastAPIInstrumentor.instrument_app(app)
# 之後所有 HTTP 請求都會自動產生 trace
```

**與 AWS X-Ray 的關係：**
AWS 提供 ADOT（AWS Distro for OpenTelemetry），讓你用標準的 OpenTelemetry SDK 把資料送到 X-Ray，不需要用 X-Ray 專屬的 SDK。

---

**LangGraph**

LangGraph 是 LangChain 團隊開發的框架，用來建立**有狀態的、多步驟的 AI Agent 工作流程**。它把 Agent 的執行流程建模成一個有向圖（Graph），每個節點是一個處理步驟，邊是流程的走向。

**為什麼需要 LangGraph：**
一般的 LLM 呼叫是無狀態的（問一句答一句）。但複雜的 Agent 任務需要：
- 記住之前的步驟結果
- 根據條件走不同的分支
- 在某個步驟失敗時重試或走備用路徑
- 多個 Agent 協作

**核心概念：**
- **State**：整個工作流程共享的狀態（類似一個 dict，每個節點都可以讀寫）
- **Node**：一個處理步驟（LLM 呼叫、工具呼叫、條件判斷等）
- **Edge**：節點之間的連線，決定執行順序
- **Conditional Edge**：根據狀態決定走哪條邊

**簡單範例：**
```python
from langgraph.graph import StateGraph, END
from typing import TypedDict

class AgentState(TypedDict):
    messages: list

def call_llm(state: AgentState) -> AgentState:
    response = llm.invoke(state["messages"])
    return {"messages": state["messages"] + [response]}

def use_tool(state: AgentState) -> AgentState:
    result = search_tool(state["messages"][-1])
    return {"messages": state["messages"] + [result]}

def should_use_tool(state: AgentState) -> str:
    last_message = state["messages"][-1]
    if "需要搜尋" in last_message.content:
        return "use_tool"
    return "end"

graph = StateGraph(AgentState)
graph.add_node("llm", call_llm)
graph.add_node("tool", use_tool)
graph.set_entry_point("llm")
graph.add_conditional_edges("llm", should_use_tool, {
    "use_tool": "tool",
    "end": END
})
graph.add_edge("tool", "llm")   # 用完工具再回去問 LLM

app = graph.compile()
result = app.invoke({"messages": [HumanMessage("幫我查一下今天天氣")]})
```

**與 LangChain 的關係：**
LangGraph 建立在 LangChain 之上，可以直接使用 LangChain 的 LLM、工具、記憶體等元件，但流程控制改用 Graph 管理。

---

**sse-starlette**

`sse-starlette` 是一個 Python 套件，讓你在 FastAPI（底層是 Starlette）裡輕鬆實作 **SSE（Server-Sent Events）**，也就是伺服器主動推送資料給客戶端的功能。

```bash
pip install sse-starlette
```

**基本用法：**
```python
from fastapi import FastAPI
from sse_starlette.sse import EventSourceResponse
import asyncio

app = FastAPI()

async def event_generator():
    for i in range(5):
        yield {
            "event": "message",
            "data": f"第 {i+1} 筆資料"
        }
        await asyncio.sleep(1)

@app.get("/stream")
async def stream():
    return EventSourceResponse(event_generator())
```

**實際應用：AI 串流回應**
```python
from sse_starlette.sse import EventSourceResponse
import json

async def stream_llm_response(prompt: str):
    async for chunk in llm.astream(prompt):
        yield {
            "event": "message",
            "data": json.dumps({"text": chunk.content})
        }
    yield {"event": "done", "data": json.dumps({"done": True})}

@app.post("/chat")
async def chat(request: ChatRequest):
    return EventSourceResponse(stream_llm_response(request.prompt))
```

**`EventSourceResponse` 做了什麼：**
- 自動設定 `Content-Type: text/event-stream`
- 自動設定 `Cache-Control: no-cache`
- 把你 yield 的 dict 格式化成標準 SSE 格式

---

**SSE 中的 yield**

在 SSE 的情境下，`yield` 讓 async generator 函式「吐出」一筆資料給客戶端，然後**暫停等待**，直到下一筆資料準備好再繼續。

**yield 在這裡的角色：**
```python
async def event_generator():
    yield {"data": "第一筆"}   # 吐出，客戶端立刻收到
    await asyncio.sleep(1)     # 等 1 秒
    yield {"data": "第二筆"}   # 再吐出
```

**跟一般 return 的差別：**
```python
# return：等全部算完才回傳（客戶端要等很久）
async def get_all_data():
    results = []
    for i in range(100):
        result = await slow_operation(i)
        results.append(result)
    return results   # 等 100 個都完成才回傳

# yield：每算完一個就推給客戶端（客戶端立刻看到進度）
async def stream_data():
    for i in range(100):
        result = await slow_operation(i)
        yield {"data": result}   # 算完一個就推一個
```

**yield 的暫停機制：**
每次執行到 `yield`，函式暫停，把控制權交還給 event loop。event loop 可以去處理其他請求，等客戶端準備好接收下一筆時，再回來繼續執行這個 generator。

---

**httpx**

`httpx` 是 Python 的 HTTP 客戶端套件，是 `requests` 的現代替代品，最大的差別是**支援 async**。

```bash
pip install httpx
```

**同步用法（跟 requests 幾乎一樣）：**
```python
import httpx

response = httpx.get("https://api.example.com/users")
print(response.status_code)
print(response.json())

response = httpx.post(
    "https://api.example.com/users",
    json={"name": "Neo"},
    headers={"Authorization": "Bearer my-token"}
)
```

**非同步用法（在 FastAPI / async 環境裡用這個）：**
```python
import httpx
import asyncio

async def fetch_data():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com/users")
        return response.json()

# 同時發多個請求
async def fetch_multiple():
    async with httpx.AsyncClient() as client:
        results = await asyncio.gather(
            client.get("https://api.example.com/users"),
            client.get("https://api.example.com/orders"),
        )
    return [r.json() for r in results]
```

**在測試裡用 httpx 測 FastAPI：**
```python
import pytest
import httpx
from app.main import app

@pytest.mark.asyncio
async def test_async():
    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/users")
        assert response.status_code == 200
```

**httpx vs requests：**

| | requests | httpx |
|--|----------|-------|
| async 支援 | 不支援 | 支援（AsyncClient）|
| HTTP/2 | 不支援 | 支援 |
| 語法 | - | 幾乎一樣 |
| 適合場景 | 簡單腳本 | FastAPI、async 環境 |

---

**uvicorn**

`uvicorn` 是一個高效能的 Python ASGI 伺服器，用來執行 FastAPI、Starlette 等 ASGI 框架的應用程式。

**ASGI 是什麼：**
ASGI（Asynchronous Server Gateway Interface）是 Python web 框架和伺服器之間的標準介面，支援非同步。相對於舊的 WSGI（只支援同步），ASGI 可以處理 WebSocket、SSE 等長連線。

```
客戶端請求
    ↓
uvicorn（ASGI 伺服器，處理網路連線）
    ↓
FastAPI app（你的程式碼）
    ↓
回應
```

**安裝與啟動：**
```bash
pip install uvicorn

uvicorn app.main:app                          # 基本啟動
uvicorn app.main:app --reload                 # 開發模式（自動重啟）
uvicorn app.main:app --host 0.0.0.0 --port 8080
uvicorn app.main:app --workers 4              # 多個 worker（生產環境）
```

**在程式碼裡啟動：**
```python
import uvicorn
from fastapi import FastAPI

app = FastAPI()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**uvicorn vs gunicorn：**

| | uvicorn | gunicorn |
|--|---------|----------|
| 協定 | ASGI（支援 async）| WSGI（同步）|
| 適合 | FastAPI、Starlette | Flask、Django（舊版）|
| 多進程 | 需要搭配 gunicorn | 內建 |

**生產環境常見組合：**
```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

---

**AsyncMock vs MagicMock 的差別**

這兩個都是 `unittest.mock` 裡的工具，差別在於被 mock 的函式是不是 `async def`。

**判斷要用哪個：**
- 函式定義是 `def`（同步）→ 用 `MagicMock`
- 函式定義是 `async def`（非同步）→ 用 `AsyncMock`

**MagicMock：用於同步函式**
```python
from unittest.mock import MagicMock

mock_db = MagicMock()
mock_db.get_user.return_value = {"id": 1, "name": "Neo"}

result = mock_db.get_user(1)   # 直接呼叫，不需要 await
```

**AsyncMock：用於 async 函式**
```python
from unittest.mock import AsyncMock

mock_db = AsyncMock()
mock_db.get_user.return_value = {"id": 1, "name": "Neo"}

result = await mock_db.get_user(1)   # 需要 await
```

**如果用錯會怎樣：**
```python
mock = MagicMock()
result = await mock.some_async_method()
# TypeError: object MagicMock can't be used in 'await' expression
```

**實際測試範例（同時用兩個）：**
```python
import pytest
from unittest.mock import AsyncMock, MagicMock

class UserService:
    def __init__(self, db, cache):
        self.db = db       # db.get_user 是 async
        self.cache = cache  # cache.get 是同步

    async def get_user(self, user_id: str):
        cached = self.cache.get(f"user:{user_id}")   # 同步
        if cached:
            return cached
        user = await self.db.get_user(user_id)       # async
        return user

@pytest.mark.asyncio
async def test_get_user_from_db():
    mock_cache = MagicMock()            # 同步 → MagicMock
    mock_cache.get.return_value = None  # cache miss

    mock_db = AsyncMock()               # async → AsyncMock
    mock_db.get_user.return_value = {"id": "123", "name": "Neo"}

    service = UserService(db=mock_db, cache=mock_cache)
    result = await service.get_user("123")

    assert result["name"] == "Neo"
    mock_cache.get.assert_called_once_with("user:123")
    mock_db.get_user.assert_awaited_once_with("123")   # assert_awaited，不是 assert_called
```

---

**Monorepo**

Monorepo（Monolithic Repository）是一種程式碼管理策略，把多個專案或服務的程式碼**全部放在同一個 Git repository** 裡，而不是每個服務各自一個 repo。

**Monorepo vs Polyrepo：**

| | Monorepo | Polyrepo |
|--|----------|----------|
| 結構 | 一個 repo，多個專案 | 每個專案各自一個 repo |
| 程式碼共用 | 容易，直接 import | 需要發布成套件再安裝 |
| 跨專案改動 | 一個 PR 就能改多個服務 | 需要多個 PR 協調 |
| CI/CD | 需要聰明的增量建置 | 每個 repo 獨立跑 |
| 適合 | 服務間耦合高、共用程式碼多 | 服務完全獨立、團隊各自負責 |

**典型的 Monorepo 目錄結構：**
```
my-monorepo/
├── services/
│   ├── api-gateway/        ← 服務 A
│   ├── user-service/       ← 服務 B
│   └── order-service/      ← 服務 C
├── packages/
│   ├── shared-models/      ← 共用的資料模型
│   ├── shared-utils/       ← 共用的工具函式
│   └── shared-types/       ← 共用的型別定義
├── infrastructure/
│   └── terraform/          ← 基礎設施程式碼
└── Makefile                ← 統一的建置指令
```

**Monorepo 的優點：**
- **原子性提交**：一個功能跨多個服務的改動，可以在同一個 commit 裡完成，不會有「A 服務改了但 B 服務還沒跟上」的中間狀態
- **共用程式碼容易**：`shared-models` 裡的型別定義，所有服務直接 import，不需要發布 npm/pip 套件
- **統一工具鏈**：linter、formatter、測試框架全部統一設定，不用每個 repo 各自維護

**Monorepo 的挑戰：**
- **CI/CD 要聰明**：每次 push 不能把所有服務都重新建置，要只建置有改動的部分（增量建置）
- **repo 越來越大**：clone 時間長，需要用 sparse checkout 或 shallow clone
- **權限管理複雜**：不同團隊負責不同服務，但都在同一個 repo 裡

**常見的 Monorepo 工具：**

| 工具 | 語言 | 說明 |
|------|------|------|
| Nx | JS/TS | 智慧增量建置，只跑受影響的專案 |
| Turborepo | JS/TS | Vercel 出品，快速的 pipeline 快取 |
| Bazel | 多語言 | Google 內部工具，支援大型 monorepo |
| Poetry workspaces | Python | Python 的 monorepo 套件管理 |

**在 Python 專案的實作（Poetry workspaces）：**
```
my-python-monorepo/
├── pyproject.toml
├── services/
│   ├── api/
│   │   └── pyproject.toml
│   └── worker/
│       └── pyproject.toml
└── packages/
    └── shared/
        └── pyproject.toml
```

```toml
# 根目錄 pyproject.toml
[tool.poetry.dependencies]
python = "^3.11"

[tool.poetry.group.dev.dependencies]
pytest = "^7.0"
ruff = "^0.1"
```

**知名使用 Monorepo 的公司：**
- Google：整個公司幾乎所有程式碼在一個 repo（數十億行）
- Meta：React、Jest 等都在同一個 monorepo
- Microsoft：VS Code、TypeScript 等

---

## 0519

**軟體世界的業務邏輯代表什麼？**

業務邏輯（Business Logic）是程式中「真正在做事」的那一層，也就是把現實世界的規則翻譯成程式碼的部分。它不是 HTTP 處理、不是資料庫操作、不是 UI 渲染，而是「這個系統的核心規則」。

**例子：**
- 電商系統：「庫存不足時不能下單」「滿 1000 免運費」「VIP 會員打 9 折」
- 銀行系統：「餘額不足不能轉帳」「單日轉帳上限 50 萬」
- 聊天機器人：「收到用戶訊息後，呼叫 LLM，把回應串流回去」

**為什麼要把業務邏輯獨立出來：**
如果業務邏輯混在 HTTP handler 或資料庫操作裡，會很難測試、很難重用、很難改。把它獨立成一層（Service 層），就可以：
- 單獨測試（不需要啟動 HTTP server 或連資料庫）
- 換框架時不用改（從 FastAPI 換成 Flask，業務邏輯不動）
- 多個入口共用（API 和 CLI 都呼叫同一個 Service）

```python
# 業務邏輯混在 router 裡（不好）
@app.post("/orders")
async def create_order(request: OrderRequest, db: Session):
    product = db.query(Product).get(request.product_id)
    if product.stock < request.quantity:
        raise HTTPException(400, "庫存不足")
    product.stock -= request.quantity
    order = Order(product_id=product.id, quantity=request.quantity)
    db.add(order)
    db.commit()
    return order

# 業務邏輯獨立成 Service（好）
class OrderService:
    def __init__(self, repo: OrderRepository):
        self.repo = repo

    async def create_order(self, product_id: str, quantity: int) -> Order:
        product = await self.repo.get_product(product_id)
        if product.stock < quantity:
            raise InsufficientStockError()
        product.stock -= quantity
        order = Order(product_id=product_id, quantity=quantity)
        await self.repo.save(order)
        return order
```

---

**Repo 層、Service 層（分層架構）**

軟體常見的分層架構，每一層只負責一件事：

```
Router 層（Controller）
  → 處理 HTTP 請求/回應、參數驗證、狀態碼
  → 不包含業務邏輯

Service 層
  → 業務邏輯（規則、流程、判斷）
  → 不知道 HTTP，也不知道資料庫怎麼存

Repository 層（Repo）
  → 資料存取（CRUD）
  → 只負責跟資料庫溝通
```

**為什麼要分層：**
- **可測試性**：測 Service 時 mock Repo，測 Router 時 mock Service
- **可替換性**：換資料庫只改 Repo，業務邏輯不動
- **職責清楚**：每層只做一件事，出 bug 容易定位

**實際範例：**
```python
# repository.py（Repo 層）
class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: str) -> User | None:
        return await self.db.get(User, user_id)

    async def save(self, user: User):
        self.db.add(user)
        await self.db.commit()

# service.py（Service 層）
class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def get_user(self, user_id: str) -> User:
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(user_id)
        return user

# router.py（Router 層）
@app.get("/users/{user_id}")
async def get_user(user_id: str, service: UserService = Depends()):
    user = await service.get_user(user_id)
    return UserResponse.from_entity(user)
```

---

**DRY（Don't Repeat Yourself）**

DRY 是軟體開發的核心原則之一：**不要重複自己**。如果同一段邏輯出現在兩個以上的地方，就應該抽出來成為一個函式、類別或模組。

**為什麼重複是壞事：**
- 改一個地方忘了改另一個 → bug
- 維護成本加倍
- 程式碼越來越長，越來越難讀

**DRY 的實踐：**
```python
# 違反 DRY（同樣的驗證邏輯寫了兩次）
@app.post("/orders")
async def create_order(request: OrderRequest):
    if not request.user_id:
        raise HTTPException(400, "user_id is required")
    if not request.product_id:
        raise HTTPException(400, "product_id is required")
    ...

@app.post("/returns")
async def create_return(request: ReturnRequest):
    if not request.user_id:
        raise HTTPException(400, "user_id is required")
    if not request.order_id:
        raise HTTPException(400, "order_id is required")
    ...

# 遵守 DRY（抽出共用邏輯）
def validate_required(value, field_name: str):
    if not value:
        raise HTTPException(400, f"{field_name} is required")
```

**注意：DRY 不是絕對的**
如果兩段程式碼「看起來一樣」但「原因不同」，強行合併反而會造成耦合。判斷標準是：如果其中一個改了，另一個也一定要跟著改，那才應該合併。

---

**Class（類別）**

Class 是物件導向程式設計（OOP）的核心概念，用來定義「一種東西的藍圖」，描述它有什麼屬性（資料）和什麼方法（行為）。

**直觀理解：**
- Class 是「設計圖」
- Instance（實例）是「根據設計圖蓋出來的房子」
- 你可以用同一張設計圖蓋很多間房子，每間有不同的地址和住戶

```python
# 定義 Class（設計圖）
class Dog:
    def __init__(self, name: str, breed: str):
        self.name = name      # 屬性：名字
        self.breed = breed    # 屬性：品種

    def bark(self):           # 方法：行為
        return f"{self.name} says: Woof!"

# 建立 Instance（根據設計圖蓋出來的）
my_dog = Dog(name="Lucky", breed="Golden Retriever")
your_dog = Dog(name="Max", breed="Husky")

print(my_dog.bark())    # Lucky says: Woof!
print(your_dog.bark())  # Max says: Woof!
```

**在 FastAPI 專案中的實際用法：**
```python
# Service 是一個 Class
class ChatService:
    def __init__(self, workflow, memory):
        self.workflow = workflow
        self.memory = memory

    async def execute(self, message: str):
        result = await self.workflow.run(message)
        await self.memory.save(result)
        return result

# 建立 instance 時注入依賴
service = ChatService(workflow=real_workflow, memory=real_memory)

# 測試時注入 mock
test_service = ChatService(workflow=mock_workflow, memory=mock_memory)
```

---

**Instance（實例）**

Instance 是 Class 的「具體化」，也就是根據 Class 這個藍圖建立出來的實際物件。

```python
class Car:
    def __init__(self, brand: str, color: str):
        self.brand = brand
        self.color = color

# Car 是 Class（藍圖）
# my_car 是 Instance（實際的車）
my_car = Car(brand="Toyota", color="white")
your_car = Car(brand="BMW", color="black")

# 每個 instance 有自己的屬性值
print(my_car.color)    # white
print(your_car.color)  # black

# 判斷是否為某個 Class 的 instance
print(isinstance(my_car, Car))   # True
```

**Instance vs Class 的關係：**
- Class 定義「有哪些屬性和方法」
- Instance 是「實際存在的物件，有具體的值」
- 一個 Class 可以建立無數個 Instance

---

**物件導向程式設計（OOP）**

OOP（Object-Oriented Programming）是一種程式設計範式，核心思想是把程式組織成「物件」，每個物件封裝自己的資料和行為。

**四大特性：**

| 特性 | 說明 | 例子 |
|------|------|------|
| 封裝（Encapsulation）| 把資料和操作包在一起，外部只能透過方法存取 | `user.get_name()` 而不是直接讀 `user._name` |
| 繼承（Inheritance）| 子類別繼承父類別的屬性和方法 | `Dog` 繼承 `Animal` |
| 多型（Polymorphism）| 不同類別可以有相同的方法名，但行為不同 | `cat.speak()` 和 `dog.speak()` 都叫 speak 但叫聲不同 |
| 抽象（Abstraction）| 隱藏實作細節，只暴露介面 | 你呼叫 `db.save()`，不需要知道底層是 PostgreSQL 還是 MySQL |

```python
from abc import ABC, abstractmethod

# 抽象類別（定義介面）
class NotificationService(ABC):
    @abstractmethod
    async def send(self, to: str, message: str):
        pass

# 具體實作 A
class EmailNotification(NotificationService):
    async def send(self, to: str, message: str):
        await send_email(to, message)

# 具體實作 B
class SlackNotification(NotificationService):
    async def send(self, to: str, message: str):
        await post_to_slack(to, message)

# 使用時不需要知道是哪種實作（多型）
async def notify_user(service: NotificationService, user_email: str):
    await service.send(user_email, "你的訂單已出貨")
```

---

**Python super() 用法**

`super()` 用來呼叫父類別的方法，最常見的場景是在子類別的 `__init__` 裡呼叫父類別的初始化。

**基本用法：**
```python
class Animal:
    def __init__(self, name: str):
        self.name = name

    def speak(self):
        return f"{self.name} makes a sound"

class Dog(Animal):
    def __init__(self, name: str, breed: str):
        super().__init__(name)   # 呼叫 Animal 的 __init__，設定 self.name
        self.breed = breed       # Dog 自己的屬性

    def speak(self):
        return f"{self.name} says: Woof!"

dog = Dog("Lucky", "Golden")
print(dog.name)     # Lucky（來自 Animal.__init__）
print(dog.breed)    # Golden（來自 Dog.__init__）
print(dog.speak())  # Lucky says: Woof!
```

**為什麼需要 super()：**
如果不呼叫 `super().__init__()`，父類別的初始化不會執行，`self.name` 就不會被設定。

```python
class Dog(Animal):
    def __init__(self, name: str, breed: str):
        # 忘了呼叫 super().__init__(name)
        self.breed = breed

dog = Dog("Lucky", "Golden")
print(dog.name)   # AttributeError: 'Dog' object has no attribute 'name'
```

**在 FastAPI/Pydantic 中的應用：**
```python
from pydantic import BaseModel

class BaseResponse(BaseModel):
    success: bool = True
    timestamp: str

class UserResponse(BaseResponse):
    user_id: str
    name: str
    # 自動繼承 success 和 timestamp 欄位
```

---

## 0524

**IDE（Integrated Development Environment）**

IDE 是整合開發環境，把寫程式需要的所有工具整合在一個介面裡：程式碼編輯器、終端機、除錯器、版本控制、自動補全等。

**常見的 IDE：**

| IDE | 適合語言 | 特色 |
|-----|---------|------|
| VS Code / Kiro | 多語言 | 輕量、擴充套件豐富 |
| PyCharm | Python | Python 專用，功能完整 |
| IntelliJ IDEA | Java/Kotlin | JetBrains 出品，企業級 |
| Xcode | Swift/Obj-C | Apple 開發必備 |

**IDE vs 文字編輯器的差別：**
- 文字編輯器（vim、nano）：只能編輯文字
- IDE：編輯 + 自動補全 + 除錯 + 重構 + 版本控制 + 終端機，全部整合在一起

---

**Entity（實體）**

在軟體架構中，Entity 是代表「業務核心概念」的物件，通常對應到資料庫的一筆資料，有唯一的 ID 來識別。

**Entity 的特徵：**
- 有唯一識別（ID）
- 有生命週期（建立、修改、刪除）
- 代表業務概念（User、Order、Product）

```python
# Entity 範例
from dataclasses import dataclass
from datetime import datetime

@dataclass
class User:
    id: str
    name: str
    email: str
    created_at: datetime
    updated_at: datetime

@dataclass
class Order:
    id: str
    user_id: str
    product_id: str
    quantity: int
    status: str   # pending, paid, shipped, completed
    created_at: datetime
```

**Entity vs DTO vs Model：**

| 概念 | 用途 | 位置 |
|------|------|------|
| Entity | 業務核心物件，有 ID 和行為 | Service 層 / Domain 層 |
| DTO（Data Transfer Object）| 傳輸用的資料結構，沒有行為 | Router 層（Request/Response）|
| Model | ORM 對應到資料庫表的類別 | Repository 層 |

```python
# Entity（業務核心）
class User:
    id: str
    name: str
    def change_name(self, new_name: str): ...

# DTO（API 傳輸用）
class CreateUserRequest(BaseModel):
    name: str
    email: str

class UserResponse(BaseModel):
    id: str
    name: str

# Model（ORM，對應資料庫）
class UserModel(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True)
    name = Column(String)
    email = Column(String)
```

---

**Clean Architecture（乾淨架構）**

Clean Architecture 是 Robert C. Martin（Uncle Bob）提出的架構設計原則，核心思想是：**依賴方向永遠從外層指向內層**，內層不知道外層的存在。

**同心圓架構：**
```
┌─────────────────────────────────────────────┐
│  Frameworks & Drivers（最外層）              │
│  Web 框架、資料庫、外部 API                  │
├─────────────────────────────────────────────┤
│  Interface Adapters（轉接層）                │
│  Controller、Presenter、Repository 實作      │
├─────────────────────────────────────────────┤
│  Use Cases / Application（應用層）           │
│  業務邏輯、Service                           │
├─────────────────────────────────────────────┤
│  Entities（最內層）                          │
│  核心業務物件、業務規則                       │
└─────────────────────────────────────────────┘
```

**依賴規則：箭頭只能從外指向內**
- Entity 不知道 Use Case 的存在
- Use Case 不知道 Controller 或 DB 的存在
- Controller 知道 Use Case，但不知道 DB 怎麼實作

**對應到 Python 專案：**
```
src/
├── domain/           ← Entity（最內層）
│   └── user.py       # User entity，純業務規則
├── application/      ← Use Case
│   └── create_user.py  # 業務流程
├── infrastructure/   ← 外部實作
│   ├── db/           # SQLAlchemy model、repository 實作
│   └── http/         # 外部 API client
└── presentation/     ← 最外層
    └── api/          # FastAPI router
```

**為什麼要這樣分：**
- 換資料庫（PostgreSQL → DynamoDB）只改 infrastructure，業務邏輯不動
- 換框架（FastAPI → Flask）只改 presentation，業務邏輯不動
- 測試 Use Case 時不需要真實資料庫，mock Repository 介面就好

---

**uv.lock**

`uv.lock` 是 `uv`（一個超快的 Python 套件管理工具）產生的鎖定檔案，記錄專案所有依賴的**精確版本**，確保每個人安裝的套件版本完全一致。

**為什麼需要 lock 檔：**
`pyproject.toml` 裡寫的是版本範圍（如 `fastapi >= 0.100`），但不同時間安裝可能裝到不同版本。lock 檔記錄「上次安裝時實際解析出的精確版本」，確保可重現。

```
pyproject.toml：fastapi >= 0.100（範圍）
uv.lock：fastapi == 0.115.6（精確版本 + hash）
```

**uv 的基本用法：**
```bash
# 安裝 uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 初始化專案
uv init my-project

# 新增依賴（會自動更新 uv.lock）
uv add fastapi
uv add pytest --dev

# 安裝所有依賴（根據 uv.lock）
uv sync

# 執行程式（自動使用正確的虛擬環境）
uv run python main.py
uv run pytest
```

**uv.lock 要不要 commit 進 git：**
- **應用程式（API、服務）**：要 commit，確保部署時版本一致
- **函式庫（給別人用的套件）**：通常不 commit，讓使用者自己解析

**uv vs pip vs poetry：**

| | pip | poetry | uv |
|--|-----|--------|-----|
| 速度 | 慢 | 中等 | 極快（Rust 寫的）|
| Lock 檔 | 無（需要 pip-tools）| poetry.lock | uv.lock |
| 虛擬環境管理 | 手動 | 自動 | 自動 |
| 解析依賴 | 基本 | 完整 | 完整 |

---

## 0527

**Generic 語法 / TypeVar**

Generic（泛型）是一種讓函式或類別「不綁定特定型別」的寫法，讓你可以寫出可重用的程式碼，同時保留型別安全。TypeVar 是 Python 裡定義泛型型別變數的工具。

**為什麼需要 Generic：**
如果你寫一個「回傳第一個元素」的函式，不用泛型的話：
```python
# 只能處理 int，不夠通用
def first(items: list[int]) -> int:
    return items[0]

# 用 Any 失去型別安全
from typing import Any
def first(items: list[Any]) -> Any:
    return items[0]
```

用 Generic 就可以「保留型別資訊」：
```python
from typing import TypeVar

T = TypeVar('T')   # T 是一個型別變數，代表「任意型別」

def first(items: list[T]) -> T:
    return items[0]

# 型別檢查器知道回傳值的型別
result = first([1, 2, 3])      # result 的型別是 int
result = first(["a", "b"])     # result 的型別是 str
```

**TypeVar 的進階用法：**
```python
from typing import TypeVar

# 限制 T 只能是 int 或 float
Number = TypeVar('Number', int, float)

def add(a: Number, b: Number) -> Number:
    return a + b

add(1, 2)       # OK
add(1.0, 2.0)   # OK
add("a", "b")   # 型別錯誤

# 限制 T 必須是某個類別的子類別
from typing import TypeVar
from pydantic import BaseModel

ModelT = TypeVar('ModelT', bound=BaseModel)

def validate_and_return(data: dict, model_class: type[ModelT]) -> ModelT:
    return model_class(**data)
```

**Python 3.12+ 的新語法（更簡潔）：**
```python
# 舊寫法
from typing import TypeVar
T = TypeVar('T')
def first(items: list[T]) -> T: ...

# 新寫法（Python 3.12+）
def first[T](items: list[T]) -> T:
    return items[0]
```

**在 FastAPI / Pydantic 的實際應用：**
```python
from typing import TypeVar, Generic
from pydantic import BaseModel

T = TypeVar('T')

# 通用的分頁回應格式
class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int

# 使用時指定具體型別
class UserResponse(BaseModel):
    id: str
    name: str

# 回傳型別是 PaginatedResponse[UserResponse]
@app.get("/users")
async def list_users() -> PaginatedResponse[UserResponse]:
    ...
```

---

**SonarQube**

SonarQube 是一個靜態程式碼分析平台，自動掃描程式碼找出潛在問題，包含：程式碼品質問題、安全漏洞、重複程式碼、測試覆蓋率等。

**SonarQube 能找出什麼：**

| 類別 | 說明 | 例子 |
|------|------|------|
| Bug | 可能導致錯誤的程式碼 | 空指標存取、資源未關閉 |
| Vulnerability（漏洞）| 安全性問題 | SQL injection、硬編碼密碼 |
| Code Smell | 不影響功能但難維護的程式碼 | 函式太長、重複邏輯 |
| Security Hotspot | 需要人工審查的安全敏感點 | 加密演算法使用 |
| Coverage | 測試覆蓋率 | 哪些程式碼沒有被測試到 |
| Duplications | 重複程式碼 | 違反 DRY 的地方 |

**在 CI/CD 中的整合：**
```yaml
# GitHub Actions 範例
- name: SonarQube Scan
  uses: SonarSource/sonarqube-scan-action@master
  env:
    SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
    SONAR_HOST_URL: ${{ secrets.SONAR_HOST_URL }}
```

**Quality Gate（品質閘門）：**
SonarQube 可以設定「品質閘門」，如果程式碼不符合標準（例如新增程式碼的測試覆蓋率低於 80%），CI 就會失敗，阻止合併。

**SonarQube vs SonarCloud：**
- SonarQube：自架版本，部署在自己的伺服器
- SonarCloud：雲端版本，不需要自架，適合開源或小團隊

---

**JSON-RPC vs REST 的差別**

兩者都是 API 的設計風格，但思維方式完全不同。

**REST（Representational State Transfer）：**
- 以「資源」為中心，URL 代表資源，HTTP 方法代表動作
- 無狀態，每個請求都是獨立的
- 利用 HTTP 的語義（GET/POST/PUT/DELETE、狀態碼）

```
GET    /users/123          → 取得用戶 123
POST   /users              → 建立新用戶
PUT    /users/123          → 更新用戶 123
DELETE /users/123          → 刪除用戶 123
```

**JSON-RPC（JSON Remote Procedure Call）：**
- 以「動作/方法」為中心，呼叫遠端的函式
- 所有請求都用 POST，URL 通常固定（如 `/rpc`）
- 請求 body 裡指定要呼叫的方法名稱和參數

```json
// 請求
{
  "jsonrpc": "2.0",
  "method": "getUser",
  "params": {"id": 123},
  "id": 1
}

// 回應
{
  "jsonrpc": "2.0",
  "result": {"id": 123, "name": "Neo"},
  "id": 1
}
```

**比較：**

| | REST | JSON-RPC |
|--|------|----------|
| 設計思維 | 資源導向 | 動作導向 |
| URL 設計 | 每個資源有獨立 URL | 通常只有一個 endpoint |
| HTTP 方法 | 充分利用 GET/POST/PUT/DELETE | 幾乎只用 POST |
| 錯誤處理 | HTTP 狀態碼（404、500 等）| 統一用 200，錯誤在 body 裡 |
| 適合場景 | 資源的 CRUD 操作 | 複雜的遠端方法呼叫 |
| 常見使用 | Web API、RESTful 服務 | 區塊鏈 API、內部 RPC 服務 |

**什麼時候用 JSON-RPC：**
- 操作不容易對應到 CRUD（例如「計算兩點距離」「發送通知」）
- 需要批次呼叫多個方法（JSON-RPC 支援 batch request）
- 內部服務間通訊，不需要 REST 的語義

**MCP 也用 JSON-RPC：**
Anthropic 的 MCP（Model Context Protocol）底層就是用 JSON-RPC 2.0 來讓 AI 模型呼叫工具，因為「呼叫工具」這個概念更接近「執行方法」而不是「操作資源」。

---

**Hard Reload（強制重新載入）**

Hard Reload 是強制瀏覽器**忽略快取**，重新從伺服器下載所有資源（HTML、CSS、JS、圖片等）。相對於一般的 Reload（F5），Hard Reload 確保你看到的是最新版本，而不是瀏覽器快取的舊版本。

**三種重新載入的差別：**

| 操作 | 行為 | 快捷鍵（macOS）|
|------|------|--------------|
| 一般 Reload | 重新載入頁面，但可能使用快取 | `Cmd + R` |
| Hard Reload | 忽略快取，重新下載所有資源 | `Cmd + Shift + R` |
| Empty Cache + Hard Reload | 清空快取再重新下載 | DevTools 開啟時，長按重新整理按鈕 |

**什麼時候需要 Hard Reload：**
- 你更新了 CSS 或 JS，但瀏覽器還顯示舊版本
- 部署了新版本，但頁面看起來沒有變化
- 開發時改了靜態資源，想確認效果

**背後原理：**
瀏覽器快取靜態資源是為了加速載入。一般 Reload 時，瀏覽器會發送帶有 `If-None-Match` 或 `If-Modified-Since` header 的請求，如果伺服器說「沒變」就用快取。Hard Reload 則是發送帶有 `Cache-Control: no-cache` 的請求，強制伺服器回傳最新版本。

**在開發中避免快取問題的方法：**
```html
<!-- 在 HTML 裡加版本號，讓瀏覽器認為是新檔案 -->
<link rel="stylesheet" href="/style.css?v=1.2.3">
<script src="/app.js?v=1.2.3"></script>
```

```nginx
# nginx 設定：讓 HTML 不快取，靜態資源長期快取
location ~* \.(html)$ {
    add_header Cache-Control "no-cache";
}

location ~* \.(js|css|png|jpg)$ {
    add_header Cache-Control "public, max-age=31536000, immutable";
}
```

---

## 0529

**AWS X-Ray**

AWS X-Ray 是 AWS 提供的**分散式追蹤（Distributed Tracing）服務**，讓你能夠追蹤一個請求從進入系統到結束的完整路徑，看清楚它經過了哪些服務、每個環節花了多少時間、哪裡出了問題。

**解決什麼問題：**
現代應用通常由多個微服務組成（API Gateway → Lambda → DynamoDB → 外部 API），當一個請求變慢或出錯，你很難知道問題出在哪一段。X-Ray 把整條鏈路串起來，讓你一眼看出瓶頸在哪。

**核心概念：**
- **Trace（追蹤）**：一個完整請求的生命週期，從頭到尾
- **Segment（片段）**：Trace 裡的一個服務節點，例如「Lambda 函式的執行」
- **Subsegment（子片段）**：Segment 裡更細的操作，例如「對 DynamoDB 的一次查詢」
- **Service Map**：X-Ray 自動畫出的服務拓撲圖，顯示各服務之間的呼叫關係和健康狀態

**架構示意：**
```
用戶請求
  └── API Gateway (Segment: 5ms)
        └── Lambda (Segment: 120ms)
              ├── DynamoDB query (Subsegment: 80ms)  ← 瓶頸在這
              └── 外部 API call (Subsegment: 30ms)
```

**實作：在 Lambda + Python 裡啟用 X-Ray**

```python
# 安裝 SDK
# pip install aws-xray-sdk

from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all

# 自動 patch 常用的 library（boto3、requests、httpx 等）
patch_all()

def lambda_handler(event, context):
    # X-Ray 會自動追蹤這個 Lambda 的執行

    # 手動建立 subsegment，追蹤自訂的操作
    with xray_recorder.in_subsegment("process-order") as subsegment:
        subsegment.put_annotation("order_id", event["order_id"])
        subsegment.put_metadata("raw_event", event)

        result = process_order(event["order_id"])

    return result
```

**在 AWS Console 啟用 X-Ray（Lambda）：**
```bash
# 用 CLI 啟用 Lambda 的 Active Tracing
aws lambda update-function-configuration \
  --function-name my-function \
  --tracing-config Mode=Active
```

**X-Ray 與 CloudWatch 的關係：**
| | CloudWatch Logs | X-Ray |
|--|----------------|-------|
| 看什麼 | 每個服務的日誌訊息 | 跨服務的請求鏈路 |
| 適合場景 | 查看錯誤訊息、debug 單一服務 | 找出哪個服務造成延遲、分析整體架構 |
| 資料形式 | 文字日誌 | 視覺化的 Trace 圖 |

**實際使用情境：**
- 用戶反映「結帳很慢」→ 用 X-Ray 找出是哪個服務拖慢了整體
- 微服務架構中，某個 API 偶爾 timeout → 用 X-Ray 的 Service Map 找出哪條路徑有問題
- 分析 P99 延遲的來源，決定優化哪個環節

---

**CloudWatch Logs Insights**

CloudWatch Logs Insights 是 AWS 提供的**日誌查詢分析工具**，讓你用類 SQL 的查詢語言，對 CloudWatch 裡的日誌做即時搜尋、過濾、聚合和視覺化，不需要把日誌匯出到其他地方就能分析。

**解決什麼問題：**
CloudWatch 的日誌量通常很大，用肉眼翻 Log Stream 找問題效率很低。Logs Insights 讓你可以用查詢語言快速找出特定錯誤、統計錯誤頻率、分析延遲分佈等。

**查詢語法（Logs Insights Query Language）：**

```
# 基本結構
fields @timestamp, @message
| filter @message like /ERROR/
| sort @timestamp desc
| limit 20
```

**常用查詢範例：**

```
# 1. 找出最近 1 小時的所有 ERROR 日誌
fields @timestamp, @message
| filter @message like /ERROR/
| sort @timestamp desc
| limit 50

# 2. 統計每分鐘的錯誤數量（用來畫趨勢圖）
filter @message like /ERROR/
| stats count(*) as error_count by bin(1m)

# 3. 分析 Lambda 的執行時間分佈
filter @type = "REPORT"
| stats avg(@duration), max(@duration), 
        percentile(@duration, 95) as p95,
        percentile(@duration, 99) as p99
        by bin(5m)

# 4. 找出最慢的 10 個請求
filter @type = "REPORT"
| sort @duration desc
| limit 10
| fields @requestId, @duration, @billedDuration

# 5. 統計特定 HTTP 狀態碼的數量
fields @timestamp, status_code
| filter status_code >= 400
| stats count(*) as count by status_code
| sort count desc

# 6. 解析 JSON 格式的日誌
fields @timestamp
| filter ispresent(order_id)
| stats count(*) as order_count by order_status
```

**用 AWS CLI 執行查詢：**
```bash
# 開始查詢
QUERY_ID=$(aws logs start-query \
  --log-group-name /aws/lambda/order-processor \
  --start-time $(date -d "1 hour ago" +%s) \
  --end-time $(date +%s) \
  --query-string 'fields @timestamp, @message | filter @message like /ERROR/ | limit 20' \
  --query 'queryId' \
  --output text)

# 等待查詢完成並取得結果
aws logs get-query-results --query-id $QUERY_ID
```

**用 Python boto3 執行查詢：**
```python
import boto3
import time
from datetime import datetime, timedelta

logs = boto3.client("logs", region_name="ap-northeast-1")

# 開始查詢
response = logs.start_query(
    logGroupName="/aws/lambda/order-processor",
    startTime=int((datetime.now() - timedelta(hours=1)).timestamp()),
    endTime=int(datetime.now().timestamp()),
    queryString="""
        fields @timestamp, @message
        | filter @message like /ERROR/
        | sort @timestamp desc
        | limit 20
    """
)
query_id = response["queryId"]

# 輪詢直到查詢完成
while True:
    result = logs.get_query_results(queryId=query_id)
    if result["status"] in ("Complete", "Failed", "Cancelled"):
        break
    time.sleep(1)

# 印出結果
for row in result["results"]:
    record = {field["field"]: field["value"] for field in row}
    print(f"{record.get('@timestamp')} - {record.get('@message')}")
```

**與 X-Ray 的搭配使用：**
- 用 **X-Ray** 找出哪個服務有問題（視覺化的鏈路追蹤）
- 用 **Logs Insights** 深入查詢那個服務的詳細日誌（文字搜尋和統計）
- 兩者互補，X-Ray 給你「地圖」，Logs Insights 給你「細節」

**實際使用情境：**
- 收到告警說錯誤率上升 → 用 Logs Insights 查詢錯誤訊息，找出是哪種錯誤
- 分析 Lambda 的 cold start 頻率 → 查詢 `Init Duration` 欄位
- 統計某個 API 的呼叫量和成功率 → 用 `stats` 聚合

---

**Docker 中的 Volume 跟專案的關係**

Docker Volume 是 Docker 提供的**資料持久化機制**，解決「container 是暫時的，但資料需要長久保存」的問題。理解 Volume 和專案的關係，是搞懂 Docker 開發環境的關鍵。

**為什麼需要 Volume：**
Docker container 本身是無狀態的（stateless）。當你停止或刪除一個 container，裡面的所有資料都會消失。但有些資料你希望保留：
- 資料庫的資料（PostgreSQL、MySQL 的資料檔案）
- 上傳的檔案
- 開發時的程式碼（你希望改了程式碼，container 裡立刻生效）

**三種掛載方式：**

```
1. Volume（Docker 管理的儲存空間）
   Host: /var/lib/docker/volumes/myvolume/_data
   Container: /app/data

2. Bind Mount（直接掛載 Host 的目錄）
   Host: /Users/neo/my-project
   Container: /app

3. tmpfs Mount（只存在記憶體，container 停止就消失）
   適合暫存敏感資料
```

**Volume 跟專案的關係（最重要的部分）：**

**情境一：開發環境 — 用 Bind Mount 掛載程式碼**

這是開發時最常見的用法。把你本機的專案目錄掛進 container，這樣你在本機改程式碼，container 裡立刻看到變化，不需要重新 build image。

```yaml
# docker-compose.yml（開發環境）
services:
  api:
    build: .
    ports:
      - "8000:8000"
    volumes:
      # 把本機的專案目錄掛進 container 的 /app
      - .:/app
      # 但 node_modules 或 .venv 不要掛進來（用 container 裡的）
      - /app/.venv
    command: uvicorn main:app --reload --host 0.0.0.0
```

```
你的本機                    Container
/Users/neo/my-project  →   /app
├── main.py            →   /app/main.py
├── models.py          →   /app/models.py
└── requirements.txt   →   /app/requirements.txt

你改了 main.py → container 裡的 /app/main.py 立刻更新
uvicorn 的 --reload 偵測到變化 → 自動重啟
```

**情境二：資料庫 — 用 Named Volume 保存資料**

資料庫的資料不能隨著 container 消失，所以用 Named Volume 讓 Docker 幫你管理。

```yaml
# docker-compose.yml
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: secret
    volumes:
      # postgres-data 是一個 named volume，Docker 幫你管理
      - postgres-data:/var/lib/postgresql/data

  api:
    build: .
    depends_on:
      - db
    volumes:
      - .:/app   # 程式碼用 bind mount

volumes:
  postgres-data:   # 宣告這個 named volume
```

```bash
# 查看所有 volumes
docker volume ls

# 查看 volume 的詳細資訊（存在哪裡）
docker volume inspect postgres-data

# 刪除 volume（資料會消失！）
docker volume rm postgres-data

# 刪除所有未使用的 volume
docker volume prune
```

**情境三：生產環境 — 不掛載程式碼**

生產環境的 image 應該把程式碼 COPY 進去，不用 volume 掛載程式碼，確保 image 是自包含的（self-contained）。

```dockerfile
# Dockerfile（生產環境）
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

# 程式碼直接 COPY 進 image，不依賴 volume
COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**開發 vs 生產的 Volume 策略對比：**

| | 開發環境 | 生產環境 |
|--|---------|---------|
| 程式碼 | Bind Mount（即時同步）| COPY 進 image（固定版本）|
| 資料庫資料 | Named Volume | Named Volume 或雲端儲存（RDS）|
| 設定檔 | Bind Mount 或環境變數 | 環境變數或 Secrets Manager |
| 目的 | 快速迭代、即時看到變化 | 穩定、可重現、安全 |

**常見的 Volume 陷阱：**

```yaml
# 陷阱：掛載整個目錄後，container 裡的 .venv 被覆蓋
volumes:
  - .:/app   # 這會把本機的 . 覆蓋 container 的 /app
             # 如果本機沒有 .venv，container 裡的 .venv 也消失了

# 解法：用匿名 volume 保護 container 裡的特定目錄
volumes:
  - .:/app
  - /app/.venv   # 這個目錄用 container 自己的，不被 host 覆蓋
```

**完整的開發環境 docker-compose 範例：**

```yaml
version: "3.9"

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile.dev
    ports:
      - "8000:8000"
    volumes:
      - .:/app          # 程式碼即時同步
      - /app/.venv      # 保護 container 裡的虛擬環境
    environment:
      - DATABASE_URL=postgresql://postgres:secret@db:5432/mydb
    depends_on:
      - db
    command: uvicorn main:app --reload --host 0.0.0.0 --port 8000

  db:
    image: postgres:15
    ports:
      - "5432:5432"
    environment:
      POSTGRES_DB: mydb
      POSTGRES_PASSWORD: secret
    volumes:
      - postgres-data:/var/lib/postgresql/data   # 資料持久化

volumes:
  postgres-data:
```

**Volume 的核心概念總結：**
- **Bind Mount**：你控制路徑，適合開發時掛載程式碼
- **Named Volume**：Docker 控制路徑，適合資料庫等需要持久化的資料
- 開發環境用 Bind Mount 掛程式碼 → 改了立刻生效
- 生產環境把程式碼 COPY 進 image → 穩定可重現
- 資料庫永遠用 Volume → 避免 container 重啟後資料消失
