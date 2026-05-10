# AWS Bedrock AI Chatbot 實作筆記

## 專案概述

使用 **Amazon Bedrock** 和 **Python (boto3)** 建立一個 AI 聊天機器人，從 AWS Console 探索基礎模型，到透過 API 呼叫，最後實作具備對話記憶的多輪聊天機器人。

---

## 使用的技術與服務

| 技術 / 服務 | 說明 |
|---|---|
| **Amazon Bedrock** | AWS 全託管服務，提供 100+ 基礎模型的統一 API 存取 |
| **Amazon Nova 2 Lite** | Amazon 自家輕量基礎模型，速度快、成本低（$0.00006 / 1K tokens） |
| **AWS CloudShell** | 瀏覽器內建終端機，預裝 Python 和 boto3，免本地設定 |
| **boto3** | AWS 官方 Python SDK，讓 Python 腳本與 AWS 服務互動 |
| **Bedrock Converse API** | Bedrock 統一對話介面，同一套程式碼可對接任何基礎模型 |

---

## 什麼是 SDK？

**SDK（Software Development Kit，軟體開發套件）** 是一組工具、函式庫和文件的集合，讓開發者可以用特定程式語言輕鬆操作某個平台或服務，不需要自己處理底層的 HTTP 請求、認證、錯誤處理等細節。

**boto3 就是 AWS 的 Python SDK**，它幫你把這樣的原始 HTTP 請求：

```
POST https://bedrock-runtime.us-east-1.amazonaws.com/model/amazon.nova-lite-v1:0/converse
Authorization: AWS4-HMAC-SHA256 ...
Content-Type: application/json
{ "messages": [...] }
```

包裝成一行 Python：

```python
client.converse(modelId="amazon.nova-lite-v1:0", messages=messages)
```

**SDK 的核心價值：**
- 不用手寫 HTTP 請求和 AWS 簽名認證
- 自動處理錯誤重試、回應解析
- 有型別提示和文件，開發體驗好
- 每個 AWS 服務（S3、EC2、Bedrock...）都有對應的 client，介面一致

> 類比：SDK 就像餐廳的服務生，你只需要說「我要一份牛排」，不需要自己跑進廚房操作每個步驟。

---

## 執行指令整理

### 環境確認

```bash
# 確認 Python 版本
python3 --version

# 確認 boto3 是否安裝
python3 -c "import boto3; print(boto3.__version__)"
```

### 建立與執行腳本

```bash
# 建立第一個腳本（單次 API 呼叫）
nano bedrock_chat.py

# 執行第一個腳本
python3 bedrock_chat.py

# 建立第二個腳本（多輪對話聊天機器人）
nano bedrock_chat_revised.py

# 執行聊天機器人
python3 bedrock_chat_revised.py

# 修改溫度參數後重新執行
nano bedrock_chat_revised.py
python3 bedrock_chat_revised.py
```

### nano 編輯器操作

```
Ctrl+O → Enter   # 儲存檔案
Ctrl+X           # 離開 nano
方向鍵            # 移動游標（不能用滑鼠點擊）
```

---

## 程式碼說明

### Step 1：單次 API 呼叫 (`bedrock_chat.py`)

```python
import boto3

# 1. 連接 Amazon Bedrock
client = boto3.client("bedrock-runtime", region_name="us-east-1")

# 2. 指定使用的模型
model_id = "amazon.nova-lite-v1:0"

# 3. 建立提示訊息（Converse API 格式）
messages = [
    {
        "role": "user",
        "content": [{"text": "What is cloud computing? Explain in 2 sentences."}]
    }
]

# 4. 送出請求並取得回應
response = client.converse(modelId=model_id, messages=messages)

# 5. 解析並印出回應文字
response_text = response["output"]["message"]["content"][0]["text"]
print(response_text)
```

**重點說明：**
- `boto3.client("bedrock-runtime")` — 建立 Bedrock Runtime 的連線
- `messages` 格式：每則訊息包含 `role`（誰在說話）和 `content`（訊息內容）
- `client.converse()` — 呼叫 Converse API，回傳巢狀字典
- 回應路徑：`response["output"]["message"]["content"][0]["text"]`

---

### Step 2：多輪對話聊天機器人 (`bedrock_chat_revised.py`)

```python
import boto3

# 1. 連接 Bedrock 並選擇模型
client = boto3.client("bedrock-runtime", region_name="us-east-1")
model_id = "amazon.nova-lite-v1:0"

# 2. 設定系統提示（給聊天機器人一個角色）
system_prompt = [{"text": "You are a friendly cloud computing tutor. Explain concepts simply and use analogies."}]

# 3. 儲存對話歷史
messages = []

# 4. 開始對話迴圈
print("Chatbot ready! Type 'quit' to exit.")

while True:
    user_input = input("You: ")
    if user_input.lower() in ["quit", "exit"]:
        print("Goodbye!")
        break

    # 5. 將使用者訊息加入對話歷史
    messages.append({"role": "user", "content": [{"text": user_input}]})

    # 6. 送出完整對話歷史給 Bedrock
    response = client.converse(
        modelId=model_id,
        messages=messages,
        system=system_prompt,
        inferenceConfig={
            "temperature": 0.7,   # 0.0 = 可預測，1.0 = 有創意
            "topP": 0.9,          # 控制詞彙多樣性
            "maxTokens": 512      # 最大回應長度
        }
    )

    # 7. 儲存 AI 回應並印出
    assistant_message = response["output"]["message"]
    messages.append(assistant_message)

    print(f"Bot: {assistant_message['content'][0]['text']}")
```

---

## 核心概念

### Foundation Model（基礎模型）
大型 AI 模型，預先用海量資料訓練完成。不需要自己從頭訓練（成本數百萬美元），直接透過 API「租用智慧」。

### System Prompt（系統提示）
在對話開始前給 AI 的「工作說明書」，定義它的角色和行為方式。不會出現在對話歷史中，但每次 API 呼叫都會帶上。

### 對話記憶（Conversation History）
Bedrock API 本身是無狀態的（stateless），每次呼叫都是獨立的。要實現多輪對話，需要在程式端維護 `messages` 列表，每次呼叫都把完整歷史送過去，讓模型看到完整上下文。

### Inference Parameters（推論參數）

| 參數 | 範圍 | 說明 |
|---|---|---|
| `temperature` | 0.0 ~ 1.0 | 控制創意程度。低 = 精確可預測，高 = 多樣有創意 |
| `topP` | 0.0 ~ 1.0 | 控制詞彙多樣性，與 temperature 搭配使用 |
| `maxTokens` | 整數 | 限制回應最大長度（約等於字數） |

**實際應用：**
- 客服機器人 → 低 temperature（0.1）：一致、精確的答案
- 創意寫作工具 → 高 temperature（0.9）：多樣、有創意的輸出

### Converse API
Bedrock 的統一對話介面，同一套程式碼可以對接任何基礎模型（Nova、Claude、Llama 等），不需要針對每個模型寫不同格式。

---

## 架構流程

```
使用者輸入
    ↓
Python 腳本（CloudShell）
    ↓  boto3 API 呼叫
Amazon Bedrock（Converse API）
    ↓
Amazon Nova 2 Lite（基礎模型）
    ↓
AI 回應 → 印出到終端機
```

---

## 實作步驟摘要

1. **AWS Console** → 切換到 `us-east-1` 區域
2. **Amazon Bedrock** → Model catalog 瀏覽可用模型
3. **Chat playground** → 用 Nova 2 Lite 測試提示詞
4. **CloudShell** → 確認 Python 和 boto3 環境
5. **bedrock_chat.py** → 單次 API 呼叫，驗證連線
6. **bedrock_chat_revised.py** → 加入系統提示、對話迴圈、推論參數
7. **調整 temperature** → 觀察 0.7 vs 0.1 的回應差異
8. **（進階）bedrock_chat_guardrail.py** → 加入 Guardrails 過濾有害內容

---

## 費用說明

- Amazon Bedrock：按 API 呼叫計費，本專案總費用 < $0.01
- AWS CloudShell：免費
- 無常駐伺服器，停止呼叫 API 後即無持續費用
