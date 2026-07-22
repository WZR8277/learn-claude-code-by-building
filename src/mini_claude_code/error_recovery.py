"""S11 bounded recovery helpers for model/API failures."""

from __future__ import annotations

import os
import random
import time
from dataclasses import dataclass
from typing import Callable, TypeVar


DEFAULT_MAX_TOKENS = 8192
# 输出太长和上下文太长是两类问题：前者提高“回答预算”，后者缩短“输入上下文”。
ESCALATED_MAX_TOKENS = 64_000
MAX_OUTPUT_CONTINUATIONS = 3
# 429/529 属于瞬态 API 故障，只在 with_retry 内部处理，不修改 messages。
MAX_RETRIES = 10
BASE_DELAY_MS = 500
MAX_CONSECUTIVE_529 = 3
CONTINUATION_PROMPT = (
    "Output token limit hit. Resume directly. "
    "No apology, no recap. Pick up mid-thought."
)

T = TypeVar("T")


@dataclass
class RecoveryState:
    """记录本轮 loop 已经尝试过哪些恢复动作，避免无限重试。"""

    # current_model 会在连续 529 后切到 FALLBACK_MODEL_ID；其它字段限制每条恢复路径的次数。
    current_model: str
    has_escalated_output: bool = False
    output_continuations: int = 0
    has_attempted_reactive_compact: bool = False
    consecutive_529: int = 0


def create_recovery_state(primary_model: str) -> RecoveryState:
    return RecoveryState(current_model=primary_model)


def retry_delay(attempt: int, retry_after: float | None = None) -> float:
    """指数退避 + 抖动；如果服务端提供 Retry-After，则优先遵守。"""
    if retry_after is not None:
        return retry_after
    # attempt 从 0 开始：0.5s、1s、2s...，最高 32s，再加最多 25% 抖动。
    base = min(BASE_DELAY_MS * (2 ** attempt), 32_000) / 1000
    return base + random.uniform(0, base * 0.25)


def is_prompt_too_long_error(exc: Exception) -> bool:
    """识别“输入太长”；它需要 reactive compact，而不是提高 max_tokens。"""
    message = str(exc).lower()
    return (
        ("prompt" in message and "long" in message)
        or "prompt_is_too_long" in message
        or "context_length_exceeded" in message
        or "max_context_window" in message
        or "too many tokens" in message
    )


def is_rate_limit_error(exc: Exception) -> bool:
    """429 通常表示限流：等待后重试同一请求，模型和 messages 都不变。"""
    name = type(exc).__name__.lower()
    message = str(exc).lower()
    return "ratelimit" in name or "rate_limit" in message or "429" in message


def is_overloaded_error(exc: Exception) -> bool:
    """529 通常表示服务过载：退避重试；连续过载时可切备用模型。"""
    name = type(exc).__name__.lower()
    message = str(exc).lower()
    return "overloaded" in name or "overloaded" in message or "529" in message


def _fallback_model() -> str | None:
    return os.getenv("FALLBACK_MODEL_ID")


def with_retry(
    fn: Callable[[], T],
    state: RecoveryState,
    *,
    max_retries: int = MAX_RETRIES,
    sleep: Callable[[float], None] | None = None,
) -> T:
    """对 429/529 做有界重试；其它异常交给外层恢复逻辑处理。

    这里不碰 messages：瞬态错误代表请求没有成功完成，不能伪造 assistant
    响应，也不能重复执行工具。真正会改变对话历史的恢复动作留给 loop 外层。
    """
    sleeper = sleep or time.sleep
    for attempt in range(max_retries):
        try:
            result = fn()
            # 成功调用后清空 529 计数，避免一次旧的过载影响后续正常请求。
            state.consecutive_529 = 0
            return result
        except Exception as exc:
            if is_rate_limit_error(exc):
                # 429 不改变模型，只等一会儿后重试同一个 LLM 请求。
                sleeper(retry_delay(attempt))
                continue

            if is_overloaded_error(exc):
                state.consecutive_529 += 1
                if state.consecutive_529 >= MAX_CONSECUTIVE_529:
                    fallback = _fallback_model()
                    if fallback:
                        # 切模型只影响后续重试；这仍然是同一轮恢复，不是新任务。
                        state.current_model = fallback
                    state.consecutive_529 = 0
                sleeper(retry_delay(attempt))
                continue

            raise

    raise RuntimeError(f"Max retries ({max_retries}) exceeded")
