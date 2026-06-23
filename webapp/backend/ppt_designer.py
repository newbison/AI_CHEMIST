"""PPT 设计器 — 调用 DeepSeek 读取 ppt-design-skill，把 Markdown 报告转成 PptxGenJS 代码。

流程：
  Markdown 报告 + SKILL.md + pptxgenjs.md → DeepSeek → PptxGenJS JS 代码
  → 写入临时 .js 文件 → node 执行 → 输出 .pptx 文件 → 返回字节流

相比旧的 JSON→python-pptx 方案，PptxGenJS 生成的 PPT 设计质量更高，
支持丰富的形状、阴影、图标、图表等 python-pptx 难以实现的效果。
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

from llm_client import get_client


REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL_DIR = REPO_ROOT / "ppt-design-skill"
SKILL_FILE = SKILL_DIR / "SKILL.md"
PPTXGENJS_FILE = SKILL_DIR / "pptxgenjs.md"


def _load_file(path: Path) -> str:
    """读取文件内容，文件不存在返回空字符串。"""
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _build_design_prompt(markdown: str) -> tuple[str, str]:
    """构建 (system_prompt, user_prompt) 用于 PptxGenJS 代码生成。

    system: 前端工程师角色 + 输出格式要求
    user: skill 规范 + PptxGenJS API 参考 + 报告原文 + 任务指令
    """
    skill_text = _load_file(SKILL_FILE)
    pptxgenjs_ref = _load_file(PPTXGENJS_FILE)

    system_prompt = """你是一个专业的前端工程师，擅长使用 PptxGenJS 库创建精美的 PowerPoint 演示文稿。

你的任务：阅读一份 R&D 报告（Markdown），根据设计规范，编写一段完整的 Node.js 脚本，
使用 pptxgenjs 库生成一个专业、美观的 .pptx 文件。

你必须只输出 JavaScript 代码，不要输出任何 Markdown 代码块标记（如 ```js）、
不要任何解释文字。代码必须：
1. 语法正确，可直接被 Node.js 执行
2. 所有颜色值不带 # 前缀（如 "1A3C6E" 而非 "#1A3C6E"）
3. 使用 breakLine: true 分隔多行文本
4. 使用 bullet: true 而非 Unicode 项目符号
5. 不重复使用 option 对象（每次调用创建新对象）
6. 以 console.log("DONE: output.pptx") 结尾"""

    user_prompt = f"""# PPT 设计规范

{skill_text}

---

# PptxGenJS API 参考

{pptxgenjs_ref}

---

# 待设计的 R&D 报告（Markdown）

{markdown}

---

# 任务

请按照设计规范，编写一段完整的 Node.js 脚本，使用 pptxgenjs 生成这份报告的 PPT。

要求：
1. 仔细阅读报告，理解每节内容的核心信息
2. 选择合适的配色方案（从设计规范的调色板中选，不要用默认蓝色）
3. 每页内容要精简：要点 ≤15 字、表格列 ≤5、表格行 ≤8
4. 不同章节使用不同的 accent 配色变体，制造视觉节奏
5. 关键数据和发现用大字号或高亮色突出
6. 合理变化布局（bullets / table / split / quote / comparison / metrics）
7. 必须包含：1 封面 + 1 目录 + N 章节分隔页 + M 内容页 + 1 结尾页
8. 使用 pres.writeFile({{ fileName: "output.pptx" }}) 保存文件
9. 最后一行：console.log("DONE: output.pptx");

只输出 JavaScript 代码，不要任何其他文字。"""

    return system_prompt, user_prompt


def design_pptx_js(markdown: str) -> str:
    """调用 DeepSeek 生成 PptxGenJS JavaScript 代码。

    Args:
        markdown: R&D 报告 Markdown 文本

    Returns:
        PptxGenJS JavaScript 代码字符串。失败时返回空字符串。
    """
    system_prompt, user_prompt = _build_design_prompt(markdown)

    client = get_client()
    resp = client.chat.completions.create(
        model=os.environ.get("DEEPSEEK_MODEL", "deepseek-v4-pro"),
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.4,
        max_tokens=16384,
    )
    text = resp.choices[0].message.content.strip()

    # 清理可能的 Markdown 代码块包裹
    # 尝试提取 ```js ... ``` 或 ```javascript ... ``` 内的代码
    m = re.search(r'```(?:js|javascript)?\s*\n?(.*?)\n?```', text, re.DOTALL)
    if m:
        code = m.group(1).strip()
    else:
        code = text

    # 基本验证：代码必须包含 pptxgenjs 引用
    if 'pptxgenjs' not in code.lower() and 'require' not in code:
        print("[ppt_designer] 生成的代码未包含 pptxgenjs 引用，可能无效")
        return ""

    # 基本验证：必须有 writeFile 调用
    if 'writeFile' not in code and 'writeFile' not in code:
        print("[ppt_designer] 生成的代码未包含 writeFile 调用，可能无效")
        return ""

    return code


def design_pptx_js_safe(markdown: str) -> str:
    """安全版：生成 PptxGenJS 代码，失败时返回空字符串。

    调用方可通过返回值是否为空判断是否成功。
    """
    try:
        code = design_pptx_js(markdown)
        if code:
            return code
        print("[ppt_designer] DeepSeek 返回空代码")
        return ""
    except Exception as e:
        import traceback
        print(f"[ppt_designer] 生成 PptxGenJS 代码异常: {e}")
        traceback.print_exc()
        return ""


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv(REPO_ROOT / ".env")
    load_dotenv()

    sample = REPO_ROOT / "docs" / "reports" / "2026-06-19-battery-tape-rd-report.md"
    if sample.exists():
        md = sample.read_text(encoding="utf-8")
        print(f"报告长度: {len(md)} 字符\n")
        code = design_pptx_js_safe(md)
        if code:
            out = SKILL_DIR / "_test_script.js"
            out.write_text(code, encoding="utf-8")
            print(f"代码长度: {len(code)} 字符 → 已写入 {out}")
        else:
            print("生成失败")
    else:
        print(f"未找到测试报告: {sample}")
