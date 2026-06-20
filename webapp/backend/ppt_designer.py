"""PPT 设计器 — 调用 DeepSeek 读取 ppt-design-skill，把 Markdown 报告转成结构化设计方案 JSON。

流程：
  Markdown 报告 + SKILL.md → DeepSeek → JSON 设计方案 → pptx_export 渲染

设计方案 JSON schema 见 ppt-design-skill/SKILL.md。
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

from llm_client import get_client


REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL_FILE = REPO_ROOT / "ppt-design-skill" / "SKILL.md"


def _load_skill() -> str:
    """读取 PPT 设计 skill 文件内容。"""
    if not SKILL_FILE.exists():
        return ""
    return SKILL_FILE.read_text(encoding="utf-8")


def _build_design_prompt(markdown: str) -> tuple[str, str]:
    """构建 (system_prompt, user_prompt) 用于 PPT 设计。

    system: 设计师角色 + 输出格式要求
    user: skill 规范 + 报告原文 + 任务指令
    """
    skill_text = _load_skill()

    system_prompt = """你是一个专业的 PPT 演示文稿设计师。你的任务是阅读一份 R&D 报告（Markdown），
根据设计规范把它转换成一份结构化的 PPT 设计方案（JSON 格式）。

你必须只输出一个 JSON 对象，不要输出任何 Markdown 代码块标记、不要任何解释文字。
JSON 必须是合法的、可直接被 json.loads 解析的。

设计目标：让最终的 PPT 专业、美观、信息清晰、视觉有节奏感。"""

    user_prompt = f"""# PPT 设计规范（Skill）

{skill_text}

---

# 待设计的 R&D 报告（Markdown）

{markdown}

---

# 任务

请按照上面的 PPT 设计规范，把这份报告设计成一份 PPT 设计方案。

要求：
1. 仔细阅读报告，理解每节内容的核心信息
2. 按设计规范的 JSON schema 输出设计方案
3. 每页内容要精简：要点 ≤15 字、表格列 ≤5、表格行 ≤8
4. 为不同章节选择不同的 accent 配色变体（blue/teal/amber/slate/indigo），制造视觉节奏
5. 关键数据和发现放入 highlights，关键风险/洞察放入 callout
6. 合理选择 layout 类型（bullets/table/split/quote/comparison/metrics）
7. 必须包含：1 封面 + 1 目录 + N 章节分隔页 + M 内容页 + 1 结尾页
8. 只输出 JSON，不要任何其他文字

输出 JSON："""

    return system_prompt, user_prompt


def design_ppt_slides(markdown: str) -> dict[str, Any]:
    """调用 DeepSeek 生成 PPT 设计方案。

    Args:
        markdown: R&D 报告 Markdown 文本

    Returns:
        设计方案 dict，结构为 {title, theme, slides: [...]}
        失败时返回空 dict。
    """
    system_prompt, user_prompt = _build_design_prompt(markdown)

    client = get_client()
    resp = client.chat.completions.create(
        model=os.environ.get("DEEPSEEK_MODEL", "deepseek-chat"),
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.4,
        max_tokens=8192,
    )
    text = resp.choices[0].message.content.strip()

    # 提取 JSON（LLM 可能偶尔仍带 ```json 包裹）
    # 先尝试直接解析
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # 尝试提取代码块内的 JSON
    m = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            pass

    # 尝试提取第一个 { 到最后一个 } 之间的内容
    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(text[start:end + 1])
        except json.JSONDecodeError:
            pass

    print(f"[ppt_designer] JSON 解析失败，原始返回前500字: {text[:500]}")
    return {}


def _validate_plan(plan: dict) -> bool:
    """校验设计方案基本结构。"""
    if not isinstance(plan, dict):
        return False
    slides = plan.get("slides")
    if not isinstance(slides, list) or len(slides) == 0:
        return False
    return True


def design_ppt_slides_safe(markdown: str) -> dict[str, Any]:
    """安全版：生成设计方案，失败时返回 fallback 空方案。

    返回的 dict 始终包含 "slides" 键（可能为空列表）。
    调用方可通过 plan.get("slides") 是否为空判断是否成功。
    """
    try:
        plan = design_ppt_slides(markdown)
        if _validate_plan(plan):
            return plan
        print("[ppt_designer] 设计方案校验失败，返回空方案")
        return {"title": "", "theme": "blue", "slides": []}
    except Exception as e:
        print(f"[ppt_designer] 生成设计方案异常: {e}")
        return {"title": "", "theme": "blue", "slides": []}


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv(REPO_ROOT / ".env")
    load_dotenv()

    sample = REPO_ROOT / "docs" / "reports" / "2026-06-19-battery-tape-rd-report.md"
    if sample.exists():
        md = sample.read_text(encoding="utf-8")
        print(f"报告长度: {len(md)} 字符\n")
        plan = design_ppt_slides_safe(md)
        print(f"设计方案: {len(plan.get('slides', []))} 页")
        for i, s in enumerate(plan.get("slides", [])):
            t = s.get("type", "?")
            title = s.get("title", s.get("callout", ""))[:40]
            accent = s.get("accent", "")
            layout = s.get("layout", "")
            print(f"  {i+1}. [{t}] {title} | accent={accent} layout={layout}")
    else:
        print(f"未找到测试报告: {sample}")
