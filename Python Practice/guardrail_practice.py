"""
Guardrail System Practice — 

涵蓋概念:
- dataclass + field(default_factory)
- Literal type hint
- async/await + AsyncIterator
- asyncio.wait_for (timeout)
- asyncio.to_thread (sync in async)
- threading.Lock (雙重檢查鎖)
- MagicMock + pytest.mark.asyncio
- frozenset, cast, TypeVar

執行: python -m pytest guardrail_practice.py -v
或:   python guardrail_practice.py  (直接執行 demo)
"""

from __future__ import annotations

import asyncio
import threading
import time
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from typing import Any, Literal


# ────────────────────────────────────────────────────────────────
# PART 1: Dataclasses
# ────────────────────────────────────────────────────────────────
# 練習重點: dataclass, Literal, field(default_factory=list)
#
# 真實對應: ValidateResult / StreamCheckEvent / GuardrailStreamResult

@dataclass
class ValidateResult:
    """
    TODO 1: 補完這個 dataclass。
    欄位:
      - intervened: bool
      - output_text: str | None
      - reason: str
    """
    pass  # 刪掉這行, 補上欄位


@dataclass
class StreamCheckEvent:
    """
    TODO 2: 補完這個 dataclass。
    欄位:
      - type: Literal["text", "blocked"]   ← 只能是這兩個值
      - text: str | None = None
      - replacement: str | None = None
      - reason: str | None = None
    """
    pass


@dataclass
class FilterResult:
    """
    TODO 3: 補完這個 dataclass。
    欄位:
      - intervened: bool
      - reason: str | None
      - text: str
      - tags: list[str]  ← 預設空 list, 用 field(default_factory=list)
      - error: bool = False
      - is_last: bool = False
    """
    pass


# ────────────────────────────────────────────────────────────────
# PART 2: Sentence boundary detection
# ────────────────────────────────────────────────────────────────
# 練習重點: frozenset, 字串操作, pure function

SENTENCE_DELIMITERS: frozenset[str] = frozenset(
    {"。", ".", "！", "!", "？", "?", "\n", "；", ";"}
)
BOUNDARY_LOOKBACK: int = 5
MIN_CLAIM_SIZE: int = 60


def has_boundary(buffer: str) -> bool:
    """
    TODO 4: 實作這個函式。
    條件:
      1. buffer 長度 >= MIN_CLAIM_SIZE
      2. buffer 最後 BOUNDARY_LOOKBACK 個字元中，至少有一個在 SENTENCE_DELIMITERS 裡

    範例:
      has_boundary("a" * 60 + "。") -> True
      has_boundary("a" * 59 + "。") -> False  ← 太短
      has_boundary("a" * 60 + "x") -> False   ← 沒有 delimiter
    """
    pass


def split_text_chunks(text: str, *, min_chunk_size: int = 20) -> list[str]:
    """
    TODO 5: 實作這個函式。
    邏輯:
      1. 若 text 為空或長度 <= min_chunk_size, 直接回傳 [text] 或 []
      2. 用 regex 在句子邊界切割 (。！？\n 以及 ". " "! " "? " 後面)
      3. 過濾掉空字串
      4. 合併太短的片段: 累積 buf, 超過 min_chunk_size 才 append 到 chunks
      5. 最後剩下的 buf 合併到最後一個 chunk, 或直接 append

    提示: import re, re.split(r"(?<=[。！？\n])|(?<=\\. )|(?<=! )|(?<=\\? )", text)
    """
    pass


# ────────────────────────────────────────────────────────────────
# PART 3: Sync fake guardrail validator
# ────────────────────────────────────────────────────────────────
# 練習重點: class, threading.Lock, double-checked locking

BLOCK_FLAG = "BLOCKED"
PASS_MSG = "Content passed validation"


class FakeGuardrail:
    """
    模擬一個簡化版的 GuardrailManager。
    - 內部維護一個 blocked_words: set[str]
    - validate() 掃描文字中是否有被封鎖的詞
    - 有版本快取機制 + threading.Lock 保護

    TODO 6: 實作 __init__
      - self.blocked_words: set[str]  ← 從參數傳入
      - self._version: str = "1"
      - self._version_lock: threading.Lock()
      - self._last_refresh: float = 0.0
      - self._refresh_interval: float = 60.0  ← 秒
    """

    def __init__(self, blocked_words: set[str]) -> None:
        pass

    def _needs_refresh(self) -> bool:
        """True if more than _refresh_interval seconds since last refresh."""
        return (time.time() - self._last_refresh) > self._refresh_interval

    def _refresh_version(self) -> None:
        """Simulate fetching latest version from remote."""
        self._version = str(int(self._version) + 1)
        self._last_refresh = time.time()

    def resolve_version(self) -> str:
        """
        TODO 7: 實作 double-checked locking。
        邏輯:
          1. 若 _needs_refresh() 為 False, 直接回傳 self._version
          2. with self._version_lock:
               再次檢查 _needs_refresh() (另一個 thread 可能已更新)
               若仍需更新, 呼叫 _refresh_version()
          3. 回傳 self._version
        """
        pass

    def validate(self, text: str) -> ValidateResult:
        """
        TODO 8: 實作 validate。
        邏輯:
          1. 呼叫 resolve_version() (不需要用到回傳值, 只是觸發更新)
          2. 找出 text 中出現的 blocked_words
          3. 若有, 回傳 ValidateResult(intervened=True, output_text="[BLOCKED]",
                                        reason=f"Blocked: {violations}")
          4. 若無, 回傳 ValidateResult(intervened=False, output_text=None, reason=PASS_MSG)
        """
        pass


# ────────────────────────────────────────────────────────────────
# PART 4: Async streaming guardrail
# ────────────────────────────────────────────────────────────────
# 練習重點: async def, AsyncIterator, asyncio.to_thread, asyncio.wait_for

async def avalidate_stream(
    guardrail: FakeGuardrail,
    text: str,
    *,
    version: str = "LATEST",
) -> AsyncIterator[StreamCheckEvent]:
    """
    TODO 9: 實作 async generator。
    邏輯 (逐字掃描):
      1. 若 text 為空, 直接 return
      2. approved = "", buffer = ""
      3. for ch in text:
           buffer += ch
           if has_boundary(buffer):
             用 asyncio.to_thread 呼叫 guardrail.validate(approved + buffer)
             若 result.intervened:
               yield StreamCheckEvent(type="blocked",
                                       replacement="[BLOCKED]",
                                       reason=result.reason)
               return
             yield StreamCheckEvent(type="text", text=buffer)
             approved += buffer
             buffer = ""
      4. 若 buffer 非空, 做最後一次驗證, 同上邏輯
    """
    pass
    if False:
        yield  # keeps this an async generator even before TODO is done


async def apply_filter_to_stream(
    guardrail: FakeGuardrail | None,
    text: str,
    refusal_message: str,
    *,
    timeout: float = 10.0,
) -> FilterResult:
    """
    TODO 10: 實作這個 coroutine。
    邏輯:
      1. 若 guardrail 為 None 或 text 為空:
           回傳 FilterResult(intervened=False, reason=None, text=text, tags=[])
      2. 定義內部 async def _collect() -> StreamCheckEvent | None:
           async for event in avalidate_stream(guardrail, text):
             if event.type == "blocked": return event
           return None
      3. 用 asyncio.wait_for(_collect(), timeout=timeout) 取得結果
         - 若 TimeoutError: 回傳 FilterResult(intervened=True, reason="timeout",
                                               text=refusal_message, tags=[], error=True)
         - 若其他 Exception: 回傳 FilterResult(intervened=True, reason="service error",
                                               text=refusal_message, tags=[], error=True)
      4. 若 blocked_event 不為 None:
           回傳 FilterResult(intervened=True, reason=blocked_event.reason,
                             text=blocked_event.replacement or refusal_message, tags=[])
      5. 否則回傳 FilterResult(intervened=False, reason=None, text=text, tags=[])
    """
    pass


# ────────────────────────────────────────────────────────────────
# PART 5: with_last_flag utility
# ────────────────────────────────────────────────────────────────
# 練習重點: async generator, 1-item lookahead

async def with_last_flag(
    iterable: AsyncIterator[Any],
) -> AsyncIterator[tuple[Any, bool]]:
    """
    TODO 11: 實作 1-item lookahead async generator。
    讓 consumer 知道哪個是最後一個 item。

    範例:
      async for item, is_last in with_last_flag(aiter([1, 2, 3])):
          print(item, is_last)
      # 1 False
      # 2 False
      # 3 True

    提示:
      - iterator = aiter(iterable)
      - prev_item = await anext(iterator)  ← 若 StopAsyncIteration 則 return
      - async for item in iterator:
          yield prev_item, False
          prev_item = item
      - yield prev_item, True
    """
    pass
    if False:
        yield  # keeps async generator


# ────────────────────────────────────────────────────────────────
# PART 6: Full streaming pipeline
# ────────────────────────────────────────────────────────────────
# 練習重點: 組合前面所有工具

async def stream_with_guardrail(
    chunks: AsyncIterator[str],
    guardrail: FakeGuardrail | None,
    refusal_message: str,
) -> AsyncIterator[FilterResult]:
    """
    TODO 12: 實作 sentence-level streaming guardrail loop。
    邏輯:
      1. approved_prefix = "", buffer = ""
      2. async for chunk, is_last in with_last_flag(chunks):
           buffer += chunk
           if not is_last and not has_boundary(buffer): continue
           ← 用 apply_filter_to_stream(guardrail, buffer, refusal_message) 驗證
           ← 在 FilterResult 上設定 is_last=is_last (直接指派屬性)
           yield result
           if result.intervened or result.error: return
           approved_prefix += buffer
           buffer = ""
    """
    pass
    if False:
        yield


# ────────────────────────────────────────────────────────────────
# PART 7: Tests
# ────────────────────────────────────────────────────────────────
# 執行: python -m pytest guardrail_practice.py -v

import pytest
from unittest.mock import MagicMock, AsyncMock


class TestDataclasses:
    def test_validate_result_fields(self) -> None:
        r = ValidateResult(intervened=True, output_text="blocked", reason="policy")
        assert r.intervened is True
        assert r.output_text == "blocked"
        assert r.reason == "policy"

    def test_stream_check_event_defaults(self) -> None:
        e = StreamCheckEvent(type="text", text="hello")
        assert e.text == "hello"
        assert e.replacement is None
        assert e.reason is None

    def test_filter_result_default_list(self) -> None:
        r1 = FilterResult(intervened=False, reason=None, text="ok")
        r2 = FilterResult(intervened=False, reason=None, text="ok")
        r1.tags.append("x")
        assert r2.tags == []  # 若用 default=[] 會失敗 (shared reference bug)

    def test_filter_result_error_defaults(self) -> None:
        r = FilterResult(intervened=False, reason=None, text="ok")
        assert r.error is False
        assert r.is_last is False


class TestBoundaryDetection:
    def test_has_boundary_true(self) -> None:
        text = "a" * 60 + "。"
        assert has_boundary(text) is True

    def test_has_boundary_too_short(self) -> None:
        text = "a" * 59 + "。"
        assert has_boundary(text) is False

    def test_has_boundary_no_delimiter(self) -> None:
        text = "a" * 65
        assert has_boundary(text) is False

    def test_has_boundary_english(self) -> None:
        text = "The quick brown fox jumps over the lazy dog and it was fun."
        assert has_boundary(text) is True


class TestSplitTextChunks:
    def test_empty_string(self) -> None:
        assert split_text_chunks("") == []

    def test_short_string(self) -> None:
        result = split_text_chunks("hello")
        assert result == ["hello"]

    def test_chinese_split(self) -> None:
        text = "這是第一個句子。這是第二個句子。這是第三個句子。"
        chunks = split_text_chunks(text)
        assert len(chunks) >= 1
        assert "".join(chunks) == text

    def test_no_tiny_chunks(self) -> None:
        text = "這是第一個句子。這是第二個句子，然後還有更多文字接在後面繼續說明。"
        chunks = split_text_chunks(text, min_chunk_size=20)
        for c in chunks:
            assert len(c) >= 20 or c == chunks[-1]


class TestFakeGuardrail:
    def test_passes_clean_text(self) -> None:
        g = FakeGuardrail(blocked_words={"bomb", "hack"})
        result = g.validate("Hello, how are you?")
        assert result.intervened is False
        assert result.output_text is None

    def test_blocks_bad_word(self) -> None:
        g = FakeGuardrail(blocked_words={"bomb"})
        result = g.validate("How to make a bomb at home")
        assert result.intervened is True
        assert "bomb" in result.reason

    def test_version_double_checked_lock(self) -> None:
        g = FakeGuardrail(blocked_words=set())
        g._last_refresh = 0.0  # force stale
        v1 = g.resolve_version()
        assert v1 != "1"  # was refreshed
        g._last_refresh = time.time()  # mark fresh
        v2 = g.resolve_version()
        assert v1 == v2  # no extra refresh


class TestAsyncGuardrail:
    @pytest.mark.asyncio
    async def test_passthrough_when_none(self) -> None:
        result = await apply_filter_to_stream(None, "hello world", "refused")
        assert result.intervened is False
        assert result.text == "hello world"

    @pytest.mark.asyncio
    async def test_passthrough_empty_text(self) -> None:
        g = FakeGuardrail(blocked_words={"bomb"})
        result = await apply_filter_to_stream(g, "", "refused")
        assert result.intervened is False
        assert result.text == ""

    @pytest.mark.asyncio
    async def test_clean_text_passes(self) -> None:
        g = FakeGuardrail(blocked_words={"bomb"})
        long_clean = "This is a perfectly fine sentence with no bad words at all okay? " * 2
        result = await apply_filter_to_stream(g, long_clean, "refused")
        assert result.intervened is False

    @pytest.mark.asyncio
    async def test_blocked_text_intervenes(self) -> None:
        g = FakeGuardrail(blocked_words={"bomb"})
        long_bad = "How to make a bomb at home with basic materials you can find easily. " * 2
        result = await apply_filter_to_stream(g, long_bad, "refused")
        assert result.intervened is True
        assert result.text in ("[BLOCKED]", "refused")

    @pytest.mark.asyncio
    async def test_timeout_returns_error(self) -> None:
        async def _slow_stream(_text, **_kw):
            await asyncio.sleep(60)
            yield StreamCheckEvent(type="text", text="late")

        g = MagicMock(spec=FakeGuardrail)
        g.validate = MagicMock()

        # Patch avalidate_stream to hang
        import guardrail_practice as m
        original = m.avalidate_stream

        async def hanging_stream(guardrail, text, **kw):
            await asyncio.sleep(60)
            yield StreamCheckEvent(type="text", text="x")

        m.avalidate_stream = hanging_stream
        try:
            result = await apply_filter_to_stream(g, "any text here ok", "refused", timeout=0.05)
            assert result.error is True
            assert result.intervened is True
            assert "timeout" in result.reason
        finally:
            m.avalidate_stream = original


class TestWithLastFlag:
    @pytest.mark.asyncio
    async def test_single_item(self) -> None:
        async def _gen():
            yield 42

        results = [(item, flag) async for item, flag in with_last_flag(_gen())]
        assert results == [(42, True)]

    @pytest.mark.asyncio
    async def test_multiple_items(self) -> None:
        async def _gen():
            for i in [1, 2, 3]:
                yield i

        results = [(item, flag) async for item, flag in with_last_flag(_gen())]
        assert results == [(1, False), (2, False), (3, True)]

    @pytest.mark.asyncio
    async def test_empty(self) -> None:
        async def _gen():
            return
            yield  # pragma: no cover

        results = [(item, flag) async for item, flag in with_last_flag(_gen())]
        assert results == []


class TestStreamWithGuardrail:
    @pytest.mark.asyncio
    async def test_clean_stream_passes(self) -> None:
        async def _chunks():
            for chunk in ["This is a clean sentence okay? ", "Another fine sentence here! "]:
                yield chunk

        g = FakeGuardrail(blocked_words={"bomb"})
        results = [r async for r in stream_with_guardrail(_chunks(), g, "refused")]
        assert all(not r.intervened for r in results)
        assert results[-1].is_last is True

    @pytest.mark.asyncio
    async def test_passthrough_no_guardrail(self) -> None:
        async def _chunks():
            yield "hello world "
            yield "goodbye world."

        results = [r async for r in stream_with_guardrail(_chunks(), None, "refused")]
        assert len(results) >= 1


# ────────────────────────────────────────────────────────────────
# Demo (直接 python 執行)
# ────────────────────────────────────────────────────────────────

async def _demo() -> None:
    print("\n=== Guardrail Practice Demo ===\n")

    g = FakeGuardrail(blocked_words={"bomb", "hack", "exploit"})

    print("1. sync validate:")
    for text in ["Hello world!", "How to make a bomb?"]:
        r = g.validate(text)
        print(f"   '{text[:30]}...' -> intervened={r.intervened}, reason={r.reason}")

    print("\n2. split_text_chunks:")
    sample = "這是第一個完整的句子。然後是第二個句子！第三個句子呢？"
    chunks = split_text_chunks(sample)
    print(f"   chunks: {chunks}")

    print("\n3. apply_filter_to_stream:")
    clean = "This is a perfectly safe and normal response with no issues at all here. "
    result = await apply_filter_to_stream(g, clean * 3, "I cannot help with that.")
    print(f"   clean: intervened={result.intervened}")

    bad = "Let me explain how to hack into systems and make a bomb easily. More text follows here. "
    result2 = await apply_filter_to_stream(g, bad * 2, "I cannot help with that.")
    print(f"   bad:   intervened={result2.intervened}, text={result2.text}")

    print("\n4. stream_with_guardrail:")
    async def _stream():
        for chunk in ["This is safe. ", "More safe content here okay? ", "All done!"]:
            yield chunk

    async for r in stream_with_guardrail(_stream(), g, "refused"):
        print(f"   chunk: intervened={r.intervened}, is_last={r.is_last}, text={r.text!r:.40}")

    print("\nDone.")


if __name__ == "__main__":
    asyncio.run(_demo())
