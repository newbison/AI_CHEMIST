"""DeepSeek LLM 客户端 — OpenAI 兼容协议，流式输出。"""
from __future__ import annotations

import os
from typing import Iterator

from openai import OpenAI

DEFAULT_MODEL = "deepseek-chat"
DEFAULT_BASE_URL = "https://api.deepseek.com"


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
) -> Iterator[str]:
    """流式生成报告，逐 chunk 返回文本。

    使用 max_tokens=8192（DeepSeek-chat 的最大输出）。
    完整报告可能被截断 — 调用方应告知用户报告可能不完整。
    """
    client = get_client()
    stream = client.chat.completions.create(
        model=model or os.environ.get("DEEPSEEK_MODEL", DEFAULT_MODEL),
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        stream=True,
        temperature=0.3,
        max_tokens=8192,
    )
    for chunk in stream:
        if not chunk.choices:
            continue
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta
