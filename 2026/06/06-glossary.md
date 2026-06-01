# 06 每日名詞解釋

## 0601

**SDK（Software Development Kit）**

SDK 是「軟體開發套件」，一組讓你能夠跟某個平台、服務或語言互動的工具集合。它通常包含：函式庫（library）、API 封裝、範例程式碼、文件，有時還有 CLI 工具。

**為什麼需要 SDK：**
直接呼叫 API 需要自己處理 HTTP 請求、簽名、錯誤處理、重試邏輯等底層細節。SDK 把這些都封裝好，讓你只需要呼叫幾行程式碼就能完成任務。

**例子：**
```python
# 沒有 SDK：自己處理 AWS API（非常繁瑣）
import hmac, hashlib, datetime, requests
# 需要自己實作 AWS Signature Version 4 簽名...（幾十行）

# 有 SDK（boto3）：幾行搞定
import boto3
s3 = boto3.client("s3")
s3.upload_file("local.txt", "my-bucket", "remote.txt")
```

**常見 SDK 對照：**
| 服務 | SDK 名稱 | 語言 |
|------|---------|------|
| AWS | boto3 | Python |
| AWS | AWS SDK for JavaScript | Node.js |
| OpenAI | openai | Python / Node |
| Stripe | stripe | Python / Node / Ruby |
| Firebase | firebase-admin | Python / Node |

**SDK vs API vs Library 的差別：**
- **API**：定義「可以做什麼」的介面規格（通常是 HTTP endpoints）
- **Library**：一組可重用的函式集合
- **SDK**：包含 Library + 工具 + 文件 + 範例，是更完整的開發套件

---

**P90 Latency（第 90 百分位延遲）**

P90 是「Percentile 90」，代表在所有請求中，有 90% 的請求延遲低於這個數值，最慢的 10% 超過這個數值。

**為什麼不用平均值：**
平均值會被少數極端值拉偏。假設 100 個請求，99 個都是 10ms，1 個是 10000ms，平均是 109ms，但其實 99% 的用戶體驗都很好。百分位數更能反映真實的用戶體驗分佈。

**常見的延遲指標：**
| 指標 | 意義 | 用途 |
|------|------|------|
| P50 | 中位數，50% 的請求低於此值 | 一般用戶的典型體驗 |
| P90 | 90% 的請求低於此值 | 大多數用戶的體驗上限 |
| P95 | 95% 的請求低於此值 | 更嚴格的標準 |
| P99 | 99% 的請求低於此值 | 尾端延遲，找出最慢的那群 |

**實際例子：**
```
100 個請求的延遲（ms）：
10, 12, 11, 15, 13, 10, 11, 14, 12, ... (90 個都在 10-20ms)
... 最後 10 個：50, 80, 120, 200, 300, 400, 500, 600, 800, 1000

P50 = 13ms   ← 一般用戶感受很快
P90 = 50ms   ← 90% 的人在 50ms 以內
P99 = 900ms  ← 最慢的 1% 要等將近 1 秒
```

**在 CloudWatch 查詢 P90：**
```python
import boto3

cloudwatch = boto3.client("cloudwatch")
response = cloudwatch.get_metric_statistics(
    Namespace="MyApp",
    MetricName="APILatency",
    StartTime=start,
    EndTime=end,
    Period=300,
    ExtendedStatistics=["p90", "p95", "p99"]
)
```

**SLA 中的應用：**
SLA 通常會這樣寫：「P99 延遲 < 500ms，P90 延遲 < 200ms」，而不是「平均延遲 < 100ms」，因為百分位數更能保護用戶體驗。

---

**KB Query（Knowledge Base Query）**

KB Query 是對「知識庫（Knowledge Base）」的查詢操作。在 AI / RAG（Retrieval-Augmented Generation）架構中，KB 是存放結構化或非結構化知識的地方，KB Query 就是從這個知識庫裡找出跟問題相關的資訊。

**在 AWS 的情境（Amazon Bedrock Knowledge Base）：**
AWS Bedrock 提供 Knowledge Base 功能，讓你把文件（PDF、Word、網頁等）上傳到 S3，Bedrock 會自動做向量化（embedding）並存進向量資料庫，之後你就可以用自然語言查詢。

```python
import boto3

bedrock_agent = boto3.client("bedrock-agent-runtime", region_name="us-east-1")

# KB Query：用自然語言查詢知識庫
response = bedrock_agent.retrieve(
    knowledgeBaseId="XXXXXXXXXX",
    retrievalQuery={
        "text": "公司的請假政策是什麼？"
    },
    retrievalConfiguration={
        "vectorSearchConfiguration": {
            "numberOfResults": 5   # 回傳最相關的 5 筆
        }
    }
)

# 取得查詢結果
for result in response["retrievalResults"]:
    print(result["content"]["text"])
    print(f"相關度分數：{result['score']}")
```

**KB Query 的運作原理：**
```
用戶問題（文字）
    ↓ Embedding Model 轉成向量
問題向量
    ↓ 向量相似度搜尋（cosine similarity）
知識庫裡最相關的文件片段
    ↓ 傳給 LLM 作為 context
最終回答
```

**與一般資料庫查詢的差別：**
| | 一般 DB Query | KB Query |
|--|--------------|---------|
| 查詢方式 | 精確匹配（SQL WHERE）| 語意相似度搜尋 |
| 適合場景 | 找特定 ID、精確數值 | 找「跟這個問題相關的內容」|
| 底層技術 | B-tree index | 向量索引（FAISS、pgvector）|

---

**SLA 分解（SLA Decomposition）**

SLA（Service Level Agreement，服務等級協議）是對服務品質的承諾，例如「系統可用性 99.9%」或「API P99 延遲 < 500ms」。SLA 分解是把一個整體的 SLA 目標，拆解到各個子系統或元件上，讓每個部分都有自己的目標，合起來才能達到整體承諾。

**為什麼需要分解：**
一個 API 請求可能經過 API Gateway → Lambda → DynamoDB → 外部服務，如果整體 SLA 是 500ms，你需要知道每個環節最多能用多少時間，否則無法設計和監控。

**分解的方式：**
```
整體 SLA：P99 < 500ms

分解：
├── API Gateway overhead：< 10ms
├── Lambda 執行（含冷啟動）：< 300ms
│   ├── 業務邏輯：< 100ms
│   ├── DynamoDB query：< 150ms
│   └── 其他：< 50ms
└── 網路傳輸：< 190ms
```

**Error Budget（錯誤預算）的概念：**
SLA 99.9% 可用性代表每個月允許約 43 分鐘的停機時間，這就是你的「錯誤預算」。SLA 分解也包含把這個預算分配給各個元件：
```
每月錯誤預算：43 分鐘
├── 計劃性維護：20 分鐘
├── 資料庫故障容忍：10 分鐘
├── 部署失敗容忍：8 分鐘
└── 其他意外：5 分鐘
```

**實作：用 CloudWatch Alarm 監控各層 SLA**
```python
import boto3

cloudwatch = boto3.client("cloudwatch")

# 為每個子系統設定獨立的 alarm
cloudwatch.put_metric_alarm(
    AlarmName="DynamoDB-P99-SLA",
    MetricName="SuccessfulRequestLatency",
    Namespace="AWS/DynamoDB",
    Statistic="p99",
    Period=300,
    Threshold=150,          # DynamoDB 分配到的 SLA：150ms
    ComparisonOperator="GreaterThanThreshold",
    EvaluationPeriods=3,
    AlarmActions=["arn:aws:sns:..."]
)
```

---

**KC 呼叫點（Knowledge Component Call Point）**

KC 呼叫點是指在程式碼或系統架構中，**呼叫某個知識元件（Knowledge Component）或外部服務的具體位置**。在 AI Agent 或 RAG 系統的設計中，KC 呼叫點標記了「在哪裡、什麼時機去查詢知識庫或呼叫 AI 模型」。

**在 Agent 架構中的意義：**
一個複雜的業務流程可能有多個地方需要查詢知識庫或呼叫 LLM，KC 呼叫點讓你明確定義這些位置，方便追蹤、測試和優化。

**例子：**
```python
class OrderProcessor:
    def __init__(self, kb_client, llm_client):
        self.kb = kb_client
        self.llm = llm_client

    def process(self, order):
        # KC 呼叫點 1：查詢商品知識庫，確認商品資訊
        product_info = self.kb.query(f"商品 {order.product_id} 的規格")

        # 業務邏輯...
        if order.has_special_request:
            # KC 呼叫點 2：呼叫 LLM 處理特殊需求
            response = self.llm.generate(
                f"訂單有特殊需求：{order.special_request}，請建議處理方式"
            )

        # KC 呼叫點 3：查詢退換貨政策
        policy = self.kb.query("退換貨政策")
```

**為什麼要明確標記 KC 呼叫點：**
- **可觀測性**：在每個呼叫點加上 tracing（X-Ray span），知道每次 KB 查詢花了多少時間
- **測試**：可以 mock 掉 KC 呼叫點，讓業務邏輯測試不依賴真實的 KB
- **優化**：找出哪個呼叫點最慢，決定是否要加 cache

---

**Span Attribute（追蹤屬性）**

Span 是分散式追蹤（Distributed Tracing）中的基本單位，代表一個操作的執行區間（有開始時間和結束時間）。Span Attribute 是附加在 Span 上的 key-value 標籤，用來描述這個操作的上下文資訊，方便後續查詢和分析。

**Span 的結構：**
```
Span
├── trace_id: "abc123"          # 整條請求鏈路的 ID
├── span_id: "def456"           # 這個 span 的 ID
├── parent_span_id: "xyz789"    # 上層 span 的 ID
├── name: "DynamoDB.GetItem"    # 操作名稱
├── start_time: 1234567890.123
├── end_time: 1234567890.456
├── duration: 333ms
└── attributes:                 # ← 這就是 Span Attribute
    ├── db.system: "dynamodb"
    ├── db.operation: "GetItem"
    ├── db.table: "orders"
    ├── order.id: "ORD-001"
    └── http.status_code: 200
```

**用 OpenTelemetry 設定 Span Attribute（Python）：**
```python
from opentelemetry import trace
from opentelemetry.trace import SpanKind

tracer = trace.get_tracer(__name__)

def process_order(order_id: str):
    with tracer.start_as_current_span(
        "process_order",
        kind=SpanKind.INTERNAL
    ) as span:
        # 設定 span attributes
        span.set_attribute("order.id", order_id)
        span.set_attribute("order.source", "web")
        span.set_attribute("service.version", "2.1.0")

        try:
            result = do_processing(order_id)
            span.set_attribute("order.status", "success")
            span.set_attribute("order.total", result.total)
            return result
        except Exception as e:
            span.set_attribute("error", True)
            span.set_attribute("error.message", str(e))
            span.record_exception(e)
            raise
```

**Span Attribute 的命名慣例（OpenTelemetry Semantic Conventions）：**
| 前綴 | 用途 | 例子 |
|------|------|------|
| `http.*` | HTTP 請求 | `http.method`, `http.status_code` |
| `db.*` | 資料庫操作 | `db.system`, `db.statement` |
| `rpc.*` | RPC 呼叫 | `rpc.service`, `rpc.method` |
| `messaging.*` | 訊息佇列 | `messaging.system`, `messaging.destination` |
| 自訂 | 業務邏輯 | `order.id`, `user.tier` |

**與 X-Ray 的對應：**
AWS X-Ray 裡的 Annotation 和 Metadata 對應到 OpenTelemetry 的 Span Attribute：
```python
# X-Ray 的寫法
subsegment.put_annotation("order_id", "ORD-001")   # 可搜尋
subsegment.put_metadata("raw_data", {...})           # 不可搜尋，存詳細資料

# OpenTelemetry 的寫法
span.set_attribute("order.id", "ORD-001")           # 統一用 attribute
```

---

**Coverage Integration Test（整合測試覆蓋率）**

Coverage 是測試覆蓋率，衡量你的測試跑過了多少比例的程式碼。Integration Test 是整合測試，測試多個元件組合在一起的行為（相對於 Unit Test 只測單一函式）。Coverage Integration Test 就是在跑整合測試時，同時收集覆蓋率數據。

**為什麼整合測試的覆蓋率特別重要：**
Unit Test 的覆蓋率高，不代表整合起來沒問題。整合測試的覆蓋率能告訴你，在真實的呼叫鏈路下，哪些程式碼路徑有被走到。

**用 pytest + coverage 收集整合測試覆蓋率：**
```bash
# 安裝
pip install pytest pytest-cov

# 跑整合測試並收集覆蓋率
pytest tests/integration/ \
  --cov=src \
  --cov-report=html \
  --cov-report=term-missing

# 輸出範例：
# Name                    Stmts   Miss  Cover
# ----------------------------------------------
# src/order_service.py       45      3    93%
# src/payment_service.py     32      8    75%
# src/notification.py        18     18     0%  ← 完全沒被整合測試覆蓋到
```

**在 CI/CD 設定覆蓋率門檻：**
```yaml
# .github/workflows/test.yml
- name: Run integration tests with coverage
  run: |
    pytest tests/integration/ \
      --cov=src \
      --cov-fail-under=80   # 覆蓋率低於 80% 就讓 CI 失敗
```

**覆蓋率的種類：**
| 類型 | 說明 |
|------|------|
| Line Coverage | 每一行程式碼是否被執行到 |
| Branch Coverage | 每個 if/else 的分支是否都走過 |
| Function Coverage | 每個函式是否被呼叫過 |

**注意事項：**
覆蓋率高不等於測試品質好。100% 覆蓋率但沒有 assertion，測試毫無意義。覆蓋率是「下限指標」，告訴你哪些地方完全沒測到，而不是「上限指標」。

---

**AST Parse（抽象語法樹解析）**

AST（Abstract Syntax Tree，抽象語法樹）是程式碼的樹狀結構表示。AST Parse 是把原始程式碼文字解析成這個樹狀結構的過程，讓程式能夠「理解」程式碼的結構，而不只是把它當成字串處理。

**為什麼需要 AST：**
如果你想分析或修改程式碼（例如找出所有函式名稱、自動重構、靜態分析），用字串搜尋很脆弱，用 AST 才能正確理解程式碼的語意結構。

**Python 的 AST 長什麼樣：**
```python
import ast

code = """
def add(a, b):
    return a + b
"""

tree = ast.parse(code)
print(ast.dump(tree, indent=2))

# 輸出（簡化）：
# Module(
#   body=[
#     FunctionDef(
#       name='add',
#       args=arguments(args=[arg(arg='a'), arg(arg='b')]),
#       body=[
#         Return(
#           value=BinOp(left=Name(id='a'), op=Add(), right=Name(id='b'))
#         )
#       ]
#     )
#   ]
# )
```

**實際應用：用 AST 找出所有函式名稱**
```python
import ast

class FunctionFinder(ast.NodeVisitor):
    def __init__(self):
        self.functions = []

    def visit_FunctionDef(self, node):
        self.functions.append({
            "name": node.name,
            "line": node.lineno,
            "args": [arg.arg for arg in node.args.args]
        })
        self.generic_visit(node)  # 繼續遍歷子節點

code = open("my_module.py").read()
tree = ast.parse(code)

finder = FunctionFinder()
finder.visit(tree)

for func in finder.functions:
    print(f"Line {func['line']}: {func['name']}({', '.join(func['args'])})")
```

**AST 的常見用途：**
| 用途 | 工具 / 場景 |
|------|------------|
| 靜態分析 | pylint、flake8、mypy 都是基於 AST |
| 程式碼格式化 | black、prettier 解析 AST 再重新輸出 |
| 自動重構 | 批次重命名變數、函式 |
| 程式碼生成 | 根據 schema 自動生成程式碼 |
| 安全掃描 | 找出危險的函式呼叫（如 eval、exec）|
| AI 程式碼理解 | LLM 工具用 AST 理解程式碼結構 |

---

**防退化測試（Regression Test / Anti-Regression Test）**

防退化測試是確保「已經修好的 bug 不會再次出現」、「已有的功能不會因為新的改動而壞掉」的測試。每次修完一個 bug 或加完一個功能，就寫一個對應的測試，讓未來的改動不會不小心把它弄壞。

**為什麼叫「防退化」：**
「退化（Regression）」指的是程式碼在某次改動後，原本正常的功能變得不正常了。防退化測試就是防止這種「倒退」發生。

**典型的防退化測試流程：**
```
發現 Bug
    ↓
先寫一個測試，確認這個測試會失敗（證明 bug 存在）
    ↓
修復 Bug
    ↓
確認測試通過
    ↓
這個測試永遠留在 test suite 裡
    ↓
未來任何改動，如果不小心讓這個 bug 復活，測試會立刻抓到
```

**實作範例：**
```python
# 假設發現一個 bug：當 quantity=0 時，計算總價會除以零
# 先寫防退化測試

import pytest
from order import calculate_total

class TestCalculateTotalRegression:
    """防退化測試：確保已修復的 bug 不再出現"""

    def test_quantity_zero_should_return_zero_not_raise(self):
        """Bug #123：quantity=0 時不應該拋出 ZeroDivisionError"""
        # 這個測試在 bug 修復前會失敗
        result = calculate_total(price=100, quantity=0)
        assert result == 0  # 應該回傳 0，不是拋出例外

    def test_negative_quantity_should_raise_value_error(self):
        """Bug #124：負數 quantity 應該拋出 ValueError"""
        with pytest.raises(ValueError, match="quantity must be non-negative"):
            calculate_total(price=100, quantity=-1)
```

**防退化測試 vs 其他測試的關係：**
| 測試類型 | 目的 |
|---------|------|
| Unit Test | 測試單一函式的邏輯正確性 |
| Integration Test | 測試多個元件組合的行為 |
| Regression Test | 確保已知問題不再復發 |
| Smoke Test | 快速確認系統基本功能正常 |

防退化測試不是獨立的測試類型，它可以是 unit test 或 integration test，差別在於「它是為了防止特定 bug 復發而寫的」。

**在 CI/CD 的重要性：**
每次 PR 都跑完整的 test suite（包含所有防退化測試），確保新的改動沒有讓舊的東西壞掉。這是「持續整合」的核心價值之一。

---

**TTFT（Time To First Token）**

TTFT 是「第一個 Token 出現的時間」，衡量從你送出請求到 LLM 開始輸出第一個字的延遲。這是 AI 應用中最重要的延遲指標之一，直接影響用戶感受到的「反應速度」。

**為什麼 TTFT 特別重要：**
LLM 的輸出是串流（streaming）的，一個字一個字吐出來。用戶不需要等全部輸出完才看到內容，但如果 TTFT 很高，用戶會盯著空白畫面等很久，感覺系統「卡住了」。

**TTFT 的組成：**
```
用戶送出請求
    ↓
網路傳輸（request 到達 LLM 服務）
    ↓
LLM 處理 prompt（prefill 階段）← 這是 TTFT 最大的來源
    ↓
第一個 token 輸出  ← TTFT 在這裡結束
    ↓
後續 token 持續輸出（decode 階段）
    ↓
輸出完成
```

**影響 TTFT 的因素：**
| 因素 | 說明 |
|------|------|
| Prompt 長度 | Prompt 越長，prefill 越慢，TTFT 越高 |
| 模型大小 | 模型越大，處理越慢 |
| 硬體（GPU）| GPU 越強，TTFT 越低 |
| 並發請求數 | 同時請求越多，排隊等待越久 |
| Context window | 使用的 context 越長，TTFT 越高 |

**在 Python 中測量 TTFT：**
```python
import time
import boto3
import json

bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

start_time = time.perf_counter()
first_token_time = None

# 用 streaming 方式呼叫
response = bedrock.invoke_model_with_response_stream(
    modelId="anthropic.claude-3-sonnet-20240229-v1:0",
    body=json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1024,
        "messages": [{"role": "user", "content": "解釋什麼是 TTFT"}]
    })
)

for event in response["body"]:
    chunk = json.loads(event["chunk"]["bytes"])
    if chunk["type"] == "content_block_delta":
        if first_token_time is None:
            first_token_time = time.perf_counter()
            ttft = first_token_time - start_time
            print(f"TTFT: {ttft * 1000:.2f}ms")
        print(chunk["delta"]["text"], end="", flush=True)
```

**TTFT vs 其他 LLM 延遲指標：**
| 指標 | 定義 | 用途 |
|------|------|------|
| TTFT | 第一個 token 出現的時間 | 衡量「感知速度」|
| TPS（Tokens Per Second）| 每秒輸出幾個 token | 衡量輸出速度 |
| Total Latency | 整個回應完成的時間 | 衡量整體效能 |

**優化 TTFT 的方法：**
- 縮短 system prompt（減少 prefill 計算量）
- 使用較小的模型（速度快但品質可能下降）
- 使用 prompt caching（AWS Bedrock 支援，重複的 prompt 部分不需要重新計算）
- 選擇離用戶較近的 region（減少網路延遲）

---

**AWS Transform（AWS 轉換服務）**

AWS Transform 是 AWS 提供的**程式碼和基礎設施遷移轉換服務**，利用 AI 幫助你把舊的程式碼、設定或架構自動轉換成新的格式，減少手動遷移的工作量。

**主要的 Transform 服務：**

**1. AWS Transform for .NET（最常見）**
把舊的 .NET Framework 應用程式自動轉換成現代的 .NET（跨平台），讓它能跑在 Linux container 上，降低授權費用。

```
舊架構：Windows Server + .NET Framework 4.x（只能跑在 Windows）
    ↓ AWS Transform 分析程式碼
    ↓ 自動修改不相容的 API 呼叫
    ↓ 更新 NuGet 套件版本
新架構：Linux Container + .NET 8（跨平台，可跑在 ECS/EKS）
```

**2. AWS Transform for Java**
把舊的 Java 8 / Java 11 應用程式升級到 Java 17 / Java 21，自動處理 deprecated API 和語法變更。

**3. Amazon Q Developer Transform（最新）**
整合進 Amazon Q（AWS 的 AI 助手），在 IDE 裡直接幫你做程式碼轉換：
```
你在 IDE 裡選取舊程式碼
    ↓
Amazon Q 分析並建議轉換方式
    ↓
自動產生轉換後的程式碼
    ↓
你 review 並接受或修改
```

**Transform 的運作流程：**
```bash
# 1. 在 AWS Console 建立 Transform job
# 2. 指定來源（CodeCommit repo 或 S3）
# 3. Transform 服務分析程式碼
# 4. 產生轉換計畫（你可以 review）
# 5. 執行轉換，產生 PR 或直接修改
# 6. 你 review 變更，測試，合併
```

**與手動遷移的差別：**
| | 手動遷移 | AWS Transform |
|--|---------|--------------|
| 時間 | 數週到數月 | 數小時到數天 |
| 人力 | 需要熟悉新舊技術的工程師 | AI 自動處理大部分 |
| 風險 | 容易遺漏邊緣案例 | AI 系統性掃描所有程式碼 |
| 適合場景 | 複雜的業務邏輯調整 | 大量重複性的語法/API 升級 |

**實際使用情境：**
- 公司有幾十個舊的 .NET Framework 服務，想容器化部署到 ECS
- Java 8 EOL，需要批次升級到 Java 21
- 把 CloudFormation 模板轉換成 CDK 程式碼

---

**Binary（二進位）**

Binary 在電腦科學裡有兩個常見的意思，要看上下文判斷：

**意思一：二進位數字系統（Base-2）**

電腦只懂 0 和 1，所有資料在底層都是用二進位表示的。

```
十進位  →  二進位
0       →  0
1       →  1
2       →  10
3       →  11
4       →  100
10      →  1010
255     →  11111111  （1 byte = 8 bits 的最大值）
```

**位元（bit）和位元組（byte）：**
```
1 bit  = 0 或 1
8 bits = 1 byte
1 KB   = 1024 bytes
1 MB   = 1024 KB
1 GB   = 1024 MB
```

**Python 中的二進位操作：**
```python
# 十進位轉二進位
print(bin(10))      # '0b1010'
print(bin(255))     # '0b11111111'

# 二進位轉十進位
print(int('1010', 2))   # 10
print(int('11111111', 2))  # 255

# 位元運算（Bitwise Operations）
a = 0b1010   # 10
b = 0b1100   # 12

print(bin(a & b))   # AND: 0b1000 = 8
print(bin(a | b))   # OR:  0b1110 = 14
print(bin(a ^ b))   # XOR: 0b0110 = 6
print(bin(~a))      # NOT: -11（補數）
print(bin(a << 1))  # 左移: 0b10100 = 20（乘以 2）
print(bin(a >> 1))  # 右移: 0b101 = 5（除以 2）
```

**意思二：二進位檔案（Binary File）**

相對於文字檔（Text File），二進位檔案的內容不是人類可讀的文字，而是直接儲存原始的位元組資料。

```
文字檔（.txt, .py, .json）：
  內容是 UTF-8 或 ASCII 編碼的字元，用文字編輯器打開看得懂

二進位檔（.exe, .jpg, .mp4, .pkl）：
  內容是原始位元組，用文字編輯器打開會看到亂碼
```

**Python 讀寫二進位檔案：**
```python
# 讀取二進位檔案（例如圖片）
with open("image.jpg", "rb") as f:   # "rb" = read binary
    data = f.read()
    print(type(data))    # <class 'bytes'>
    print(data[:4])      # b'\xff\xd8\xff\xe0'（JPEG 的 magic bytes）

# 寫入二進位檔案
with open("output.bin", "wb") as f:  # "wb" = write binary
    f.write(b'\x00\x01\x02\x03')

# 序列化 Python 物件成二進位（pickle）
import pickle

data = {"name": "neo", "scores": [95, 87, 92]}
with open("data.pkl", "wb") as f:
    pickle.dump(data, f)

# 反序列化
with open("data.pkl", "rb") as f:
    loaded = pickle.load(f)
print(loaded)   # {'name': 'neo', 'scores': [95, 87, 92]}
```

**在 AWS 的情境：**
```python
import boto3

s3 = boto3.client("s3")

# 上傳二進位檔案（模型檔、圖片等）
with open("model.pkl", "rb") as f:
    s3.upload_fileobj(f, "my-bucket", "models/model.pkl")

# 下載並直接在記憶體處理（不寫到磁碟）
import io
buffer = io.BytesIO()
s3.download_fileobj("my-bucket", "models/model.pkl", buffer)
buffer.seek(0)
model = pickle.load(buffer)
```

**Magic Bytes（檔案識別碼）：**
每種二進位格式的開頭幾個 bytes 有固定的值，用來識別檔案類型：
| 格式 | Magic Bytes（hex）|
|------|-----------------|
| JPEG | `FF D8 FF` |
| PNG | `89 50 4E 47` |
| PDF | `25 50 44 46`（`%PDF`）|
| ZIP | `50 4B 03 04` |
| ELF（Linux 執行檔）| `7F 45 4C 46` |
