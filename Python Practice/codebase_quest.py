"""
Codebase Navigation Quest — 練習自己找答案的能力
目標: 不靠 Agent 回答，自己打開檔案讀，寫下你的答案

用法:
  1. 每個 QUEST 有一個問題
  2. 打開它說的檔案，自己讀
  3. 把答案寫進 YOUR_ANSWER 變數
  4. 執行: python codebase_quest.py 看哪些過關

這訓練的是: 「看到需求 → 知道去哪找 → 找到後能讀懂」
"""

PROJECT = "/Users/neosu/Desktop/Project-CTBC-EAO"

# ================================================================
# 怎麼讀 code 的基本策略 (先讀這裡)
# ================================================================
#
# 1. 先看資料夾結構  → 知道整體分層
# 2. 找 __init__.py → 知道這個 package 對外暴露什麼
# 3. 看 imports     → 知道這個檔案依賴什麼
# 4. 看 class/def 的 signature → 知道吃什麼吐什麼，不用立刻讀實作
# 5. 搜尋關鍵字     → grep 或 VS Code Cmd+Shift+F
#
# 工具: terminal 裡用 grep -rn "關鍵字" . --include="*.py"
#       VS Code: Cmd+P 搜尋檔案, Cmd+Shift+F 搜尋內容


# ================================================================
# QUEST 1: 找到 guardrail 的「入口」
# ================================================================
# 問題: 當使用者送出訊息，guardrail 驗證在哪裡被觸發？
#
# 提示:
#   - 從 services/eao/src/services/chat_service.py 開始
#   - 找哪個 method 處理 chat 請求
#   - 追蹤裡面有沒有呼叫 guardrail 相關的函式
#
# 你需要回答:
#   - 哪個 class/method 觸發 guardrail？
#   - 是 input guardrail 還是 output guardrail？

QUEST_1 = {
    "file_to_open": f"{PROJECT}/services/eao/src/services/chat_service.py",
    "question": "使用者送出訊息後，哪個 method 觸發 guardrail？",
    "YOUR_ANSWER": "",   # ← 在這裡填你的答案
    "hint": "搜尋 'guardrail' 關鍵字，看它被哪個 method 呼叫",
}


# ================================================================
# QUEST 2: 搞懂 GuardrailManager 的初始化需要什麼
# ================================================================
# 問題: 要建立一個 GuardrailManager，你需要提供哪些必填參數？
#
# 提示: 看 packages/common/common/llm/guardrail.py 的 __init__

QUEST_2 = {
    "file_to_open": f"{PROJECT}/packages/common/common/llm/guardrail.py",
    "question": "GuardrailManager.__init__ 有哪些沒有預設值的必填參數？",
    "YOUR_ANSWER": [],   # ← 填入 list of str，e.g. ["region", "account_id", ...]
    "hint": "看 def __init__(self, ...) 的參數，有 = 預設值的不算必填",
}


# ================================================================
# QUEST 3: timeout 是怎麼決定的？
# ================================================================
# 問題: guardrail 的預設 timeout 是幾秒？這個值定義在哪裡？
#       如果你要改成 60 秒，你會改哪個地方？

QUEST_3 = {
    "file_to_open": f"{PROJECT}/packages/common/common/llm/guardrail.py",
    "question": "DEFAULT_GUARDRAIL_TIMEOUT_SEC 是多少秒？定義在哪一行？",
    "YOUR_ANSWER": {
        "value": None,        # ← 填數字
        "line_number": None,  # ← 填行號
        "where_used": "",     # ← 這個變數被哪些函式用到？
    },
    "hint": "Cmd+F 搜尋 DEFAULT_GUARDRAIL_TIMEOUT_SEC，看它在哪裡出現",
}


# ================================================================
# QUEST 4: blocked 之後顯示什麼訊息？
# ================================================================
# 問題: guardrail 攔截後，使用者看到的拒絕訊息 (refusal_message)
#       是在哪裡定義的？你怎麼修改它？

QUEST_4 = {
    "files_to_check": [
        f"{PROJECT}/services/eao/src/workflows/integration_workflow.py",
        f"{PROJECT}/services/eao/src/core/config.py",
    ],
    "question": "refusal_message 從哪裡來？是 hardcode 還是從 config 讀？",
    "YOUR_ANSWER": "",
    "hint": "在 integration_workflow.py 搜尋 'refusal'，找到後看它的值從哪來",
}


# ================================================================
# QUEST 5: 分句邏輯
# ================================================================
# 問題: streaming guardrail 不是一次驗整段文字，而是分句驗
#       它用什麼符號來判斷「一個句子結束了」？
#       中文和英文的分句符號一樣嗎？

QUEST_5 = {
    "file_to_open": f"{PROJECT}/packages/common/common/llm/guardrail.py",
    "question": "DEFAULT_CLAIM_DELIMITERS 包含哪些字元？為什麼同時要中英文？",
    "YOUR_ANSWER": {
        "delimiters": [],   # ← 列出所有字元
        "reason": "",       # ← 你的理解
    },
    "hint": "看第 24-27 行的 frozenset",
}


# ================================================================
# QUEST 6: 測試 pattern 辨識
# ================================================================
# 問題: 測試檔裡有一個常見 pattern：建立一個假的 guardrail
#       讓測試不依賴真實 AWS 服務
#
# 提示: 看 packages/common/tests/test_apply_guardrail_to_stream.py

QUEST_6 = {
    "file_to_open": f"{PROJECT}/packages/common/tests/test_apply_guardrail_to_stream.py",
    "question": "測試用什麼方式建立假的 GuardrailManager？哪個 Python 函式做到這件事？",
    "YOUR_ANSWER": {
        "tool_used": "",       # e.g. "MagicMock", "patch", ...
        "why_spec_arg": "",    # MagicMock(spec=GuardrailManager) 的 spec= 參數有什麼用？
    },
    "hint": "看 _guardrail_yielding 函式，注意 MagicMock(spec=...)",
}


# ================================================================
# QUEST 7: 找 bug 練習 (進階)
# ================================================================
# 問題: 下面這段 code 有什麼問題？你需要打開真實檔案對照
#
# 假設有人寫了這段:
"""
async def bad_apply_guardrail(guardrail, text, refusal_message):
    async for event in guardrail.avalidate_stream(text):
        if event.type == "blocked":
            return GuardrailStreamResult(
                intervened=True,
                text=refusal_message,
            )
    return GuardrailStreamResult(intervened=False, text=text)
"""
# 和真實的 apply_guardrail_to_stream 相比，這段 code 少了什麼？

QUEST_7 = {
    "file_to_open": f"{PROJECT}/packages/common/common/llm/guardrail.py",
    "question": "這段 bad code 和真實實作相比，少了哪些重要處理？",
    "YOUR_ANSWER": [],   # ← 列出你找到的差異
    "hint": "看 apply_guardrail_to_stream (line 413-477)，思考: timeout? error? None guardrail?",
}


# ================================================================
# 驗收: 自動檢查你填了多少答案
# ================================================================

def check_answers() -> None:
    quests = {
        "QUEST 1 — guardrail 入口": QUEST_1["YOUR_ANSWER"],
        "QUEST 2 — 必填參數":       QUEST_2["YOUR_ANSWER"],
        "QUEST 3 — timeout 秒數":   QUEST_3["YOUR_ANSWER"]["value"],
        "QUEST 4 — refusal_message": QUEST_4["YOUR_ANSWER"],
        "QUEST 5 — delimiters":     QUEST_5["YOUR_ANSWER"]["delimiters"],
        "QUEST 6 — mock pattern":   QUEST_6["YOUR_ANSWER"]["tool_used"],
        "QUEST 7 — bug 差異":       QUEST_7["YOUR_ANSWER"],
    }

    answered = 0
    for name, answer in quests.items():
        filled = bool(answer)
        status = "✓" if filled else "○"
        print(f"  {status} {name}")
        if filled:
            answered += 1

    print(f"\n  {answered}/{len(quests)} 完成")
    if answered == len(quests):
        print("  全部完成! 你已具備基本 codebase 導航能力。")
    else:
        print("  繼續! 打開對應的檔案，用 Cmd+F 搜尋關鍵字。")


if __name__ == "__main__":
    print("=== Codebase Quest 進度 ===\n")
    check_answers()
    print(f"\n專案路徑: {PROJECT}")
    print("推薦: 用 VS Code 開啟專案，Cmd+Shift+F 全域搜尋")
