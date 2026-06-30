"""
Python dict.get() 完整練習 — 真實 codebase 中最常用的安全取值方式
執行: python 03_dict_get.py
"""

# ================================================================
# PART A: 為什麼需要 .get()？
# ================================================================
# 用 dict["key"] 取值，如果 key 不存在 → 直接 crash (KeyError)
# 用 dict.get("key") 取值，如果 key 不存在 → 回傳 None，不會 crash
# 用 dict.get("key", 預設值) → key 不存在時回傳你指定的預設值
#
# 真實情境：API response 的欄位不一定每次都有
# 例如有的 response 有 "error" 欄位，有的沒有
# 你不能假設它一定存在

# ================================================================
# 基本比較
# ================================================================

user = {"name": "Leo", "age": 25}

# 危險寫法：key 不存在就 crash
# print(user["email"])  ← KeyError: 'email'

# 安全寫法：
print(user.get("name"))       # "Leo"    ← key 存在，正常回傳
print(user.get("email"))      # None     ← key 不存在，回傳 None
print(user.get("email", "N/A"))  # "N/A" ← key 不存在，回傳預設值


# ================================================================
# PART B: .get() 的三種用法
# ================================================================

config = {
    "model": "claude-3",
    "temperature": 0.7,
    "max_tokens": None,  # ← 注意: key 存在但值是 None
}

# 用法 1: get(key) — 不存在回傳 None
print(config.get("model"))        # "claude-3"
print(config.get("timeout"))      # None (key 不存在)

# 用法 2: get(key, default) — 不存在回傳 default
print(config.get("timeout", 30))  # 30 (key 不存在，用預設值)

# 用法 3: ⚠️ 陷阱！key 存在但值是 None 時，get 回傳 None，不是 default
print(config.get("max_tokens", 1000))  # None ← 不是 1000！因為 key 存在
# 這是新手最常搞混的地方


# ================================================================
# PART C: .get() vs [] vs in — 什麼時候用哪個？
# ================================================================

response = {"status": 200, "data": {"users": []}}

# 1. 你「確定」key 一定存在 → 用 []
status = response["status"]  # 安全，因為你知道一定有

# 2. key「可能不存在」→ 用 .get()
error = response.get("error")  # None，不 crash

# 3. 你需要根據「有沒有這個 key」做不同邏輯 → 用 in
if "error" in response:
    print(f"Error: {response['error']}")
else:
    print("No error")


# ================================================================
# PART D: 巢狀 dict 的安全取值
# ================================================================
# 真實 API response 通常是多層巢狀
# response["data"]["users"][0]["name"] ← 任何一層不存在就 crash

api_response = {
    "action": "GUARDRAIL_INTERVENED",
    "outputs": [{"text": "已被攔截"}],
    "assessments": [
        {
            "topicPolicy": {
                "topics": [
                    {"name": "violence", "action": "BLOCKED"}
                ]
            }
        }
    ]
}

# 危險：一路 [] 取到底
# text = api_response["outputs"][0]["text"]  # 如果 outputs 是空 list 就爆了

# 安全做法 1：逐層 .get() + 檢查
def safe_get_output(resp: dict) -> str:
    outputs = resp.get("outputs")   # 可能是 None
    if not outputs:                 # None 或 []
        return "No output"
    first = outputs[0]              # 這時才安全取 [0]
    return first.get("text", "No text")

print(safe_get_output(api_response))          # "已被攔截"
print(safe_get_output({"outputs": []}))       # "No output"
print(safe_get_output({}))                    # "No output"


# 安全做法 2：try/except 包起來 (簡單粗暴但有效)
def safe_get_output_v2(resp: dict) -> str:
    try:
        return resp["outputs"][0]["text"]
    except (KeyError, IndexError, TypeError):
        return "No output"


# ================================================================
# PART E: .get() 搭配條件判斷 — 真實 pattern
# ================================================================

# Pattern 1: 檢查某個 flag 是否為特定值
def is_blocked_response(resp: dict) -> bool:
    """判斷 response 是否被 guardrail 攔截"""
    return resp.get("action") == "GUARDRAIL_INTERVENED"

print(is_blocked_response(api_response))  # True
print(is_blocked_response({}))            # False (None != "GUARDRAIL_INTERVENED")


# Pattern 2: 取值後給預設行為
def get_model_config(config: dict) -> dict:
    """取得 model 設定，缺少的欄位用預設值補"""
    return {
        "model": config.get("model", "claude-3-sonnet"),
        "temperature": config.get("temperature", 0.7),
        "max_tokens": config.get("max_tokens", 1024),
        "stream": config.get("stream", False),
    }

my_config = {"model": "claude-3-haiku", "stream": True}
full_config = get_model_config(my_config)
print(full_config)
# {'model': 'claude-3-haiku', 'temperature': 0.7, 'max_tokens': 1024, 'stream': True}


# Pattern 3: 用 .get() 做 fallback chain（備援鏈）
def get_username(user_data: dict) -> str:
    """依序嘗試 display_name → username → email → 'Anonymous'"""
    return (
        user_data.get("display_name")
        or user_data.get("username")
        or user_data.get("email")
        or "Anonymous"
    )

print(get_username({"email": "leo@example.com"}))         # "leo@example.com"
print(get_username({"display_name": "Leo"}))              # "Leo"
print(get_username({}))                                   # "Anonymous"


# ================================================================
# PART F: TODO 練習
# ================================================================

# 模擬資料
student_record = {
    "name": "Alice",
    "grades": {"math": 92, "english": 85},
    "clubs": ["coding", "basketball"],
    "graduated": False,
}

aws_event = {
    "source": "aws.ecs",
    "detail": {
        "clusterArn": "arn:aws:ecs:us-east-1:123456:cluster/prod",
        "taskArn": "arn:aws:ecs:us-east-1:123456:task/abc123",
        "lastStatus": "STOPPED",
        "stoppedReason": "Essential container exited",
        "containers": [
            {"name": "app", "exitCode": 1, "reason": "OOM"},
            {"name": "sidecar", "exitCode": 0, "reason": ""},
        ]
    }
}

guardrail_result = {
    "action": "GUARDRAIL_INTERVENED",
    "outputs": [{"text": "I cannot help with that."}],
    "assessments": [
        {
            "topicPolicy": {
                "topics": [
                    {"name": "harmful_content", "action": "BLOCKED"},
                    {"name": "finance", "action": "NONE"},
                ]
            },
            "contentPolicy": {
                "filters": [
                    {"type": "VIOLENCE", "confidence": "HIGH", "action": "BLOCKED"},
                    {"type": "HATE", "confidence": "LOW", "action": "NONE"},
                ]
            }
        }
    ]
}


# ------------------------------------------------------------------
# TODO F1: 安全取得學生的 science 成績，沒有就回傳 0
# ------------------------------------------------------------------
def get_science_grade(record: dict) -> int:
    pass

# print(get_science_grade(student_record))  # 0 (沒有 science)
# print(get_science_grade({"grades": {"science": 78}}))  # 78


# ------------------------------------------------------------------
# TODO F2: 取得 AWS event 的 stoppedReason，沒有就回傳 "Unknown"
# 注意: detail 這層也可能不存在
# ------------------------------------------------------------------
def get_stopped_reason(event: dict) -> str:
    pass

# print(get_stopped_reason(aws_event))   # "Essential container exited"
# print(get_stopped_reason({}))          # "Unknown"
# print(get_stopped_reason({"detail": {}}))  # "Unknown"


# ------------------------------------------------------------------
# TODO F3: 找出 AWS event 中 exitCode != 0 的 container names
# 如果 containers 不存在就回傳空 list
# ------------------------------------------------------------------
def get_failed_containers(event: dict) -> list[str]:
    pass

# print(get_failed_containers(aws_event))  # ["app"]
# print(get_failed_containers({}))         # []


# ------------------------------------------------------------------
# TODO F4: 從 guardrail_result 取出所有被 BLOCKED 的 filter types
# 路徑: assessments[0] → contentPolicy → filters → action == "BLOCKED" 的 type
# 任何一層不存在就回傳空 list
# ------------------------------------------------------------------
def get_blocked_filters(result: dict) -> list[str]:
    pass

# print(get_blocked_filters(guardrail_result))  # ["VIOLENCE"]
# print(get_blocked_filters({}))                # []


# ------------------------------------------------------------------
# TODO F5: 實作一個通用的 safe nested get
# 接收一個 dict 和一串 keys，逐層取值，任何一層失敗回傳 default
#
# 例如: safe_nested_get(data, ["a", "b", "c"], default="N/A")
# 等於安全版的 data["a"]["b"]["c"]
# ------------------------------------------------------------------
def safe_nested_get(data: dict, keys: list[str], default=None):
    pass

# print(safe_nested_get(aws_event, ["detail", "lastStatus"]))           # "STOPPED"
# print(safe_nested_get(aws_event, ["detail", "missing", "key"]))       # None
# print(safe_nested_get(aws_event, ["detail", "missing"], default="?")) # "?"
# print(safe_nested_get({}, ["a", "b"]))                                # None


# ------------------------------------------------------------------
# TODO F6: 實作 merge_with_defaults
# 給一個 user_config 和 defaults dict，用 defaults 填補 user_config 缺少的欄位
# 已存在的欄位不要覆蓋（包括值是 None 或 False 的情況）
#
# 提示: 用 "key in dict" 判斷 key 是否存在，而不是 .get()
# ------------------------------------------------------------------
def merge_with_defaults(user_config: dict, defaults: dict) -> dict:
    pass

# defaults = {"model": "claude-3", "temperature": 0.7, "stream": False, "timeout": 30}
# user = {"model": "gpt-4", "stream": True}
# print(merge_with_defaults(user, defaults))
# → {"model": "gpt-4", "stream": True, "temperature": 0.7, "timeout": 30}

# 陷阱測試: user 的值是 None 或 False 也不應該被覆蓋
# user2 = {"model": "claude", "temperature": None, "stream": False}
# print(merge_with_defaults(user2, defaults))
# → {"model": "claude", "temperature": None, "stream": False, "timeout": 30}


# ================================================================
# PART G: .get() 的近親 — 其他安全取值方法
# ================================================================

# 1. dict.setdefault(key, default)
# 跟 .get() 類似，但如果 key 不存在，會「同時寫入」dict
cache = {}
cache.setdefault("users", []).append("Alice")
cache.setdefault("users", []).append("Bob")
print(cache)  # {"users": ["Alice", "Bob"]}
# ↑ 很適合用在「初始化 + 累加」的場景

# 2. collections.defaultdict
from collections import defaultdict
word_count: dict[str, int] = defaultdict(int)  # 預設值是 0
for word in ["apple", "banana", "apple"]:
    word_count[word] += 1
print(dict(word_count))  # {'apple': 2, 'banana': 1}


# ================================================================
# SELF CHECK
# ================================================================
# 看完這段 code，你應該能回答:
#
# Q1: response.get("action") == "BLOCKED" 和 response["action"] == "BLOCKED" 差在哪？
#     → .get() 在 key 不存在時回傳 None，比較結果是 False，不 crash
#       [] 在 key 不存在時直接 KeyError crash
#
# Q2: config.get("timeout", 30) 什麼時候回傳 30？
#     → 只有 "timeout" 這個 key 完全不存在時
#       如果 key 存在但值是 None，回傳的是 None 不是 30！
#
# Q3: 什麼時候該用 [] 而不是 .get()？
#     → 你「確定」key 一定存在，而且如果不存在就是 bug 需要 crash 告訴你


if __name__ == "__main__":
    print("\n=== 執行完成 ===")
    print("把 TODO 的 pass 換成實作，取消 # 驗證區的 print 來測試")
