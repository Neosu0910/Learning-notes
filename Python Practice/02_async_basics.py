"""
Async/Await 從零開始 — 對應真實 codebase 的 streaming 和 guardrail 邏輯
執行: python 02_async_basics.py
"""

import asyncio

# ================================================================
# PART A: 為什麼需要 async？
# ================================================================
# 想像你在餐廳點餐:
#   同步 (sync):  點完餐 → 站在廚房門口等 → 拿到餐 → 去點飲料
#   非同步 (async): 點完餐 → 去點飲料 → 等餐的同時順便拿餐具 → 餐好了再取
#
# 真實 codebase 的 guardrail 流程:
#   1. 把文字送給 AWS Bedrock API (網路請求，要等)
#   2. 在等的期間可以做別的事
#   3. API 回來了再處理結果
#
# async/await 就是 Python 處理「等待」的語法


# ================================================================
# PART B: 基本語法
# ================================================================

# 一般函式: def
def sync_hello() -> str:
    return "Hello (sync)"

# 非同步函式: async def
async def async_hello() -> str:
    return "Hello (async)"

# 執行 async 函式必須用 asyncio.run() 或在另一個 async 函式裡用 await
# print(async_hello())    ← 錯! 這只會印出 coroutine object
# print(await async_hello())  ← 對! 但只能在 async def 裡用


async def main_b() -> None:
    # await 告訴 Python: 「這裡要等，等的時候可以去做別的」
    result = await async_hello()
    print(result)

asyncio.run(main_b())


# ================================================================
# PART C: await 讓你「暫停等待」
# ================================================================

async def fetch_data(name: str, delay: float) -> str:
    """模擬一個需要等待的 API 呼叫"""
    print(f"  開始取得 {name} 的資料...")
    await asyncio.sleep(delay)   # ← 等待 delay 秒 (模擬網路延遲)
    print(f"  {name} 資料回來了!")
    return f"Data from {name}"


async def main_c() -> None:
    print("=== PART C: await ===")

    # 一個一個等: 總共要 0.3s
    print("依序執行:")
    r1 = await fetch_data("guardrail", 0.1)
    r2 = await fetch_data("llm", 0.2)
    print(f"  結果: {r1}, {r2}")

asyncio.run(main_c())


# ================================================================
# PART D: asyncio.gather — 同時等多個
# ================================================================

async def main_d() -> None:
    print("\n=== PART D: 同時等待 ===")

    # asyncio.gather 同時跑多個，總共只要最長的那個時間
    results = await asyncio.gather(
        fetch_data("guardrail", 0.1),
        fetch_data("llm", 0.2),
    )
    print(f"  全部結果: {results}")

asyncio.run(main_d())


# ================================================================
# PART E: asyncio.wait_for — 加上 timeout
# ================================================================
# 這是 guardrail_practice.py 的核心概念
# 真實 code (guardrail.py line 442):
#   blocked_event = await asyncio.wait_for(_collect(), timeout=timeout)

async def slow_api_call() -> str:
    await asyncio.sleep(5)   # 模擬很慢的 API
    return "finally done"

async def main_e() -> None:
    print("\n=== PART E: timeout ===")

    try:
        result = await asyncio.wait_for(slow_api_call(), timeout=0.1)
        print(f"  結果: {result}")
    except TimeoutError:
        print("  API 太慢了! TimeoutError 被 catch 到")
        print("  → 真實 codebase 在這裡回傳 refusal_message")

asyncio.run(main_e())


# ================================================================
# PART F: asyncio.to_thread — 在 async 裡執行 sync 函式
# ================================================================
# 問題: boto3 (AWS SDK) 是 sync 的，但我們的 code 是 async
# 解法: asyncio.to_thread 把 sync 函式丟到另一個 thread 執行，不阻塞主 loop
#
# 真實 code (guardrail.py line 373):
#   response = await asyncio.to_thread(
#       self.bedrock_runtime.client.apply_guardrail, ...
#   )

import time

def sync_heavy_computation(n: int) -> int:
    """模擬一個費時的 sync 操作 (e.g. boto3 API call)"""
    time.sleep(0.1)  # sync sleep，會真的卡住
    return n * n

async def main_f() -> None:
    print("\n=== PART F: asyncio.to_thread ===")

    # 把 sync 函式丟到 thread 執行，不卡住 async loop
    result = await asyncio.to_thread(sync_heavy_computation, 5)
    print(f"  computation result: {result}")   # 25

asyncio.run(main_f())


# ================================================================
# PART G: async generator — 逐步產生資料
# ================================================================
# 真實 codebase 的 streaming: LLM 不是一次給你所有文字，
# 而是一個字一個字「串流」出來
# async generator 讓你可以 async for 逐步取得
#
# 真實 code (guardrail.py line 315):
#   async def avalidate_stream(self, text, ...) -> AsyncIterator[StreamCheckEvent]:
#       ...
#       yield StreamCheckEvent(...)   ← 這就是 async generator

async def text_streamer(text: str):
    """模擬 LLM 逐字輸出"""
    for char in text:
        await asyncio.sleep(0.01)  # 模擬網路延遲
        yield char   # ← yield 讓這變成 generator

async def main_g() -> None:
    print("\n=== PART G: async generator ===")

    collected = ""
    async for char in text_streamer("Hello!"):   # ← async for
        collected += char
        print(f"  收到: {char!r}")

    print(f"  完整文字: {collected}")

asyncio.run(main_g())


# ================================================================
# PART H: TODO 練習
# ================================================================

# TODO H1: 實作一個 async 函式，接收兩個數字，回傳相加結果
# 記得加型別標注
async def async_add(a: int, b: int) -> int:
    pass


# TODO H2: 實作 async 版的 safe_divide
# 若 b == 0，回傳 None；否則回傳 a / b
# 加上 await asyncio.sleep(0) 模擬非同步操作
async def async_divide(a: float, b: float) -> float | None:
    pass


# TODO H3: 實作 async generator — 逐個產生 list 中的元素
# 每個元素之間 await asyncio.sleep(0)
async def async_yield_items(items: list):
    pass
    # 提示:
    # for item in items:
    #     await asyncio.sleep(0)
    #     yield item


# TODO H4: 實作 fetch_with_timeout
# 呼叫 fetch_data("test", 5.0)，若超過 timeout 秒則回傳 "timeout"
async def fetch_with_timeout(timeout: float) -> str:
    try:
        pass  # 用 asyncio.wait_for 呼叫 fetch_data("test", 5.0)
    except TimeoutError:
        return "timeout"


# TODO H5: 實作 run_parallel
# 同時執行 fetch_data("A", 0.1) 和 fetch_data("B", 0.2)
# 回傳兩個結果的 list
async def run_parallel() -> list[str]:
    pass  # 用 asyncio.gather


# 驗證區 (取消 # 來測試):
async def verify_h() -> None:
    print("\n=== 驗證 H1~H5 ===")
    # print(await async_add(3, 4))             # 7
    # print(await async_divide(10, 2))          # 5.0
    # print(await async_divide(10, 0))          # None
    # async for item in async_yield_items([1, 2, 3]):
    #     print(item)
    # print(await fetch_with_timeout(0.1))      # "timeout" (5s task, 0.1s timeout)
    # print(await run_parallel())               # ['Data from A', 'Data from B']

asyncio.run(verify_h())


# ================================================================
# SELF CHECK: 讀真實 code
# ================================================================
# 看 guardrail.py 裡的這段 (line 369-387)，現在你應該能讀懂了:
"""
async def _check_claim(
    self, approved: str, buffer: str, resolved_version: str
) -> StreamCheckEvent | None:
    response = await asyncio.to_thread(
        self.bedrock_runtime.client.apply_guardrail,
        guardrailIdentifier=self.guardrail_id,
        guardrailVersion=resolved_version,
        source=self.source,
        content=[{"text": {"text": approved + buffer}}],
    )
    if response["action"] == BEDROCK_GUARDRAIL_BLOCK_FLAG:
        violations = self._extract_violations(response)
        return StreamCheckEvent(
            type="blocked",
            replacement=response["outputs"][0]["text"],
            reason=f"Content blocked: {violations}",
        )
    return None
"""
# Q1: 為什麼用 asyncio.to_thread？
#     → boto3 的 apply_guardrail 是 sync，直接呼叫會卡住 async loop
#
# Q2: StreamCheckEvent | None 是什麼意思？
#     → 這個函式可能回傳 StreamCheckEvent 物件，也可能回傳 None
#       (blocked 時回傳 event，通過時回傳 None)
#
# Q3: response["outputs"][0]["text"] 你現在能讀懂嗎？
#     → 參考 01_python_core.py 的 PART D


if __name__ == "__main__":
    print("\n執行完成。去掉 verify_h() 中的 # 測試你的 TODO。")
