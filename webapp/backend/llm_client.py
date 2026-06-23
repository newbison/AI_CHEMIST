"""DeepSeek LLM 客户端 — OpenAI 兼容协议，流式输出。

支持自动续写：当模型因 max_tokens 截断时，自动发送续写请求，
直到报告完整生成或达到续写次数上限。
"""
from __future__ import annotations

import os
from typing import Callable, Iterator

from openai import OpenAI

DEFAULT_MODEL = "deepseek-v4-pro"
DEFAULT_BASE_URL = "https://api.deepseek.com"

# 单次调用的最大输出 token 数
# DeepSeek V4 Pro 支持最高 384K 输出，设为 64K 足够覆盖最长的报告
# 如遇极端情况超出，续写机制会自动接管
MAX_TOKENS_PER_CALL = 65536
# 续写次数上限（防止无限循环）
MAX_CONTINUATIONS = 3


def _get_api_key() -> str:
    key = os.environ.get("DEEPSEEK_API_KEY", "")
    if not key:
        raise RuntimeError(
            "未设置 DEEPSEEK_API_KEY 环境变量。"
            "请在 .env 文件或环境变量中设置你的 DeepSeek API key。"
        )
    return key


def get_client() -> OpenAI:
    # timeout: 连接+读取超时 300 秒（大 prompt 首 token 延迟可能很长）
    return OpenAI(
        api_key=_get_api_key(),
        base_url=os.environ.get("DEEPSEEK_BASE_URL", DEFAULT_BASE_URL),
        timeout=300.0,
    )


def stream_report(
    system_prompt: str,
    user_prompt: str,
    *,
    model: str | None = None,
    on_continue: "Callable[[int], None] | None" = None,
) -> Iterator[str]:
    """流式生成报告，逐 chunk 返回文本。

    当模型输出达到 max_tokens 上限（finish_reason="length"）时，
    自动发送续写请求，确保 18 节完整报告不会在中途截断。
    最多续写 MAX_CONTINUATIONS 次。

    Args:
        on_continue: 续写开始时的回调，参数为续写次数（1-based）。
                     用于让调用方推送 SSE 进度事件。
    """
    client = get_client()
    model_name = model or os.environ.get("DEEPSEEK_MODEL", DEFAULT_MODEL)

    messages: list[dict] = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    continuation_count = 0

    while True:
        finish_reason = None
        generated_this_round = ""

        stream = client.chat.completions.create(
            model=model_name,
            messages=messages,
            stream=True,
            stream_options={"include_usage": True},
            temperature=0.3,
            max_tokens=MAX_TOKENS_PER_CALL,
        )

        for chunk in stream:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta.content
            fr = chunk.choices[0].finish_reason
            if fr:
                finish_reason = fr
            if delta:
                generated_this_round += delta
                yield delta

        # 检查是否因 max_tokens 截断
        if finish_reason == "length":
            continuation_count += 1
            if continuation_count > MAX_CONTINUATIONS:
                print(f"[llm_client] 已达最大续写次数 {MAX_CONTINUATIONS}，停止续写")
                break

            print(f"[llm_client] 模型输出被截断 (max_tokens={MAX_TOKENS_PER_CALL})，"
                  f"自动续写第 {continuation_count} 次...")

            if on_continue:
                on_continue(continuation_count)

            # 将已生成内容加入对话历史
            messages.append({"role": "assistant", "content": generated_this_round})

            # 续写提示：要求从断点精确继续
            if continuation_count == 1:
                cont_msg = (
                    "You were cut off mid-output. Continue EXACTLY where you stopped. "
                    "Do NOT repeat anything already written. Do NOT restart from the beginning. "
                    "Pick up from the very next character and continue the report. "
                    "你刚才的输出被截断了。请从断点处**精确继续**，不要重复已输出的任何内容，不要重新开始。"
                )
            else:
                cont_msg = "Continue. Do not repeat. Pick up exactly where you stopped."
            messages.append({"role": "user", "content": cont_msg})
        else:
            # 自然结束（finish_reason="stop" 或 None）
            if continuation_count > 0:
                print(f"[llm_client] 续写完成，共续写 {continuation_count} 次")
            break
