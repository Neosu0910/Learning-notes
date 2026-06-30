"""
Python Core Practice — 從你現在的程度往上一層
執行: python 01_python_core.py
"""

# ================================================================
# PART A: Type Hints (型別標注)
# ================================================================
# 你已經知道 def 和 return，但真實 codebase 每個函式都有型別標注
# 這讓你一眼看懂「這函式吃什麼、吐什麼」
#
# 語法: def 函式名(參數: 型別) -> 回傳型別:
#
# 常見型別:
#   str, int, float, bool
#   list[str]       ← 字串的 list
#   dict[str, int]  ← key 是 str, value 是 int
#   str | None      ← 可能是 str 也可能是 None (Python 3.10+)
#   Any             ← 任意型別 (from typing import Any)


# 範例: 有型別標注的版本
def greet(name: str) -> str:
    return f"Hello, {name}!"

result: str = greet("Leo")
print(result)


# TODO A1: 把你之前寫的 cal 函式加上型別標注
# 原本: def cal(num):
# 改成: def cal(num: int) -> int:  ← 要改成有 return 的版本

def cal(num: int) -> int:
    # 你的版本只有 print，但真實 code 需要 return 值讓別人用
    # 改寫: 把 sum 計算完後 return，不要 print
    sum=0
    for x in range(num):
        sum=sum+x
    return (sum)


# 驗證你的實作:
print(cal(30))   # 應該印出 435
# print(cal(5))    # 應該印出 10  (0+1+2+3+4)


# TODO A2: 寫一個有型別標注的函式，接收一個 list[int]，回傳最大值
def find_max(numbers: list[int]) -> int:
    max_value=numbers[0]
    for x in (numbers):
        if x>max_value:
            max_value=x
    return(max_value)

print(find_max([0,2,4,6]))     
    


# TODO A3: 回傳值可能是 None 的情況
# 在 codebase 裡很常見: 找到東西回傳，找不到回傳 None
def find_word(text: str, keyword: str) -> str | None:
    """在 text 中找 keyword，找到回傳 keyword，找不到回傳 None"""
    if keyword in text:
        return keyword
    return None

# 驗證:
print(find_word("hello world", "world"))   # -> "world"
print(find_word("hello world", "python"))  # -> None


# ================================================================
# PART B: Class 進階 — 讓你的 class 更像真實 codebase
# ================================================================
# 你已經會 __init__ 和 self，但真實 code 還有:
#   1. 方法回傳 self (讓人知道型別)
#   2. __repr__ (讓 print 好看)
#   3. 屬性有型別標注


# 範例: 真實 codebase 的 class 風格
class Point:
    def __init__(self, x: float, y: float) -> None:  # ← __init__ 回傳 None
        self.x = x
        self.y = y

    def __repr__(self) -> str:  # ← 讓 print(point) 有意義
        return f"Point(x={self.x}, y={self.y})"

    def distance_to_origin(self) -> float:
        return ((self.x ** 2) + (self.y ** 2)) ** 0.5


p = Point(3.0, 4.0)
print(p)               # Point(x=3.0, y=4.0)
print(p.distance_to_origin())  # 5.0


# TODO B1: 設計一個 Message class，對應 codebase 中的訊息概念
# 欄位:
#   - role: str  ("user" 或 "assistant")
#   - content: str
#   - blocked: bool = False  ← 預設是 False
#
# 方法:
#   - __repr__: 印出 "Message(role=..., content=...前20字...)"
#   - is_user() -> bool: 回傳 role == "user"
#   - block() -> None: 把 self.blocked 設為 True，self.content 改成 "[BLOCKED]"

class Message:
    def __init__(self, role: str, content: str) -> None:
        self.role = role
        self.content = content
        self.blocked: bool = False

    def __repr__(self) -> str:
        return f"Message(role={self.role},content={self.content[:20]})"

    def is_user(self) -> bool:
        return self.role == "user"

    def block(self) -> None:
         self.content = "[BLOCKED]"
         self.blocked = True


# 驗證:
m = Message("user", "Hello, how are you?")
print(m)              # Message(role=user, content=Hello, how are you?)
print(m.is_user())    # True
m.block()
print(m.content)      # [BLOCKED]
print(m.blocked)      # True


# ================================================================
# PART C: Exception Handling (例外處理)
# ================================================================
# 真實 codebase 到處都有 try/except
# 你在 guardrail_practice.py 會看到很多
#
# 語法:
#   try:
#       有可能出錯的程式碼
#   except SomeError as e:
#       出錯時怎麼處理
#   except (TypeError, ValueError):
#       可以同時 catch 多種
#   finally:
#       不管有沒有錯都會執行

# 範例:
def safe_divide(a: float, b: float) -> float | None:
    try:
        return a / b
    except ZeroDivisionError:
        print("Cannot divide by zero")
        return None

print(safe_divide(10, 2))   # 5.0
print(safe_divide(10, 0))   # None


# TODO C1: 實作 safe_get_index
# 從 list 取得指定 index 的值，index 超出範圍回傳 None
def safe_get_index(items: list, index: int):
    try:
        return items[index]
    except IndexError:
        return None

# 驗證:
print(safe_get_index([10, 20, 30], 1))   # 20
print(safe_get_index([10, 20, 30], 99))  # None


# TODO C2: 實作 parse_int
# 把字串轉成 int，失敗時回傳 None
def parse_int(text: str) -> int | None:
    try:
        return int(text)
    except (ValueError, TypeError):
        return None

# 驗證:
print(parse_int("42"))     # 42
print(parse_int("hello"))  # None
print(parse_int("3.14"))   # None


# TODO C3: 實作 validate_role
# 若 role 不是 "user" 或 "assistant"，raise ValueError
# 參考真實 codebase: GuardrailManager.__init__ 中有許多 validate 邏輯
def validate_role(role: str) -> None:
    allowed = {"user", "assistant"}
    if role not in allowed:
        raise ValueError(f"Invalid role: {role}")

# 驗證:
validate_role("user")       # 不會報錯
validate_role("assistant")  # 不會報錯
try:
    validate_role("hacker")
except ValueError as e:
    print(f"Caught: {e}")   # Caught: Invalid role: hacker


# ================================================================
# PART D: dict 進階 — codebase 中最常用的資料結構
# ================================================================
# 真實 API response 全是 dict，你要能快速讀懂和操作

# 模擬一個 guardrail API response (真實格式)
fake_response = {
    "action": "GUARDRAIL_INTERVENED",
    "outputs": [{"text": "很抱歉，我無法回答這個問題。"}],
    "assessments": [
        {
            "topicPolicy": {
                "topics": [
                    {"name": "violence", "action": "BLOCKED"},
                    {"name": "finance", "action": "ALLOWED"},
                ]
            },
            "contentPolicy": {
                "filters": [
                    {"type": "HATE", "action": "BLOCKED"}
                ]
            }
        }
    ]
}

# TODO D1: 從 fake_response 取出 output 文字
# 答案應該是 "很抱歉，我無法回答這個問題。"
def get_output_text(response: dict) -> str | None:
    try:
        return response["outputs"][0]["text"]
    except (KeyError, IndexError):
        return None

print(get_output_text(fake_response))  # 很抱歉，我無法回答這個問題。


# TODO D2: 從 fake_response 找出所有 action == "BLOCKED" 的 topic name
# 答案應該是 ["violence"]
def get_blocked_topics(response: dict) -> list[str]:
    blocked = []
    topics = response["assessments"][0]["topicPolicy"]["topics"]
    for topic in topics:
        if topic["action"] == "BLOCKED":
            blocked.append(topic["name"])
    return blocked

print(get_blocked_topics(fake_response))  # ['violence']


# TODO D3: 判斷 response 是否被 guardrail 攔截
BLOCK_FLAG = "GUARDRAIL_INTERVENED"

def is_blocked(response: dict) -> bool:
    return response.get("action") == BLOCK_FLAG

print(is_blocked(fake_response))          # True
print(is_blocked({"action": "NONE"}))     # False


# ================================================================
# SELF CHECK: 看這段 code，你能回答嗎？
# ================================================================
# 下面是從真實 codebase 截出的片段 (guardrail.py line 229-236)
# 不用執行，只要能「讀懂」就代表你這部分過關了
"""
if response["action"] == BEDROCK_GUARDRAIL_BLOCK_FLAG:
    violations_str = self._extract_violations(response)
    return ValidateResult(
        intervened=True,
        output_text=response["outputs"][0]["text"],
        reason=f"Content blocked: {violations_str}",
    )
return ValidateResult(intervened=False, output_text=None, reason=CONTENT_PASSED_VALIDATION)
"""
# Q1: response["outputs"][0]["text"] 是什麼意思？
#     → response 是 dict，"outputs" 的值是 list，[0] 取第一個元素，["text"] 取它的 text 欄位

# Q2: 為什麼有兩個 return？
#     → if 成立走第一個 return，不成立走第二個 return
#       在 codebase 中這叫 early return，避免巢狀 if/else

# Q3: f"Content blocked: {violations_str}" 是什麼？
#     → f-string，把變數嵌入字串，你在 TODO A1 驗證區看到過


if __name__ == "__main__":
    print("\n=== 執行到這裡代表語法沒有明顯錯誤 ===")
    print("把每個 TODO 的 pass 換成實作，然後取消 # 驗證區的 print 來測試")
