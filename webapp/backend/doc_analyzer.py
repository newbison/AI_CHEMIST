"""文档分析模块 — 从 PDF/Word 文件提取文本并调用 LLM 生成技术分析。"""

from __future__ import annotations

import io
import json
import logging
import os
from typing import Any

import pdfplumber
from docx import Document

from common.json_utils import parse_json_with_fallback  # noqa: E402
from llm_client import get_client  # noqa: E402

# 配置日志
logger = logging.getLogger(__name__)


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """从 PDF 文件提取文本。

    策略：
    - 优先逐页提取文本，保留段落结构
    - 过滤空页
    - 限制单文件总字符数（50万）防止内存溢出
    - 限制最多提取 200 页，防止超大 PDF 处理时间过长
    """
    text_parts: list[str] = []
    total_chars = 0
    MAX_CHARS = 500_000
    MAX_PAGES = 200  # 最多处理 200 页

    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            pages_to_process = pdf.pages[:MAX_PAGES]
            if len(pdf.pages) > MAX_PAGES:
                logger.warning(f"PDF 共 {len(pdf.pages)} 页，只处理前 {MAX_PAGES} 页")

            for page in pages_to_process:
                page_text = page.extract_text() or ""
                if page_text.strip():
                    # 防止超过总限制
                    if total_chars + len(page_text) > MAX_CHARS:
                        remaining = MAX_CHARS - total_chars
                        if remaining > 0:
                            text_parts.append(page_text[:remaining])
                        break
                    text_parts.append(page_text)
                    total_chars += len(page_text)
    except Exception as e:
        raise ValueError(f"PDF 解析失败: {e}")

    if not text_parts:
        raise ValueError("PDF 中未提取到文本（可能是扫描图片或加密文件）")

    logger.info(f"PDF 文本提取完成，共 {len(text_parts)} 页，{total_chars} 字符")
    return "\n\n".join(text_parts)


def extract_text_from_docx(file_bytes: bytes) -> str:
    """从 Word (.docx) 文件提取文本。

    提取所有段落内容，保留基本结构。
    """
    try:
        doc = Document(io.BytesIO(file_bytes))
        paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
        return "\n\n".join(paragraphs)
    except Exception as e:
        raise ValueError(f"Word 文件解析失败: {e}")


def analyze_document(text: str, doc_name: str) -> str:
    """调用 DeepSeek LLM 对文档内容进行技术分析。

    分析维度：技术要点、应用场景、主要结论、关键数据、创新点

    Args:
        text: 提取的文档文本
        doc_name: 文件名（用于提示）

    Returns:
        技术分析文本（Markdown 格式）

    降级策略：
        - LLM 调用失败 → 返回简要摘要（截取前2000字符）
        - JSON 解析失败 → 返回纯文本
    """
    client = get_client()
    model = os.environ.get("DEEPSEEK_MODEL", "deepseek-v4-pro")

    # 截断：超过10万字符只取前10万（LLM上下文窗口限制）
    if len(text) > 100_000:
        text = text[:100_000] + f"\n\n[...文档已截断，原文共 {len(text)} 字符...]"

    prompt = f"""你是一个技术文档分析专家。请对以下文档（文件名：{doc_name}）进行深度分析，提取并总结：

1. **技术要点**：文档涉及的核心技术/材料/工艺/方法
2. **应用场景**：文档描述的应用领域、使用条件和场景
3. **主要结论**：文档的主要发现、结论或技术效果
4. **关键数据**：具体的技术参数、数值、配方范围、条件范围等（如有）
5. **创新点**：与现有技术相比的独特之处或改进（如有）

请用中文回答，结构清晰，数据具体。不要泛泛而谈，不要说"该文档讨论了..."这种废话，直接给出实质内容。
如果文档中某些信息缺失，请明确说明"未提供"，不要虚构。

文档内容：
---
{text}
---

请按以下 JSON 格式输出你的分析（只输出 JSON，不要其他内容）：

```json
{{
  "技术要点": "...",
  "应用场景": "...",
  "主要结论": "...",
  "关键数据": "...",
  "创新点": "..."
}}
```"""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "你是一个技术文档分析专家，擅长提取文档中的关键技术信息。回答必须用中文，输出格式必须是有效的 JSON。",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=2048,
        )
        raw = response.choices[0].message.content or ""

        # 使用公共 JSON 解析函数
        result = parse_json_with_fallback(raw, expected_keys=["技术要点", "应用场景", "主要结论", "关键数据", "创新点"])
        if result and isinstance(result, dict):
            return _format_analysis(result)
        else:
            # 降级：无法解析 JSON，直接返回原始文本
            logger.warning(f"[doc_analyzer] JSON 解析失败，原始返回: {raw[:200]}")
            return f"## 技术分析（原始输出）\n\n{raw[:3000]}"

    except Exception as e:
        logger.error(f"[doc_analyzer] LLM 分析失败: {e}")
        # 降级：返回简要摘要
        return _fallback_analysis(text)


def _format_analysis(result: dict[str, str]) -> str:
    """将解析后的 JSON 格式化为 Markdown。"""
    sections = []
    for key, label in [
        ("技术要点", "技术要点"),
        ("应用场景", "应用场景"),
        ("主要结论", "主要结论"),
        ("关键数据", "关键数据"),
        ("创新点", "创新点"),
    ]:
        value = result.get(key, "").strip()
        if value:
            sections.append(f"### {label}\n\n{value}")
        else:
            sections.append(f"### {label}\n\n未提供")

    return "\n\n".join(sections)


def _fallback_analysis(text: str) -> str:
    """降级分析：无法调用 LLM 时，返回截取的原始文本。"""
    preview = text[:2000]
    return (
        "## 技术分析（自动摘要失败，以下为文档前2000字符预览）\n\n"
        f"```\n{preview}\n```\n\n"
        "> 提示：完整的分析需要 LLM 支持，请检查 API 配置。"
    )
