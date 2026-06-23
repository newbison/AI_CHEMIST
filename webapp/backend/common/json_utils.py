"""JSON 解析工具 — 三重兜底解析策略"""

import json
import logging
import re
from typing import Any

logger = logging.getLogger(__name__)

# 通用日志函数，避免每个模块重复定义
log = logger.debug


def parse_json_with_fallback(
    raw: str,
    expected_keys: list[str] | None = None,
) -> dict[str, Any] | list | None:
    """三重 JSON 解析兜底策略。

    尝试三种解析方法：
    1. 直接 json.loads()
    2. 提取代码块 ```json ... ```
    3. 找首尾花括号

    Args:
        raw: 原始字符串（通常是 LLM 返回）
        expected_keys: 可选，期望的顶级键列表，用于验证解析结果

    Returns:
        解析后的 dict/list，或 None（全部失败）
    """
    # 方法1：直接解析
    try:
        result = json.loads(raw)
        if expected_keys:
            _validate_keys(result, expected_keys)
        return result
    except (json.JSONDecodeError, TypeError) as e:
        log(f"[json_utils] 直接解析失败: {e}")

    # 方法2：提取代码块
    patterns = [
        r"```(?:json)?\s*([\s\S]*?)\s*```",  # 标准代码块
        r"```\s*([\s\S]*?)\s*```",            # 无语言标注
    ]
    for pattern in patterns:
        match = re.search(pattern, raw, re.MULTILINE)
        if match:
            try:
                result = json.loads(match.group(1).strip())
                if expected_keys:
                    _validate_keys(result, expected_keys)
                log(f"[json_utils] 代码块解析成功")
                return result
            except (json.JSONDecodeError, TypeError) as e:
                log(f"[json_utils] 代码块解析失败: {e}")

    # 方法3：找首尾花括号
    start = raw.find("{")
    end = raw.rfind("}")
    if start != -1 and end != -1 and start < end:
        try:
            result = json.loads(raw[start : end + 1])
            if expected_keys:
                _validate_keys(result, expected_keys)
            log(f"[json_utils] 花括号解析成功")
            return result
        except (json.JSONDecodeError, TypeError) as e:
            log(f"[json_utils] 花括号解析失败: {e}")

    log(f"[json_utils] 三重解析全部失败，原始内容: {raw[:200]}...")
    return None


def _validate_keys(result: dict | list, expected_keys: list[str]) -> None:
    """验证解析结果是否包含期望的键。"""
    if isinstance(result, dict):
        missing = [k for k in expected_keys if k not in result]
        if missing:
            log(f"[json_utils] 警告：缺少期望的键: {missing}")


def parse_json_array_with_fallback(raw: str) -> list | None:
    """三重 JSON 数组解析兜底策略。

    专门用于解析 LLM 返回的 JSON 数组（如策略列表）。

    Args:
        raw: 原始字符串

    Returns:
        解析后的 list，或 None（全部失败）
    """
    # 方法1：直接解析
    try:
        result = json.loads(raw)
        if isinstance(result, list):
            return result
        log(f"[json_utils] 直接解析成功但不是数组: {type(result)}")
    except (json.JSONDecodeError, TypeError) as e:
        log(f"[json_utils] 数组直接解析失败: {e}")

    # 方法2：提取代码块
    match = re.search(r"```(?:json)?\s*(\[[\s\S]*?\])\s*```", raw, re.MULTILINE)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except (json.JSONDecodeError, TypeError):
            pass

    # 方法3：找首尾方括号
    start = raw.find("[")
    end = raw.rfind("]")
    if start != -1 and end != -1 and start < end:
        try:
            return json.loads(raw[start : end + 1])
        except (json.JSONDecodeError, TypeError):
            pass

    log(f"[json_utils] 三重数组解析全部失败")
    return None
