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

---

**Docker 中的 CMD**

`CMD` 是 Dockerfile 裡的指令，定義**容器啟動時預設執行的命令**。它不是在 build image 時執行，而是在你 `docker run` 啟動容器時才執行。

**基本用法：**
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

# 容器啟動時預設跑這個
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**CMD 的三種寫法：**
```dockerfile
# 1. Exec 格式（推薦）：JSON array，不透過 shell 執行
CMD ["python", "app.py"]

# 2. Shell 格式：透過 /bin/sh -c 執行，可以用 shell 語法
CMD python app.py

# 3. 作為 ENTRYPOINT 的預設參數（後面會說）
CMD ["--port", "8000"]
```

**CMD 可以被覆蓋：**
這是 CMD 最重要的特性——`docker run` 時在最後加上指令，就會覆蓋 CMD。

```bash
# 使用 Dockerfile 裡的 CMD（跑 uvicorn）
docker run my-app

# 覆蓋 CMD，改成跑 bash（進入容器 debug）
docker run -it my-app bash

# 覆蓋 CMD，跑一次性的腳本
docker run my-app python scripts/migrate.py
```

**RUN vs CMD 的差別：**
| 指令 | 執行時機 | 用途 |
|------|---------|------|
| `RUN` | build image 時 | 安裝套件、設定環境 |
| `CMD` | 容器啟動時 | 定義預設的啟動命令 |

---

**`--rm`（自動刪除容器）**

`docker run --rm` 是一個旗標，讓容器在**停止後自動刪除**，不會留下停止狀態的容器殘骸。

**為什麼需要 `--rm`：**
每次 `docker run` 都會建立一個新的容器實例。如果不加 `--rm`，容器停止後還是存在（狀態是 `Exited`），佔用磁碟空間，久了會累積很多垃圾容器。

```bash
# 不加 --rm：容器停止後還在
docker run python:3.11 python -c "print('hello')"
docker ps -a   # 會看到一個 Exited 狀態的容器

# 加 --rm：容器停止後自動刪除
docker run --rm python:3.11 python -c "print('hello')"
docker ps -a   # 什麼都沒有，乾乾淨淨
```

**常見使用情境：**
```bash
# 1. 跑一次性的工具或腳本
docker run --rm \
  -v $(pwd):/app \
  python:3.11 \
  python /app/scripts/seed_db.py

# 2. 用容器跑測試（跑完就刪）
docker run --rm \
  -e DATABASE_URL=postgresql://... \
  my-app \
  pytest tests/

# 3. 用容器跑 CLI 工具（不想在本機裝）
docker run --rm \
  -v $(pwd):/workspace \
  hashicorp/terraform:latest \
  terraform plan

# 4. 互動式的一次性容器
docker run --rm -it ubuntu bash
# 離開 bash 後容器自動刪除
```

**`--rm` 跟 `-d`（背景執行）不能同時用：**
`--rm` 是「停止後刪除」，`-d` 是「背景執行」。背景執行的容器通常是長期服務，不應該自動刪除，所以這兩個旗標不能一起用。

```bash
docker run --rm -d my-app   # ❌ 這樣不行
docker run -d my-app        # ✓ 長期服務用這個
docker run --rm my-app      # ✓ 一次性任務用這個
```

---

**ENTRYPOINT（容器進入點）**

`ENTRYPOINT` 也是 Dockerfile 的指令，定義**容器啟動時一定會執行的命令**，跟 `CMD` 的差別在於它**不能被 `docker run` 後面的參數覆蓋**（只能被 `--entrypoint` 旗標覆蓋）。

**ENTRYPOINT vs CMD 的核心差別：**

```dockerfile
# 只用 CMD
CMD ["python", "app.py"]
# docker run my-app bash → 執行 bash（CMD 被覆蓋）

# 只用 ENTRYPOINT
ENTRYPOINT ["python", "app.py"]
# docker run my-app bash → 執行 python app.py bash（bash 變成參數！）

# ENTRYPOINT + CMD 搭配（最常見的模式）
ENTRYPOINT ["python", "app.py"]
CMD ["--port", "8000"]
# docker run my-app → 執行 python app.py --port 8000
# docker run my-app --port 9000 → 執行 python app.py --port 9000（CMD 被覆蓋，ENTRYPOINT 不變）
```

**最常見的搭配模式：**
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

# ENTRYPOINT 定義「要跑什麼程式」（固定不變）
ENTRYPOINT ["uvicorn", "main:app"]

# CMD 定義「預設參數」（可以被覆蓋）
CMD ["--host", "0.0.0.0", "--port", "8000"]
```

```bash
# 用預設參數啟動
docker run my-app
# → uvicorn main:app --host 0.0.0.0 --port 8000

# 覆蓋 CMD，改用不同 port
docker run my-app --host 0.0.0.0 --port 9000
# → uvicorn main:app --host 0.0.0.0 --port 9000

# 強制覆蓋 ENTRYPOINT（debug 用）
docker run --entrypoint bash -it my-app
# → bash（完全忽略 ENTRYPOINT）
```

**用 ENTRYPOINT 做 wrapper script：**
```dockerfile
# entrypoint.sh
#!/bin/bash
set -e

# 容器啟動時先做初始化（例如等資料庫就緒）
echo "Waiting for database..."
until pg_isready -h $DB_HOST; do
  sleep 1
done

echo "Database ready, starting app..."
exec "$@"   # 執行傳進來的命令（CMD 或 docker run 後面的參數）
```

```dockerfile
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]
```

**三者關係總結：**
```
docker run my-app --port 9000
         ↓
ENTRYPOINT ["uvicorn", "main:app"]   ← 固定，不能被參數覆蓋
CMD ["--host", "0.0.0.0"]           ← 被 --port 9000 覆蓋
         ↓
實際執行：uvicorn main:app --port 9000
```

| 指令 | 可被 `docker run` 參數覆蓋？ | 用途 |
|------|--------------------------|------|
| `RUN` | N/A（build 時執行）| 安裝套件、設定環境 |
| `ENTRYPOINT` | 不行（需要 `--entrypoint`）| 定義容器的「主程式」|
| `CMD` | 可以 | 定義預設參數或預設命令 |

---

**ADOT Collector（AWS Distro for OpenTelemetry Collector）**

ADOT Collector 是 AWS 基於開源的 [OpenTelemetry Collector](https://opentelemetry.io/docs/collector/) 所發行的版本，專門針對 AWS 環境做了優化和整合。它是一個**遙測資料的收集、處理、轉發代理（agent）**，負責把你應用程式產生的 traces、metrics、logs 收集起來，送到 AWS X-Ray、CloudWatch、Prometheus 等後端。

**為什麼需要 ADOT Collector：**
應用程式用 OpenTelemetry SDK 產生遙測資料後，不會直接送到 X-Ray 或 CloudWatch，而是先送到 Collector，由 Collector 統一處理（過濾、轉換、批次）再轉發。這樣應用程式不需要知道後端是什麼，只需要說「我要送 OpenTelemetry 格式的資料」。

**架構示意：**
```
你的應用程式（Python / Java / Node）
  └── OpenTelemetry SDK（產生 traces / metrics）
        ↓ OTLP 協定
ADOT Collector（收集、處理、轉發）
  ├── → AWS X-Ray（traces）
  ├── → Amazon CloudWatch（metrics / logs）
  └── → Amazon Managed Prometheus（metrics）
```

**ADOT Collector 的三個核心元件：**
```yaml
# collector-config.yaml
receivers:        # 接收資料的來源
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317   # 接收 gRPC 格式的 OTLP 資料
      http:
        endpoint: 0.0.0.0:4318   # 接收 HTTP 格式的 OTLP 資料

processors:       # 處理資料（過濾、加工、批次）
  batch:
    timeout: 1s
    send_batch_size: 50

exporters:        # 轉發到哪裡
  awsxray:        # 送到 AWS X-Ray
    region: ap-northeast-1
  awscloudwatch:  # 送到 CloudWatch
    region: ap-northeast-1

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [batch]
      exporters: [awsxray]
    metrics:
      receivers: [otlp]
      processors: [batch]
      exporters: [awscloudwatch]
```

**在 ECS 上部署 ADOT Collector（Sidecar 模式）：**
```json
// ECS Task Definition
{
  "containerDefinitions": [
    {
      "name": "my-app",
      "image": "my-app:latest",
      "environment": [
        {
          "name": "OTEL_EXPORTER_OTLP_ENDPOINT",
          "value": "http://localhost:4317"  // 送到同一個 task 裡的 collector
        }
      ]
    },
    {
      "name": "adot-collector",             // Sidecar container
      "image": "public.ecr.aws/aws-observability/aws-otel-collector:latest",
      "command": ["--config=/etc/ecs/ecs-default-config.yaml"]
    }
  ]
}
```

**在 Lambda 上使用 ADOT（Lambda Layer）：**
```bash
# 不需要自己跑 Collector，用 Lambda Layer 的方式
aws lambda update-function-configuration \
  --function-name my-function \
  --layers arn:aws:lambda:ap-northeast-1:901920570463:layer:aws-otel-python-amd64-ver-1-20-0:1 \
  --environment Variables="{
    AWS_LAMBDA_EXEC_WRAPPER=/opt/otel-instrument,
    OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
  }"
```

**Python 應用程式搭配 ADOT Collector：**
```python
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# 設定把 traces 送到 ADOT Collector（本機的 4317 port）
provider = TracerProvider()
exporter = OTLPSpanExporter(endpoint="http://localhost:4317", insecure=True)
provider.add_span_processor(BatchSpanProcessor(exporter))
trace.set_tracer_provider(provider)

tracer = trace.get_tracer(__name__)

def process_order(order_id: str):
    with tracer.start_as_current_span("process_order") as span:
        span.set_attribute("order.id", order_id)
        # 業務邏輯...
        # Span 結束後自動送到 ADOT Collector → X-Ray
```

**ADOT vs 直接用 X-Ray SDK 的差別：**
| | 直接用 X-Ray SDK | ADOT Collector |
|--|----------------|---------------|
| 綁定程度 | 綁定 AWS X-Ray | 廠商中立（OpenTelemetry 標準）|
| 換後端 | 需要改程式碼 | 只改 Collector 設定 |
| 多後端 | 不支援 | 可同時送到 X-Ray + Prometheus |
| 複雜度 | 簡單 | 需要額外部署 Collector |
| 適合場景 | 純 AWS 環境 | 混合雲或需要標準化的環境 |

## 0603

**Alembic**

Alembic 是 Python 的**資料庫遷移工具（Database Migration Tool）**，專門搭配 SQLAlchemy ORM 使用。它負責管理資料庫 schema 的版本控制——當你改了 model（例如加一個欄位、建一張新表），Alembic 會幫你產生對應的 migration script，讓資料庫跟著你的程式碼一起演進。

**為什麼需要 Alembic：**
直接用 `CREATE TABLE` 或 `ALTER TABLE` 手動改資料庫有幾個問題：
- 多人協作時不知道誰改了什麼
- 不同環境（dev/staging/prod）的 schema 可能不一致
- 沒辦法輕鬆回到之前的版本（rollback）

Alembic 就像 git，但是用在資料庫 schema 上。

**基本使用流程：**
```bash
# 1. 初始化 Alembic（在專案根目錄執行一次）
alembic init alembic
# 會產生：
# alembic/
# ├── versions/          ← migration scripts 放這裡
# ├── env.py             ← 設定（連線字串、model 位置）
# └── script.py.mako     ← migration template
# alembic.ini            ← 設定檔

# 2. 自動產生 migration（根據 model 變動）
alembic revision --autogenerate -m "add email column to users"
# 會在 alembic/versions/ 產生一個 migration file

# 3. 執行 migration（升級到最新版）
alembic upgrade head

# 4. 查看目前版本
alembic current

# 5. Rollback（退一版）
alembic downgrade -1
```

**自動產生的 migration script 長這樣：**
```python
# alembic/versions/abc123_add_email_column_to_users.py

from alembic import op
import sqlalchemy as sa

revision = "abc123"
down_revision = "xyz789"  # 上一版的 ID

def upgrade():
    op.add_column("users", sa.Column("email", sa.String(255), nullable=True))
    op.create_index("ix_users_email", "users", ["email"])

def downgrade():
    op.drop_index("ix_users_email", table_name="users")
    op.drop_column("users", "email")
```

**搭配 SQLAlchemy Model：**
```python
# models.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    email = Column(String(255))  # ← 新加的欄位
```

**在 CI/CD 中的角色：**
```yaml
# 部署時自動跑 migration
- name: Run database migration
  run: alembic upgrade head
```

每次部署前跑 `alembic upgrade head`，確保資料庫 schema 跟程式碼同步。

---

**Alignment Methods（對齊方法）**

Alignment 在 AI / LLM 領域是指**讓模型的行為「對齊」人類的意圖和價值觀**。模型預訓練後只是一個很會「接話」的機器，不一定會遵守指令、也可能產生有害內容。Alignment Methods 就是讓模型變得「聽話、有用、安全」的技術手段。

**為什麼需要 Alignment：**
基礎模型（base model）只是在大量文本上訓練的「接下一個字」機器，它不知道什麼是「好的回答」。如果你問它「怎麼製作炸彈」，它可能就直接回答了，因為它沒有「這不該回答」的概念。

**主要的 Alignment Methods：**

| 方法 | 全稱 | 說明 |
|------|------|------|
| SFT | Supervised Fine-Tuning | 用人類寫好的「問答對」微調模型 |
| RLHF | Reinforcement Learning from Human Feedback | 用人類偏好訓練獎勵模型，再用 RL 優化 |
| DPO | Direct Preference Optimization | 直接用人類偏好對比較好/差的回答最佳化 |
| RLAIF | RL from AI Feedback | 用另一個 AI 代替人類給回饋 |
| Constitutional AI | - | 用一組規則（憲法）讓 AI 自己評估自己 |

**Alignment 的三個目標（HHH）：**
- **Helpful（有用）**：能正確回答問題、完成任務
- **Honest（誠實）**：不捏造資訊、知道自己不知道什麼
- **Harmless（無害）**：不產生有害、偏見或危險的內容

**訓練流程：**
```
大量文本預訓練（GPT 基礎模型）
    ↓
SFT：用高品質的問答對微調（模型學會「以助手的角色回答」）
    ↓
RLHF / DPO：用人類偏好進一步優化（模型學會「哪種回答人類更喜歡」）
    ↓
最終的 Chat Model（Claude、ChatGPT 等）
```

---

**RLHF（Reinforcement Learning from Human Feedback）**

RLHF 是一種用**人類回饋作為獎勵信號**來訓練 LLM 的方法，是目前最主流的 Alignment 技術之一。核心思想是：讓人類告訴模型「這個回答比那個好」，然後用強化學習讓模型學會產生人類偏好的回答。

**RLHF 的三個階段：**

```
階段 1：SFT（Supervised Fine-Tuning）
  用人類寫好的高品質對話微調基礎模型
  → 模型學會「以助手的角色回答」

階段 2：訓練 Reward Model（獎勵模型）
  讓人類對同一個問題的多個回答做排序（哪個好哪個差）
  → 訓練一個模型來預測「人類會喜歡哪個回答」

階段 3：PPO 強化學習
  用 Reward Model 的分數作為獎勵
  用 PPO（Proximal Policy Optimization）演算法優化 LLM
  → 模型學會產生「高獎勵分數」的回答
```

**為什麼不直接用 SFT 就好：**
SFT 只能教模型模仿人類寫的答案（監督學習），但人類不可能為每個問題都寫出完美答案。RLHF 更高效——人類只需要「比較兩個答案哪個好」（判斷比生成容易得多），模型就能學會自己產生好的答案。

**RLHF 的局限：**
- 需要大量人類標註（昂貴且耗時）
- 獎勵模型可能被「刷分」（模型學會討好 reward model 而不是真正有用）
- 人類偏好不一定代表正確（人類也有偏見）

---

**RAG（Retrieval-Augmented Generation）**

RAG 是「檢索增強生成」，一種**讓 LLM 在回答前先去查資料**的架構。解決 LLM 的兩個核心問題：幻覺（亂編）和知識過時。

**核心概念：**
不改 LLM 本身，而是在它回答前先幫它找到相關的資料，把資料塞進 prompt 裡，讓它「有根據地回答」。

**架構流程：**
```
用戶問題：「公司的請假政策最多幾天？」
    ↓
1. Retrieval（檢索）：
   把問題轉成向量 → 去向量資料庫搜尋最相關的文件片段
   找到：「員工年假為 14 天，病假為 30 天...」
    ↓
2. Augment（增強）：
   把檢索到的文件塞進 prompt：
   "根據以下資料回答問題：[文件片段] 問題：公司的請假政策最多幾天？"
    ↓
3. Generate（生成）：
   LLM 根據提供的資料產生回答：
   「根據公司政策，年假最多 14 天，病假最多 30 天。」
```

**Python 實作（簡化版）：**
```python
from openai import OpenAI
import chromadb

# 1. 建立向量資料庫（事先把文件切塊並 embed）
chroma = chromadb.Client()
collection = chroma.create_collection("company_docs")

# 2. Retrieval：搜尋相關文件
results = collection.query(
    query_texts=["公司的請假政策"],
    n_results=3
)
context = "\n".join(results["documents"][0])

# 3. Augmented Generation：把文件塞進 prompt
client = OpenAI()
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": f"根據以下資料回答問題：\n{context}"},
        {"role": "user", "content": "公司的請假政策最多幾天？"}
    ]
)
print(response.choices[0].message.content)
```

**在 AWS 的實作（Bedrock Knowledge Base）：**
```python
import boto3

bedrock = boto3.client("bedrock-agent-runtime")

# Bedrock 幫你做完 Retrieve + Generate 的整個流程
response = bedrock.retrieve_and_generate(
    input={"text": "公司的請假政策最多幾天？"},
    retrieveAndGenerateConfiguration={
        "type": "KNOWLEDGE_BASE",
        "knowledgeBaseConfiguration": {
            "knowledgeBaseId": "XXXXXXXXXX",
            "modelArn": "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0"
        }
    }
)
print(response["output"]["text"])
```

**RAG vs Fine-Tuning 的差別：**
| | RAG | Fine-Tuning |
|--|-----|-------------|
| 知識更新 | 即時（更新文件就好）| 需要重新訓練 |
| 成本 | 低（不需要 GPU 訓練）| 高（需要大量 GPU）|
| 幻覺風險 | 低（有文件根據）| 較高 |
| 適合場景 | 公司內部知識、FAQ | 學會特定風格或技能 |

---

**Validator（驗證器）**

Validator 是負責**檢查資料是否符合預期格式和規則**的元件。在 API 開發中，Validator 確保進來的資料（request body、query params）合法，不合法就直接拒絕並回傳錯誤訊息，不讓髒資料進入業務邏輯。

**為什麼需要 Validator：**
永遠不要相信用戶端送來的資料。沒有驗證的 API 容易出現：
- 型別錯誤（預期 int 收到 string）
- 格式錯誤（email 欄位填了隨便的字）
- 安全漏洞（SQL injection、XSS）
- 業務邏輯炸掉（quantity = -1）

**用 Pydantic 做 Validation（FastAPI 最常用）：**
```python
from pydantic import BaseModel, Field, field_validator, EmailStr
from typing import Optional

class CreateOrderRequest(BaseModel):
    product_id: str = Field(..., min_length=1, max_length=50)
    quantity: int = Field(..., gt=0, le=9999)
    email: EmailStr
    note: Optional[str] = Field(None, max_length=500)

    @field_validator("product_id")
    @classmethod
    def product_id_must_be_alphanumeric(cls, v):
        if not v.replace("-", "").isalnum():
            raise ValueError("product_id must be alphanumeric")
        return v

# FastAPI 自動用這個 model 做 validation
from fastapi import FastAPI

app = FastAPI()

@app.post("/orders")
async def create_order(request: CreateOrderRequest):
    # 到這裡 request 已經驗證通過，可以安全使用
    return {"status": "created", "product_id": request.product_id}
```

**當驗證失敗時，FastAPI 自動回傳：**
```json
{
  "detail": [
    {
      "loc": ["body", "quantity"],
      "msg": "Input should be greater than 0",
      "type": "greater_than"
    }
  ]
}
```

**常見的 Validation 規則：**
| 規則 | Pydantic 寫法 | 用途 |
|------|--------------|------|
| 必填 | `Field(...)` | 不能是 null |
| 字串長度 | `min_length=1, max_length=255` | 防止空字串或超長 |
| 數字範圍 | `gt=0, le=100` | 防止負數或超大值 |
| 格式 | `EmailStr`, `HttpUrl` | email、URL 格式 |
| 正則 | `Field(pattern=r"^[A-Z]{3}$")` | 自訂格式 |
| 自訂邏輯 | `@field_validator` | 複雜的業務規則 |

---

**PII Data（Personally Identifiable Information）**

PII 是「個人可識別資訊」，指任何可以單獨或組合起來用於**辨識特定個人身份**的資料。在軟體開發中，處理 PII 需要特別小心，涉及法規遵循（GDPR、個資法）、安全措施和存取控制。

**常見的 PII 資料：**
| 類別 | 範例 |
|------|------|
| 直接識別 | 姓名、身分證字號、護照號碼 |
| 聯絡資訊 | email、電話號碼、住址 |
| 財務資訊 | 信用卡號、銀行帳號 |
| 生物特徵 | 指紋、臉部辨識資料 |
| 線上識別 | IP 地址、cookie ID、裝置 ID |
| 敏感 PII | 醫療紀錄、種族、宗教信仰 |

**在程式碼中處理 PII 的原則：**

```python
# ❌ 不好：PII 出現在 log 裡
import logging
logger = logging.getLogger(__name__)

def process_user(user):
    logger.info(f"Processing user: {user.name}, email: {user.email}, ssn: {user.ssn}")
    # PII 寫進 log，任何有 log 存取權的人都能看到

# ✓ 好：遮蔽 PII
def mask_email(email: str) -> str:
    name, domain = email.split("@")
    return f"{name[:2]}***@{domain}"

def mask_ssn(ssn: str) -> str:
    return f"***-**-{ssn[-4:]}"

def process_user(user):
    logger.info(f"Processing user: {user.id}, email: {mask_email(user.email)}")
    # 只記錄非敏感的 ID，email 做遮蔽
```

**在 AWS 上偵測和保護 PII：**

```python
# Amazon Comprehend：自動偵測文本中的 PII
import boto3

comprehend = boto3.client("comprehend", region_name="us-east-1")

response = comprehend.detect_pii_entities(
    Text="Hi, my name is John Smith. My email is john@example.com and my SSN is 123-45-6789.",
    LanguageCode="en"
)

for entity in response["Entities"]:
    print(f"Type: {entity['Type']}, Score: {entity['Score']:.2f}")
    # Type: NAME, Score: 0.99
    # Type: EMAIL, Score: 0.99
    # Type: SSN, Score: 0.99
```

**在 AI/LLM 應用中保護 PII：**
```python
# 送給 LLM 之前先把 PII 替換掉
import re

def redact_pii(text: str) -> str:
    # 替換 email
    text = re.sub(r'\b[\w.+-]+@[\w-]+\.[\w.-]+\b', '[EMAIL]', text)
    # 替換電話
    text = re.sub(r'\b\d{4}-\d{3}-\d{3}\b', '[PHONE]', text)
    # 替換身分證
    text = re.sub(r'\b[A-Z]\d{9}\b', '[ID_NUMBER]', text)
    return text

# 先 redact 再送給 LLM
user_message = "我的 email 是 neo@company.com，電話 0912-345-678"
safe_message = redact_pii(user_message)
# "我的 email 是 [EMAIL]，電話 [PHONE]"

# 然後才送給 LLM 處理
response = llm.generate(safe_message)
```

**PII 處理的最佳實踐：**
| 原則 | 做法 |
|------|------|
| 最小收集 | 只收集業務真正需要的 PII |
| 加密儲存 | PII 在資料庫中加密（at-rest encryption）|
| 傳輸加密 | 一定用 HTTPS（in-transit encryption）|
| 存取控制 | 只有需要的人/服務能存取 PII |
| 保留期限 | 不需要了就刪除，不要永久保留 |
| 稽核紀錄 | 記錄誰在什麼時候存取了 PII |

---

**Subnet Tier（子網路層級）**

Subnet Tier 是在 VPC 架構中，按照**用途和安全等級**把子網路分成不同層級的設計模式。每一層的子網路有不同的網路存取規則，形成「由外到內」的防護架構。

**常見的三層架構：**
```
Internet
    ↓
┌─────────────────────────────────────────────┐
│ VPC                                         │
│                                             │
│  ┌── Public Tier（公開層）──────────────┐    │
│  │  ALB, NAT Gateway, Bastion Host     │    │
│  │  可以直接跟 Internet 溝通            │    │
│  └─────────────────────────────────────┘    │
│            ↓                                │
│  ┌── Private Tier（私有層）─────────────┐    │
│  │  ECS Tasks, Lambda, EC2 (App Server)│    │
│  │  透過 NAT 才能出去，外面進不來       │    │
│  └─────────────────────────────────────┘    │
│            ↓                                │
│  ┌── Data Tier（資料層）───────────────┐     │
│  │  RDS, ElastiCache, DynamoDB VPC     │     │
│  │  完全隔離，只接受 Private Tier 的連線│     │
│  └─────────────────────────────────────┘    │
│                                             │
└─────────────────────────────────────────────┘
```

**每一層的 Route Table 差異：**
| Tier | Route Table | 可上網？ | 從外面進來？ |
|------|------------|---------|------------|
| Public | `0.0.0.0/0 → IGW` | 直接上網 | 可以（透過 ALB / EIP）|
| Private | `0.0.0.0/0 → NAT GW` | 透過 NAT 出去 | 不行 |
| Data | 只有 VPC 內部路由 | 不能 | 不行 |

**Terraform 範例：**
```hcl
# Public Subnet（放 ALB）
resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  map_public_ip_on_launch = true
  tags = { Name = "public-tier" }
}

# Private Subnet（放 App）
resource "aws_subnet" "private" {
  vpc_id     = aws_vpc.main.id
  cidr_block = "10.0.2.0/24"
  tags = { Name = "private-tier" }
}

# Data Subnet（放 RDS）
resource "aws_subnet" "data" {
  vpc_id     = aws_vpc.main.id
  cidr_block = "10.0.3.0/24"
  tags = { Name = "data-tier" }
}
```

**為什麼要分層：**
- **最小權限原則**：每一層只能存取它需要的資源
- **攻擊面縮減**：即使 Public Tier 被入侵，Data Tier 還有另一層保護
- **合規要求**：金融業、醫療業通常要求資料庫不能放在可直接上網的子網路

---

**K8s（Kubernetes）**

K8s 是 Kubernetes 的簡稱（K + 中間 8 個字母 + s），是一個開源的**容器編排平台**，負責自動化部署、擴展和管理容器化的應用程式。如果 Docker 是「把應用程式裝進容器」，K8s 就是「管理一大堆容器該怎麼跑、跑幾個、壞了怎麼辦」。

**為什麼需要 K8s：**
當你只有 1-2 個容器時，用 `docker run` 或 `docker-compose` 就夠了。但當你有幾十、幾百個容器分散在多台機器上，你需要：
- 自動把容器分配到不同機器（Scheduling）
- 容器掛了自動重啟（Self-healing）
- 流量增加時自動擴展（Auto-scaling）
- 不停機更新版本（Rolling Update）
- 服務之間的網路和負載均衡（Service Discovery）

**K8s 的核心概念：**
| 概念 | 說明 |
|------|------|
| Pod | 最小部署單位，一個或多個容器的集合 |
| Deployment | 管理 Pod 的副本數量和更新策略 |
| Service | 為 Pod 提供穩定的網路位址和負載均衡 |
| Node | 一台實體或虛擬機器，Pod 跑在 Node 上 |
| Cluster | 一組 Node 的集合 |
| Namespace | 邏輯隔離（例如 dev / staging / prod）|

**基本的 K8s 部署檔案：**
```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-api
spec:
  replicas: 3              # 跑 3 個 Pod
  selector:
    matchLabels:
      app: my-api
  template:
    metadata:
      labels:
        app: my-api
    spec:
      containers:
        - name: my-api
          image: my-registry/my-api:v1.2.0
          ports:
            - containerPort: 8000
          resources:
            requests:
              memory: "128Mi"
              cpu: "250m"
            limits:
              memory: "256Mi"
              cpu: "500m"
---
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: my-api-service
spec:
  selector:
    app: my-api
  ports:
    - port: 80
      targetPort: 8000
  type: LoadBalancer        # 自動建立 Load Balancer
```

**常用 kubectl 指令：**
```bash
# 部署
kubectl apply -f deployment.yaml

# 查看 Pod 狀態
kubectl get pods

# 查看 log
kubectl logs my-api-xyz123

# 進入 Pod 裡 debug
kubectl exec -it my-api-xyz123 -- bash

# 擴展副本數
kubectl scale deployment my-api --replicas=5
```

**在 AWS 上的 K8s（EKS）：**
AWS 提供 Amazon EKS（Elastic Kubernetes Service）作為託管的 K8s 服務，Control Plane 由 AWS 管理，你只需要管 Worker Node 和部署設定。

**K8s vs ECS 的選擇：**
| | K8s（EKS）| ECS |
|--|-----------|-----|
| 複雜度 | 高，學習曲線陡 | 低，AWS 原生好上手 |
| 可攜性 | 跨雲（GCP、Azure 都能跑）| 綁 AWS |
| 生態系 | 非常豐富（Helm、Istio、ArgoCD）| AWS 生態為主 |
| 適合場景 | 大規模、多雲、已有 K8s 經驗 | 純 AWS、小團隊、快速上線 |

---

**Schedule（排程）**

Schedule 在軟體工程中指的是**按照時間規則自動觸發任務**的機制。可以是定時執行腳本、定期跑報表、或是 K8s 裡按排程策略分配 Pod 到 Node。

**情境一：定時任務（Cron Schedule）**

最常見的 schedule 是用 cron 表達式定義「什麼時間跑什麼任務」。

```
Cron 表達式格式：
分 時 日 月 星期
*  *  *  *  *

# 範例
0 2 * * *       → 每天凌晨 2:00
*/5 * * * *     → 每 5 分鐘
0 9 * * 1-5     → 每週一到五早上 9:00
0 0 1 * *       → 每月 1 號午夜
```

**在 AWS 上做排程：**
```python
# EventBridge（CloudWatch Events）排程觸發 Lambda
import boto3

events = boto3.client("events")

# 每天凌晨 2 點跑一次 Lambda
events.put_rule(
    Name="daily-cleanup",
    ScheduleExpression="cron(0 2 * * ? *)",   # AWS cron 多一個「年」欄位
    State="ENABLED"
)

events.put_targets(
    Rule="daily-cleanup",
    Targets=[{
        "Id": "cleanup-lambda",
        "Arn": "arn:aws:lambda:ap-northeast-1:123456789:function:cleanup"
    }]
)
```

**情境二：K8s CronJob**
```yaml
# 每天凌晨 3 點跑一次 DB 備份
apiVersion: batch/v1
kind: CronJob
metadata:
  name: db-backup
spec:
  schedule: "0 3 * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
            - name: backup
              image: my-backup-tool:latest
              command: ["python", "backup.py"]
          restartPolicy: OnFailure
```

**情境三：K8s Scheduler（Pod 排程器）**

K8s Scheduler 負責決定「每個新建的 Pod 要放到哪台 Node 上」。它考慮：
- Node 的資源（CPU、記憶體是否足夠）
- 親和性規則（affinity：希望放在一起 / 分散開）
- 污點和容忍度（taints & tolerations：某些 Node 只接受特定的 Pod）

```yaml
# 指定 Pod 只跑在有 GPU 的 Node 上
spec:
  nodeSelector:
    gpu: "true"

# 或用更靈活的 affinity
spec:
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
          - matchExpressions:
              - key: instance-type
                operator: In
                values: ["gpu", "compute-optimized"]
```

**Python 常見的排程工具：**
| 工具 | 用途 |
|------|------|
| `crontab`（系統層）| Linux 系統排程 |
| APScheduler | Python 應用內的排程器 |
| Celery Beat | 分散式任務排程 |
| AWS EventBridge | Serverless 排程（觸發 Lambda、Step Functions）|
| Airflow | 複雜的 DAG 工作流排程 |

## 0604

**Trivy**

Trivy 是一款開源的**安全掃描工具**，由 Aqua Security 開發，專門用來掃描容器映像（container image）、檔案系統、git repo 和 IaC（Infrastructure as Code）中的**漏洞（vulnerabilities）**和**錯誤配置（misconfigurations）**。它是 CI/CD 流程中最常用的安全掃描工具之一，因為它安裝簡單、掃描快速、且不需要額外的資料庫服務。

**為什麼需要 Trivy：**
你用的 Docker base image（例如 `python:3.11`）或安裝的套件（pip、npm）可能包含已知的安全漏洞。如果不掃描就部署上線，等於把門打開讓攻擊者進來。Trivy 能在 build 階段就抓出這些問題，在漏洞進入 production 之前阻止它。

**基本使用：**
```bash
# 安裝 Trivy（macOS）
brew install trivy

# 掃描 Docker image
trivy image python:3.11-slim
# 輸出所有已知漏洞，包含嚴重程度（CRITICAL / HIGH / MEDIUM / LOW）

# 掃描本地專案的相依套件
trivy fs .
# 會掃描 requirements.txt、package.json、go.sum 等

# 只顯示 HIGH 和 CRITICAL 等級的漏洞
trivy image --severity HIGH,CRITICAL my-app:latest

# 掃描並設定門檻（有 CRITICAL 漏洞就回傳 exit code 1，讓 CI 失敗）
trivy image --exit-code 1 --severity CRITICAL my-app:latest
```

**在 CI/CD 中使用（GitHub Actions 範例）：**
```yaml
# .github/workflows/security.yml
name: Security Scan

on: [push, pull_request]

jobs:
  trivy-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build Docker image
        run: docker build -t my-app:${{ github.sha }} .

      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: my-app:${{ github.sha }}
          severity: CRITICAL,HIGH
          exit-code: 1   # 有 CRITICAL/HIGH 漏洞就讓 CI 失敗
          format: table
```

**Trivy 可以掃描的目標：**
| 目標 | 指令 | 說明 |
|------|------|------|
| Container Image | `trivy image nginx:latest` | 掃描 image 裡的 OS 套件和語言套件 |
| 檔案系統 | `trivy fs ./my-project` | 掃描 requirements.txt、package-lock.json 等 |
| Git Repo | `trivy repo https://github.com/...` | 遠端掃描 repo |
| IaC 配置 | `trivy config ./terraform/` | 掃描 Terraform、CloudFormation 的錯誤配置 |
| Kubernetes | `trivy k8s --all-namespaces` | 掃描整個 K8s cluster |

**Trivy 的掃描結果範例：**
```
python:3.11-slim (debian 12.4)
Total: 15 (HIGH: 8, CRITICAL: 7)

┌──────────────────┬────────────────┬──────────┬───────────────────────────┐
│     Library      │ Vulnerability  │ Severity │      Fixed Version        │
├──────────────────┼────────────────┼──────────┼───────────────────────────┤
│ openssl          │ CVE-2024-0727  │ HIGH     │ 3.0.13-1~deb12u1          │
│ libexpat2        │ CVE-2023-52425 │ CRITICAL │ 2.5.0-1+deb12u1           │
│ pip (METADATA)   │ CVE-2023-5752  │ MEDIUM   │ 23.3                      │
└──────────────────┴────────────────┴──────────┴───────────────────────────┘
```

**修復方式：**
- 升級 base image 到最新版（通常新版已修復）
- 升級有漏洞的套件到 Fixed Version
- 如果暫時無法修復，可以用 `.trivyignore` 忽略特定 CVE

```bash
# .trivyignore — 暫時忽略特定漏洞（需要附上原因）
# 這個漏洞不影響我們的使用方式，等下一次升級時一起修
CVE-2024-0727
```

---

**CVE（Common Vulnerabilities and Exposures）**

CVE 是一套**全球統一的資安漏洞編號系統**，由 MITRE 組織維護。每當有人發現一個新的安全漏洞，就會被指派一個 CVE 編號，作為全世界溝通這個漏洞的共通語言。

**編號格式：**
```
CVE-年份-流水號
例如：CVE-2024-0727
      CVE-2023-44487
      CVE-2021-44228（Log4Shell，史上最嚴重的漏洞之一）
```

**為什麼需要 CVE：**
假設 OpenSSL 有一個漏洞，不同的安全公司可能給它不同的名字。有了 CVE 編號，全世界的人在討論同一個漏洞時，都能明確知道在講哪一個。

**CVE 的生命週期：**
```
研究員發現漏洞
    ↓
向軟體廠商通報（Responsible Disclosure）
    ↓
廠商開發修補程式（Patch）
    ↓
漏洞被公開，分配 CVE 編號
    ↓
CVSS 評分（衡量嚴重程度）
    ↓
使用者更新軟體修補漏洞
```

**CVSS 評分（Common Vulnerability Scoring System）：**
每個 CVE 都有一個 0-10 的嚴重度分數：

| 分數 | 等級 | 說明 |
|------|------|------|
| 9.0 - 10.0 | CRITICAL | 可遠端執行任意程式碼、不需認證 |
| 7.0 - 8.9 | HIGH | 嚴重影響，但可能需要特定條件 |
| 4.0 - 6.9 | MEDIUM | 有一定風險，通常需要用戶互動 |
| 0.1 - 3.9 | LOW | 影響有限 |

**著名的 CVE 案例：**
| CVE | 名稱 | 影響 |
|-----|------|------|
| CVE-2021-44228 | Log4Shell | Java Log4j 可遠端執行任意程式碼，影響幾乎所有 Java 應用 |
| CVE-2023-44487 | HTTP/2 Rapid Reset | HTTP/2 DoS 攻擊，影響所有主要的 web server |
| CVE-2014-0160 | Heartbleed | OpenSSL 記憶體洩漏，可竊取加密金鑰 |
| CVE-2017-5754 | Meltdown | CPU 硬體漏洞，可讀取核心記憶體 |

**在工作中的實際應用：**
```bash
# 1. 收到安全通知「CVE-2024-XXXX 影響你的系統」
# 2. 去 NVD 查詢詳細資訊
#    https://nvd.nist.gov/vuln/detail/CVE-2024-XXXX

# 3. 用 Trivy 確認你的系統是否受影響
trivy image my-app:latest | grep CVE-2024-XXXX

# 4. 確認影響後升級套件
pip install --upgrade affected-package

# 5. 重新 build image 並掃描確認已修復
docker build -t my-app:patched .
trivy image my-app:patched | grep CVE-2024-XXXX
# 如果沒有輸出 → 已修復
```

**查詢 CVE 的資源：**
| 網站 | 說明 |
|------|------|
| [NVD](https://nvd.nist.gov/) | NIST 的國家漏洞資料庫（最官方）|
| [CVE.org](https://www.cve.org/) | MITRE 官方 CVE 清單 |
| [GitHub Advisory](https://github.com/advisories) | GitHub 的安全公告（跟 Dependabot 整合）|
| [Snyk Vuln DB](https://security.snyk.io/) | Snyk 的漏洞資料庫（對開發者友善）|

---

**Bash（Bourne Again Shell）**

Bash 是 Linux/macOS 上最常用的**命令列介面（Shell）**，也是一種腳本語言。它是 Unix 原始 shell（sh）的增強版本，名稱 "Bourne Again" 是 "Bourne"（原作者姓氏）的雙關語。在 DevOps 和後端開發中，幾乎所有自動化腳本、CI/CD pipeline、容器啟動腳本都用 Bash 寫。

**Shell 是什麼：**
Shell 是你和作業系統之間的「翻譯員」。你在終端機打的每個指令（`ls`、`cd`、`docker run`），都是 shell 在解讀並呼叫對應的程式。

**常見的 Shell 種類：**
| Shell | 說明 |
|-------|------|
| `sh` | 最原始的 Unix shell |
| `bash` | sh 的增強版，Linux 預設 |
| `zsh` | bash 的增強版，macOS 預設（你正在用的）|
| `fish` | 現代化 shell，語法更友善但不相容 bash |

**Bash 基本語法：**
```bash
#!/bin/bash
# ↑ Shebang：告訴系統用 bash 來執行這個腳本

# 變數（等號前後不能有空格！）
name="Alice"
port=8080
echo "Hello, $name on port $port"

# 條件判斷
if [ "$port" -eq 8080 ]; then
    echo "使用預設 port"
elif [ "$port" -gt 8080 ]; then
    echo "使用自訂 port"
else
    echo "port 太小了"
fi

# 迴圈
for file in *.py; do
    echo "處理 $file"
done

# while 迴圈
count=0
while [ $count -lt 5 ]; do
    echo $count
    count=$((count + 1))
done

# 函式
greet() {
    local name=$1   # $1 是第一個參數
    echo "Hello, $name!"
}
greet "Bob"
```

**常用在 CI/CD 和 DevOps 的 Bash 技巧：**
```bash
# 1. 錯誤處理（腳本一出錯就停止）
set -euo pipefail
# -e：任何指令失敗就停止
# -u：使用未定義的變數就報錯
# -o pipefail：pipe 中的任何失敗都算失敗

# 2. 環境變數預設值
DB_HOST=${DB_HOST:-"localhost"}    # 如果 DB_HOST 沒設定，用 "localhost"
DB_PORT=${DB_PORT:-5432}

# 3. 檢查指令是否存在
if ! command -v docker &> /dev/null; then
    echo "Error: docker is not installed"
    exit 1
fi

# 4. 等待服務就緒（Docker 裡很常用）
until pg_isready -h $DB_HOST -p $DB_PORT; do
    echo "等待 PostgreSQL 啟動..."
    sleep 2
done
echo "PostgreSQL 就緒！"

# 5. 讀取 .env 檔案
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi
```

**在 Dockerfile / Docker Compose 中的角色：**
```dockerfile
# Docker ENTRYPOINT 腳本通常是 bash
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
```

```bash
#!/bin/bash
# entrypoint.sh
set -e

echo "Running migrations..."
alembic upgrade head

echo "Starting server..."
exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
```

**Bash vs Python 腳本的選擇：**
| 場景 | 選 Bash | 選 Python |
|------|---------|-----------|
| 跑幾個指令組合 | ✓ | |
| 檔案操作、文字處理 | 簡單用 bash，複雜用 Python | ✓ |
| 複雜邏輯、資料處理 | | ✓ |
| CI/CD pipeline 腳本 | ✓ | |
| Docker entrypoint | ✓ | |
| 跨平台相容 | | ✓ |

**Bash 跟你正在用的 zsh 的差別：**
zsh 幾乎完全相容 bash 語法，多了一些方便的功能（更好的自動補全、主題、plugin），日常使用感覺一樣。寫腳本時建議用 `#!/bin/bash`（更通用），互動式使用 zsh 就好。

---

**SDD（Spec-Driven Development）**

SDD 是一種**先寫規格文件，再寫程式碼**的開發方法論。核心思想是：在動手寫任何程式碼之前，先把「要做什麼」和「怎麼做」明確地寫下來，形成一份完整的 spec（規格文件），然後依照 spec 來實作。

**在 Kiro 裡的 SDD：**
Kiro 內建了 SDD 的工作流程，讓你用結構化的方式從「模糊的想法」推進到「可執行的實作計劃」。整個流程分為三個階段：

```
1. Requirements（需求）
   → 把模糊的需求變成明確的 User Stories 和 Acceptance Criteria
   
2. Design（設計）
   → 決定技術方案、架構、資料流、API 規格
   
3. Tasks（任務）
   → 把設計拆成一個一個可執行的開發任務，形成 Todo List
```

**為什麼需要 SDD（不直接寫 code 就好嗎？）：**

| 問題 | 不用 SDD | 用 SDD |
|------|---------|--------|
| 範圍蔓延 | 邊做邊加功能，永遠做不完 | 需求事先定義清楚，有明確邊界 |
| 溝通成本 | 工程師理解跟 PM 想的不一樣 | 需求文件是共同的 truth |
| AI 協作 | AI 不知道你要什麼，亂猜 | AI 根據 spec 精確實作 |
| 品質 | 想到哪寫到哪，容易遺漏 | 有 Acceptance Criteria 可驗證 |
| 重構 | 沒有設計就直接改，容易改壞 | 有設計文件參考，改動有依據 |

**Kiro 的 SDD 流程範例：**

```
你的想法：「我要幫 API 加上分頁功能」
    ↓
Step 1 - Requirements：
  - User Story: 身為 API 使用者，我想要用 page/pageSize 取得分頁資料
  - Acceptance Criteria:
    - 支援 page 和 pageSize query params
    - 回傳包含 total、page、pageSize、data 的結構
    - pageSize 預設 20，最大 100
    - page < 1 回傳 400 Bad Request
    ↓
Step 2 - Design：
  - 技術方案：用 SQL LIMIT/OFFSET
  - Response 格式：{ total, page, pageSize, data: [...] }
  - 效能考量：total count 可能很慢，加快取
    ↓
Step 3 - Tasks：
  □ 建立 PaginationParams Pydantic model
  □ 修改 repository 層加上 offset/limit
  □ 修改 route handler 接受分頁參數
  □ 寫整合測試
  □ 更新 API 文件
```

**SDD vs 其他開發方法論的比較：**
| 方法 | 特點 | 適合情境 |
|------|------|---------|
| SDD | 先寫完整 spec 再實作 | 功能明確、有 AI 輔助時 |
| TDD | 先寫測試再寫程式 | 邏輯複雜、需要高信心 |
| BDD | 用自然語言寫行為規格 | 需要非工程師參與驗收 |
| Agile/Scrum | 迭代開發、快速交付 | 需求不確定、需要快速驗證 |

**SDD 跟 TDD 的關係：**
SDD 和 TDD 不衝突，反而互補。SDD 先定義「要做什麼」（spec），TDD 再確保「做出來的對不對」（test）。在 Kiro 中，tasks 階段產生的任務就可以包含寫測試的步驟。

**在 Kiro 裡使用 SDD 的好處：**
- AI 有了明確的 spec，生成的程式碼更準確
- 每個 task 都有具體的 acceptance criteria，可以逐一驗證
- 修改需求時，知道影響範圍（因為有文件追蹤）
- 多人協作時，spec 就是溝通的基礎


## 0607

**Vector（向量）**

在 AI / 機器學習的語境中，向量是一組數字的陣列，用來代表一段文字（或圖片、音訊）的「意思」。模型在訓練過程中學會把意思相近的東西放在接近的位置，意思不同的放遠。

**為什麼需要向量：**
電腦不能直接理解文字，只能處理數字。把文字轉成向量後，就可以用數學（計算距離、相似度）來判斷兩段文字是否意思相近。

**直觀理解：**
```
"國王" → [0.21, -0.45, 0.89, 0.12, ..., 0.33]   （幾百到幾千個數字）
"皇帝" → [0.19, -0.42, 0.91, 0.10, ..., 0.31]   （跟「國王」很接近）
"香蕉" → [-0.71, 0.33, 0.05, 0.88, ..., -0.22]  （跟「國王」很遠）
```

**向量的維度：**
- 2D 向量：`[x, y]` → 平面上的一個點
- 3D 向量：`[x, y, z]` → 空間中的一個點
- AI 的向量：`[x1, x2, ..., x1536]` → 1536 維空間中的一個點（人類無法想像，但數學可以算距離）

**在 RAG（檢索增強生成）中的應用：**
```python
# 1. 把公司文件轉成向量存到向量資料庫
documents = ["請假政策是14天...", "報帳流程是...", ...]
vectors = embedding_model.encode(documents)  # 每份文件 → 一個向量
vector_db.insert(vectors)

# 2. 用戶提問時，把問題也轉成向量
query_vector = embedding_model.encode("請假最多幾天？")

# 3. 用向量相似度搜尋最相關的文件
results = vector_db.search(query_vector, top_k=3)
# 找到「請假政策是14天...」這份文件（因為向量最接近）
```

**常見的向量相似度計算方式：**
| 方法 | 說明 | 值域 |
|------|------|------|
| Cosine Similarity | 計算兩個向量的夾角 | -1 到 1（1 = 完全相同）|
| Euclidean Distance | 計算兩個點的直線距離 | 0 到 ∞（0 = 完全相同）|
| Dot Product | 內積 | 值越大越相似 |

**常見的向量資料庫：**
| 名稱 | 特色 |
|------|------|
| Pinecone | 雲端全代管，最簡單 |
| ChromaDB | 輕量、適合本機開發 |
| pgvector | PostgreSQL 的擴充，用 SQL 查向量 |
| FAISS | Meta 出的，效能極好 |
| AWS OpenSearch | AWS 全代管，支援向量搜尋 |

---

**Docker Volume（持久化儲存空間）**

Volume 是 Docker 的持久化儲存機制，讓容器裡的資料在容器被刪除後依然保留。因為容器本身是「短暫的」——停止或刪除後裡面的檔案就消失了，需要長期保存的資料（如資料庫）必須存在 Volume 裡。

**比喻：**
```
容器 = 租來的辦公室（退租就什麼都沒了）
Volume = 你自己的保險箱（辦公室退了，保險箱裡的東西還在）
```

**基本用法：**
```yaml
# docker-compose.yml
services:
  db:
    image: postgres:16
    volumes:
      - db_data:/var/lib/postgresql/data   # 把 DB 資料存到 volume

  app:
    image: my-app
    volumes:
      - ./src:/app/src   # bind mount：把本機的 src 資料夾掛進容器

volumes:
  db_data:   # 宣告一個 named volume
```

**Volume 的兩種掛載方式：**
| 方式 | 語法 | 用途 |
|------|------|------|
| Named Volume | `db_data:/var/lib/...` | 持久化資料（DB、上傳檔案）|
| Bind Mount | `./local:/container` | 開發時同步本機程式碼到容器 |

**有 Volume vs 沒有 Volume：**
```bash
# 不加 -v：容器刪了資料還在
docker-compose down
docker-compose up    # DB 資料還在

# 加 -v：volume 也一起刪
docker-compose down -v
docker-compose up    # DB 是全新的空資料庫
```

**管理 Volume 的指令：**
```bash
docker volume ls                 # 列出所有 volume
docker volume inspect db_data    # 查看 volume 細節（存在主機的哪裡）
docker volume rm db_data         # 刪除特定 volume
docker volume prune              # 刪除所有沒在用的 volume
```

---

**Alpine（超輕量 Linux 發行版）**

Alpine Linux 是一個專為容器設計的極輕量 Linux 發行版，核心只有 5-7 MB。在 Docker 的世界裡，加上 `alpine` 後綴的 image 代表使用 Alpine 作為 base，體積會小很多。

**大小對比：**
| Base Image | 大小 |
|------------|------|
| `ubuntu:22.04` | ~77 MB |
| `python:3.11`（Debian）| ~900 MB |
| `python:3.11-slim` | ~120 MB |
| `python:3.11-alpine` | ~50 MB |
| `alpine:3.19`（純 Alpine）| ~7 MB |

**在 Dockerfile 裡的用法：**
```dockerfile
# 用 Alpine 版本的 Python
FROM python:3.11-alpine

# Alpine 用 apk 裝套件（不是 apt！）
RUN apk add --no-cache gcc musl-dev

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]
```

**Alpine 跟一般 Linux 的差別：**
| | Alpine | Debian/Ubuntu |
|--|--------|--------------|
| 套件管理 | `apk` | `apt` |
| C 語言函式庫 | musl libc | glibc |
| 大小 | 極小（5-7 MB）| 較大（77+ MB）|
| 預裝工具 | 幾乎沒有 | 有一堆 |
| 相容性 | 部分 C extension 套件有問題 | 幾乎都能跑 |

**什麼時候用 Alpine，什麼時候用 slim：**
| 情境 | 建議 |
|------|------|
| Go / Rust 應用（靜態編譯）| Alpine（完美適合）|
| Python + numpy/pandas 等 C 套件 | `slim`（避免 musl 相容性問題）|
| 需要最小攻擊面 | Alpine |
| 不確定 | 先用 `slim`，有需要再換 Alpine |

---

**curl（Client URL）**

curl 是一個在終端機發送 HTTP 請求的命令列工具。你在瀏覽器輸入網址是用圖形介面發請求，curl 是用指令做一樣的事情。幾乎每台 Linux / macOS 都內建，是開發者測試 API 最常用的工具。

**基本用法：**
```bash
# GET 請求（跟瀏覽器打開網址一樣）
curl https://api.example.com/users

# POST 請求（帶 JSON body）
curl -X POST https://api.example.com/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice", "age": 25}'

# 帶 Authorization header
curl https://api.example.com/me \
  -H "Authorization: Bearer eyJhbGciOi..."

# 只看 response header
curl -I https://google.com

# 下載檔案
curl -o file.zip https://example.com/file.zip

# 顯示完整的請求/回應過程（debug）
curl -v https://api.example.com/health
```

**常用旗標：**
| 旗標 | 意思 | 範例 |
|------|------|------|
| `-X` | 指定 HTTP method | `-X POST`、`-X DELETE` |
| `-H` | 加 Header | `-H "Content-Type: application/json"` |
| `-d` | 送 request body | `-d '{"key": "value"}'` |
| `-o` | 存成檔案 | `-o output.json` |
| `-I` | 只看 header | |
| `-v` | 顯示詳細過程 | |
| `-s` | 靜默模式 | |
| `-f` | 失敗時回傳 exit code 1 | 適合 CI health check |

**實際開發場景：**
```bash
# 測試你的 FastAPI endpoint
curl http://localhost:8000/users/1

# CI/CD 裡做 health check
curl -f http://localhost:8000/health || echo "服務掛了！"

# 在 Docker 裡等服務就緒
until curl -sf http://db:5432; do sleep 1; done
```

**curl vs 其他工具：**
| 工具 | 特色 |
|------|------|
| curl | 終端機指令，到處都有，腳本友善 |
| Postman | GUI 介面，方便組織 API 集合 |
| httpie | 更好讀的語法（`http GET ...`）|
| Python requests | 程式碼裡呼叫 API |

---

**SHA（Secure Hash Algorithm）**

SHA 是一種雜湊演算法（Hash Algorithm），能把任意大小的資料轉換成固定長度的字串（像是資料的「指紋」）。這個指紋具有單向性——你無法從指紋反推回原始資料。

**運作方式：**
```
任何輸入               → SHA-256 →  固定 64 字元的 hex 字串

"hello"               → 2cf24dba5fb0a30e26e83b2ac5b9e29e...
"hello "（多一個空格）→ 完全不同的值
5GB 的影片檔          → 同樣是 64 字元
```

**SHA 的特性：**
| 特性 | 說明 |
|------|------|
| 固定長度 | 不管輸入多大，輸出永遠一樣長 |
| 單向的 | 從 hash 推不回原本的內容 |
| 敏感的 | 改一個字元，hash 完全不同 |
| 不碰撞 | 不同輸入產生相同 hash 的機率趨近於零 |

**在開發中常見的地方：**
```bash
# 1. Git commit 的 SHA
git log --oneline
# a3f2b1c  fix: 修正登入邏輯  ← 這串就是 SHA

# 2. 驗證下載檔案的完整性
shasum -a 256 downloaded.zip
# 比對官方提供的 SHA 值

# 3. Docker image digest
docker pull python@sha256:abc123...
```

**常見版本：**
| 版本 | 輸出長度 | 狀態 |
|------|---------|------|
| SHA-1 | 40 字元 | 已不安全（Git 仍在用）|
| SHA-256 | 64 字元 | 目前主流 |
| SHA-512 | 128 字元 | 更安全但更長 |

---

**Hash（雜湊）**

Hash 是一個通用的「概念」——把資料經過某種演算法轉成固定長度的值。SHA 是 Hash 演算法的其中一種。Hash 這個詞在專案裡出現的頻率很高，有幾個不同的使用情境：

**情境一：密碼 Hashing**
```python
import hashlib
from passlib.context import CryptContext

# 不存明文密碼，存 hash 過的值
pwd_context = CryptContext(schemes=["bcrypt"])
hashed = pwd_context.hash("mypassword123")
# → "$2b$12$LJ3m4..."（bcrypt hash）

# 驗證時：拿用戶輸入的密碼 hash 一次，跟 DB 裡的比較
pwd_context.verify("mypassword123", hashed)  # True
```

**情境二：資料結構 Hash Table（字典/物件）**
```python
# Python 的 dict 底層就是 hash table
user = {"name": "Alice", "age": 25}
# 查詢 user["name"] 時，Python 用 hash("name") 算出儲存位置，O(1) 直接取值
```

**情境三：Git Commit Hash**
```bash
git show a3f2b1c   # 用 hash 值找到特定的 commit
```

**情境四：檔案完整性驗證**
```bash
# 確認下載的檔案沒被竄改
md5sum file.zip       # MD5（較舊，不安全）
sha256sum file.zip    # SHA-256（推薦）
```

**常見的 Hash 演算法：**
| 演算法 | 用途 | 安全性 |
|--------|------|--------|
| MD5 | 檔案校驗（非安全用途）| 已被破解 |
| SHA-256 | 通用安全雜湊 | 安全 |
| bcrypt | 密碼儲存 | 安全（有加鹽、慢速設計）|
| argon2 | 密碼儲存（更新）| 目前最佳 |

---

**Bash（Bourne Again Shell）**

Bash 是 Linux 上最常用的命令列 Shell，也是一種腳本語言。在專案中，所有 `.sh` 結尾的腳本、Dockerfile 的 `RUN` 指令、CI/CD pipeline 的 command 幾乎都是 Bash。

**在專案裡出現的地方：**
```dockerfile
# 1. Dockerfile
RUN bash -c "source ~/.bashrc && pip install -r requirements.txt"
ENTRYPOINT ["/bin/bash", "entrypoint.sh"]
```

```yaml
# 2. CI/CD（GitHub Actions）
steps:
  - run: bash scripts/deploy.sh
```

```bash
# 3. 腳本檔案（scripts/setup.sh）
#!/bin/bash
set -euo pipefail

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Running migrations..."
alembic upgrade head

echo "Done!"
```

**Bash 腳本的常見開頭：**
```bash
#!/bin/bash          # Shebang：告訴系統用 bash 執行
set -euo pipefail   # 安全設定：出錯就停、未定義變數報錯、pipe 失敗算失敗
```

**Bash vs Hash 的快速區分：**
| | Hash | Bash |
|--|------|------|
| 是什麼 | 演算法/運算（概念）| Shell 程式（工具）|
| 做什麼 | 把資料變成指紋 | 執行終端機指令 |
| 在哪看到 | 密碼、git SHA、檔案校驗 | `.sh` 檔、Dockerfile、CI |


## 0608

**cp（Copy）**

`cp` 是 Linux/macOS 終端機裡的「複製檔案」指令，全名就是 copy。是最基本的 shell 指令之一。

**基本用法：**
```bash
# 複製單一檔案
cp source.txt destination.txt

# 複製檔案到另一個資料夾
cp app.py /home/user/backup/

# 複製整個資料夾（需要 -r，recursive）
cp -r src/ backup_src/

# 複製並保留檔案的權限、時間戳等 metadata
cp -p important.conf /etc/

# 複製時如果目標已存在，先備份舊檔
cp --backup=numbered config.yml /etc/config.yml
```

**常用旗標：**
| 旗標 | 意思 | 用途 |
|------|------|------|
| `-r` / `-R` | 遞迴複製（整個資料夾）| 複製目錄必加 |
| `-p` | 保留 metadata（權限、時間）| 備份用 |
| `-i` | 覆蓋前詢問 | 避免誤蓋 |
| `-f` | 強制覆蓋（不詢問）| 腳本中使用 |
| `-v` | 顯示正在複製什麼 | debug 時看進度 |

**在 Dockerfile 裡的 COPY vs cp：**
```dockerfile
# Dockerfile 用 COPY（不是 cp），把本機檔案複製進 image
COPY requirements.txt /app/
COPY . /app/

# 容器裡面的操作才用 cp（因為已經在 Linux 環境裡）
RUN cp /app/config.example.yml /app/config.yml
```

**在 CI/CD 中的使用：**
```yaml
# GitHub Actions
steps:
  - run: |
      cp .env.example .env
      cp -r templates/ /opt/app/templates/
```

**cp vs mv（移動）的差別：**
| 指令 | 作用 | 原檔案 |
|------|------|--------|
| `cp` | 複製 | 還在（產生副本）|
| `mv` | 移動/重新命名 | 不見了（搬走了）|

```bash
cp a.txt b.txt    # a.txt 還在，多了一個 b.txt
mv a.txt b.txt    # a.txt 不見了，變成 b.txt
```

---

**LLM as a Judge（用 LLM 當評審）**

LLM as a Judge 是一種**用另一個 LLM 來評估 LLM 回答品質**的方法。核心想法是：讓一個強大的模型（例如 GPT-4 或 Claude）扮演「評審」角色，根據一套標準來給其他模型的輸出打分數。

**為什麼需要：**
傳統評估 LLM 回答品質的方式：
- **人工評估**：準確但貴、慢、不可規模化
- **自動指標**（BLEU、ROUGE）：快但常常跟人類判斷不一致

LLM as a Judge 是折衷方案——比人工便宜、比傳統指標更接近人類判斷。

**運作方式：**
```
你的 LLM（被評估的）   →  產出回答
    ↓
Judge LLM（評審）      →  根據評分標準給分數 + 解釋原因

Prompt 範例（給 Judge 的指令）：
"你是一個嚴格的評審。請根據以下標準評估這個回答：
 1. 正確性（0-5 分）
 2. 完整性（0-5 分）
 3. 清晰度（0-5 分）

 問題：{question}
 回答：{answer}
 
 請用 JSON 格式回傳分數和理由。"
```

**Python 實作範例：**
```python
from openai import OpenAI

client = OpenAI()

def judge_response(question: str, answer: str) -> dict:
    """用 GPT-4 當評審，評估回答品質"""
    judge_prompt = f"""你是一個 AI 回答品質評審。
請根據以下標準評估回答，每項 1-5 分：
- correctness：答案是否正確
- completeness：是否涵蓋重要面向
- clarity：是否清楚易懂

問題：{question}
回答：{answer}

用 JSON 格式回傳：{{"correctness": N, "completeness": N, "clarity": N, "reason": "..."}}"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": judge_prompt}],
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content)

# 使用
scores = judge_response(
    question="什麼是 Docker Volume？",
    answer="Volume 是 Docker 的持久化儲存空間..."
)
print(scores)
# {"correctness": 5, "completeness": 4, "clarity": 5, "reason": "回答正確且清晰..."}
```

**常見的 Judge 模式：**
| 模式 | 說明 | 適合場景 |
|------|------|---------|
| Single Answer Grading | 直接給一個回答打分 | 通用評估 |
| Pairwise Comparison | 比較兩個回答哪個好 | A/B 測試、模型比較 |
| Reference-based | 跟標準答案比較 | 有正確答案時 |

**LLM as a Judge 的限制：**
- **自我偏好**：模型傾向給自己風格的回答高分
- **位置偏差**：在 pairwise 比較時，傾向選第一個
- **不擅長數學/邏輯驗證**：Judge 也可能判斷錯
- **成本**：每次評估都要呼叫一次 LLM

**與人工評估的配合：**
通常做法是用 LLM as a Judge 做大規模自動評估，再抽樣一小部分做人工驗證，確保 Judge 的判斷跟人類一致。

---

**Promptfoo（Prompt 測試與評估框架）**

Promptfoo 是一個開源的 **LLM prompt 測試框架**，讓你像寫單元測試一樣測試你的 prompt。它能自動跑大量的測試案例，比較不同 prompt、不同模型的表現，並產生評估報告。

**為什麼需要 Promptfoo：**
開發 LLM 應用時，改一個 prompt 可能改善某些回答，卻讓其他回答變差。沒有系統性的測試，你不知道改動的影響範圍。Promptfoo 就像是 prompt 的「CI/CD」——每次修改都能跑一輪測試確認沒有退化。

**安裝與基本使用：**
```bash
# 安裝
npm install -g promptfoo
# 或
npx promptfoo@latest init

# 初始化專案
promptfoo init
# 會產生 promptfooconfig.yaml
```

**設定檔範例（promptfooconfig.yaml）：**
```yaml
# 定義要測試的 prompt
prompts:
  - "你是一個專業的客服助手。請回答以下問題：{{question}}"
  - "Answer the following customer question concisely: {{question}}"

# 定義要測試的模型（可以同時比較多個）
providers:
  - openai:gpt-4
  - openai:gpt-3.5-turbo
  - anthropic:messages:claude-3-sonnet-20240229

# 定義測試案例
tests:
  - vars:
      question: "如何退貨？"
    assert:
      - type: contains
        value: "7天"          # 回答必須包含「7天」
      - type: llm-rubric
        value: "回答要包含退貨流程步驟"   # 用 LLM as a Judge 評估

  - vars:
      question: "營業時間是？"
    assert:
      - type: contains
        value: "9:00"
      - type: not-contains
        value: "I don't know"   # 不能說不知道

  - vars:
      question: "你是誰？"
    assert:
      - type: llm-rubric
        value: "必須以客服助手的身分回答，不能透露是 AI"
```

**執行測試：**
```bash
# 跑測試
promptfoo eval

# 開啟 Web UI 看結果
promptfoo view
```

**Promptfoo 的評估方式（assert types）：**
| 類型 | 說明 | 範例 |
|------|------|------|
| `contains` | 回答必須包含特定字串 | `"7天"` |
| `not-contains` | 回答不能包含 | `"I don't know"` |
| `llm-rubric` | 用 LLM as a Judge 評估 | `"回答要友善且專業"` |
| `javascript` | 用 JS 寫自訂驗證邏輯 | `output.length < 500` |
| `similar` | 語意相似度 > 閾值 | 跟參考答案比較 |
| `cost` | API 呼叫費用不超過 | `< 0.01` |
| `latency` | 回應時間 | `< 2000`（ms）|

**實際使用情境：**
```bash
# 1. A/B 測試 prompt：比較哪個 prompt 效果好
# 2. 模型升級驗證：換模型前跑一輪確認沒有退化
# 3. 防退化：CI 裡跑 promptfoo，prompt 改壞了 CI 就失敗
# 4. Red teaming：測試 prompt 是否能被 jailbreak
```

**在 CI/CD 中使用：**
```yaml
# .github/workflows/prompt-test.yml
name: Prompt Tests
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npx promptfoo@latest eval --no-cache
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

**Promptfoo vs 其他工具：**
| 工具 | 特色 |
|------|------|
| Promptfoo | 開源、CLI、像單元測試、支援多 provider |
| LangSmith | LangChain 生態系，有 UI 追蹤 |
| Weights & Biases | ML 實驗追蹤，較重量級 |
| 手動測試 | 不可規模化 |

Promptfoo 的核心價值是讓 prompt engineering 從「憑感覺調」變成「有數據驗證的工程流程」。

