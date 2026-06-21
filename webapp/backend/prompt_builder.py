"""Prompt 构建模块 — 加载两个 skill 的文件，拼接成 prompt。

策略（避免 system prompt 过长导致 LLM 输出质量下降）：
- system prompt：仅角色描述 + 核心规则（精简，~1K 字符）
- user prompt：VOC + 专利 + 全部 skill 参考材料（工作流/rubric/模板）
"""

from __future__ import annotations

from pathlib import Path

# skill 根目录（webapp/backend 的上两级）
REPO_ROOT = Path(__file__).resolve().parents[2]
ORCHESTRATOR_DIR = REPO_ROOT / "rd-portfolio-rd-intelligence"
EXTRACTOR_DIR = REPO_ROOT / "patent-xy-extraction-skill"


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""


def _read_dir_files(dir_path: Path, pattern: str = "*.md", exclude: set[str] | None = None) -> str:
    """读取目录下所有匹配文件，拼接带文件名标注的内容。

    exclude: 要跳过的文件名集合（如 README.md），用于精简 prompt。
    """
    if not dir_path.is_dir():
        return ""
    exclude = exclude or set()
    parts: list[str] = []
    for f in sorted(dir_path.glob(pattern)):
        if f.name in exclude:
            continue
        content = _read(f)
        if content:
            parts.append(f"### 文件: {f.relative_to(REPO_ROOT)}\n\n{content}")
    return "\n\n---\n\n".join(parts)


# 精简策略：跳过辅助材料，只保留核心流程文件
# 这样能把参考材料从 ~70KB 压缩到 ~45KB，显著降低首 token 延迟
_SKIP_FILES = {"README.md"}


def build_system_prompt(language: str = "en") -> str:
    """构建精简的 system prompt — 仅角色 + 核心规则。

    重内容（workflow/rubric/template/schema）移到 user prompt，
    避免 system prompt 过长导致模型指令遵循能力下降。
    """
    if language == "zh":
        return (
            "# 你的角色\n\n"
            "你是一个 R&D 智能报告生成器，同时扮演两个角色：\n"
            "1. **rd-portfolio-rd-intelligence**（编排器）— VOC→CTQ→证据挖掘→"
            "专利检索排序→专利抽取→X-Y 综合→风险筛查→DOE 设计→后实验学习→组合复制。\n"
            "2. **patent-xy-extraction-skill**（抽取器）— 从专利中抽取 X/Y/DOE/X-Y 关系。\n\n"
            "用户会给你 VOC 和专利列表，以及完整的工作流/rubric/模板参考材料（在用户消息末尾）。"
            "你需要按编排器 workflow 01→09 顺序执行，在 04 步调用抽取器，"
            "最终产出一份完整的 R&D 智能报告（Markdown 格式）。\n\n"
            "## 关键规则\n"
            "- 严格遵循用户消息中给出的 workflow 和 rubric\n"
            "- 每条抽取必须标注层级：[事实]专利披露 / [抽取]AI规范化 / [推断]AI推断 / "
            "[假设]R&D假设 / [DOE]实验建议\n"
            "- 每个 X-Y 关系必须带：证据等级(0-5)、置信度、测试范围、混杂因素\n"
            "- 不要把专利 claim 当作实验证据\n"
            "- 不要给出法律 FTO 结论\n"
            "- 报告结构遵循用户消息中的 final_report_template\n"
            "- 直接输出报告正文，不要解释你将要做什么\n"
            "- **保持输出语言一致**：用中文撰写报告正文，"
            "英文仅用于专有名词（如专利号、公司名、技术术语）"
        )
    else:
        return (
            "# Your Role\n\n"
            "You are an R&D intelligence report generator playing two roles:\n"
            "1. **rd-portfolio-rd-intelligence** (orchestrator) — VOC→CTQ→evidence mining→"
            "patent search and ranking→patent extraction→X-Y synthesis→risk screening→DOE design→"
            "post-experiment learning→portfolio replication.\n"
            "2. **patent-xy-extraction-skill** (extractor) — extract X/Y/DOE/X-Y relationships from patents.\n\n"
            "The user will give you a VOC and a list of patents, along with complete workflow/rubric/template "
            "reference materials (at the end of the user message). "
            "Follow the orchestrator workflow 01→09 in order, call the extractor at step 04, "
            "and produce a complete R&D intelligence report (Markdown format).\n\n"
            "## Key Rules\n"
            "- Strictly follow the workflow and rubric in the user message\n"
            "- Label each extraction with its tier: [Fact] patent disclosure / [Extracted] AI normalization / "
            "[Inferred] AI inference / [Hypothesis] R&D hypothesis / [DOE] experiment suggestion\n"
            "- Each X-Y relationship must include: evidence level (0-5), confidence, test scope, confounding factors\n"
            "- Do not treat patent claims as experimental evidence\n"
            "- Do not give legal FTO conclusions\n"
            "- Report structure follows the final_report_template in the user message\n"
            "- Output the report directly without explaining what you will do\n"
            "- **Maintain consistent output language**: write the report in English. "
            "Use other languages only for proper nouns (patent numbers, company names, technical terms)."
        )


def _build_skill_reference() -> str:
    """构建 skill 参考材料块（移到 user prompt 末尾）。

    精简策略：跳过 README.md、examples/、references/ 目录，
    只保留 SKILL.md、workflows、rubrics、templates、schemas、HANDOFF.md。
    这样能把参考材料从 ~70KB 压缩到 ~45KB，显著降低首 token 延迟。
    """
    parts: list[str] = []
    parts.append("# 参考材料：编排器 Skill (rd-portfolio-rd-intelligence)\n")
    parts.append(f"## SKILL.md\n\n{_read(ORCHESTRATOR_DIR / 'SKILL.md')}")
    parts.append(f"## Workflows\n\n{_read_dir_files(ORCHESTRATOR_DIR / 'workflows', exclude=_SKIP_FILES)}")
    parts.append(f"## Rubrics\n\n{_read_dir_files(ORCHESTRATOR_DIR / 'rubrics', exclude=_SKIP_FILES)}")
    parts.append(f"## Templates\n\n{_read_dir_files(ORCHESTRATOR_DIR / 'templates', exclude=_SKIP_FILES)}")

    parts.append("\n\n# 参考材料：抽取器 Skill (patent-xy-extraction-skill)\n")
    parts.append(f"## SKILL.md\n\n{_read(EXTRACTOR_DIR / 'SKILL.md')}")
    parts.append(f"## HANDOFF.md（组合契约）\n\n{_read(EXTRACTOR_DIR / 'HANDOFF.md')}")
    parts.append(f"## Workflows\n\n{_read_dir_files(EXTRACTOR_DIR / 'workflows', exclude=_SKIP_FILES)}")
    parts.append(f"## Rubrics\n\n{_read_dir_files(EXTRACTOR_DIR / 'rubrics', exclude=_SKIP_FILES)}")
    parts.append(f"## Templates\n\n{_read_dir_files(EXTRACTOR_DIR / 'templates', exclude=_SKIP_FILES)}")
    parts.append(f"## Schema\n\n{_read_dir_files(EXTRACTOR_DIR / 'schemas', '*.json')}")

    return "\n\n---\n\n".join(parts)


def build_user_prompt(
    voc: str,
    patents: list[dict],
    doc_analysis: str | None = None,
) -> str:
    """构建 user prompt：任务指令 → VOC → 入选专利 → 参考材料。

    任务指令放最前面，确保模型带着目的去读专利详情。
    """
    parts: list[str] = []

    # 统计有/无详情的专利数
    with_detail = sum(1 for p in patents if p.get("detail_text"))
    without_detail = len(patents) - with_detail

    # ---- 任务指令（放最前面！模型先知道要做什么，再读专利） ----
    # 控制分析深度：专利太多时，选最相关的深入分析
    max_deep = min(len(patents), 15)  # 最多深度分析 15 篇
    parts.append(
        "# 任务：深度分析专利并生成 R&D 智能报告\n\n"
        f"下方共有 {len(patents)} 篇专利（其中 {with_detail} 篇包含完整文本）。\n"
        f"**重要：你只需要深度分析其中最相关的 {max_deep} 篇，其余的可简要归类。**\n\n"
        "## 工作流程\n"
        f"1. 快速浏览所有 {len(patents)} 篇专利的摘要，按与 VOC 的相关性排序\n"
        f"2. 选出最相关的 {max_deep} 篇，逐篇阅读完整文本（Claims + Description）\n"
        "3. 对每篇深度分析的专利，抽取 X→Y 关系并标注层级\n"
        "4. 横向比较不同专利的技术方案\n"
        "5. 生成完整报告\n\n"
        "## 关键要求\n"
        "- **深度分析**：对选中的专利，逐篇提取具体的 X（材料/组分/工艺参数）"
        "  → Y（性能/效果）数值关系，标注层级（事实/抽取/推断/假设/DOE）\n"
        "- **必须引用专利号**：每条技术发现标注来源专利号\n"
        "- **写具体数值**：不要写「提高了粘接力」，要写「粘接力从 3.2N/cm 提升到 8.7N/cm」\n"
        "- **横向对比**：用表格比较不同专利的技术方案、性能数据、适用场景\n"
        "- **不要泛泛而谈**：禁止「该领域有多种方案」这类空话\n"
        "- **每个章节都要有内容**：不要输出空章节。如果某个章节没有足够信息，"
        "写明「基于现有专利数据不足以完成此章节，建议补充 XX 实验」\n\n"
        "报告结构遵循 final_report_template。"
        "直接输出报告正文。"
    )

    # ---- VOC ----
    parts.append(f"# 用户 VOC\n\n{voc}\n")

    # ---- 文档分析（用户上传的参考资料）----
    if doc_analysis:
        parts.append(f"# 用户上传的参考资料分析\n\n{doc_analysis}\n")

    # ---- 入选专利（详情文本附在每篇后面） ----
    # 智能截断：优先保留 Abstract + Claims，Description 按剩余预算截断
    # 专利多时压缩 Description 而非砍掉 Claims
    if len(patents) > 25:
        desc_budget = 0       # 超大批量：只保留 Abstract + Claims
    elif len(patents) > 15:
        desc_budget = 1500    # 大批量：Description 保留 1500 字符
    elif len(patents) > 8:
        desc_budget = 3000    # 中批量
    else:
        desc_budget = 5000    # 小批量：保留完整 Description

    parts.append(f"# 入选专利（共 {len(patents)} 篇，{with_detail} 篇有完整文本）\n")
    for i, p in enumerate(patents, 1):
        has_detail = bool(p.get("detail_text"))
        marker = "【完整文本】" if has_detail else "【仅摘要】"
        parts.append(
            f"## 专利 {i}: {p.get('patent_number', 'N/A')} {marker}\n"
            f"- 标题: {p.get('title', 'N/A')}\n"
            f"- 受让人: {p.get('assignee', 'N/A')}\n"
            f"- 公开日: {p.get('publication_date', 'N/A')}\n"
            f"- 来源: {p.get('source', 'N/A')} | {p.get('url', '')}\n"
            f"- 摘要/片段:\n{p.get('snippet', 'N/A')}\n"
        )
        if has_detail:
            detail = _truncate_detail(p['detail_text'], desc_budget)
            parts.append(f"- 详情文本:\n{detail}\n")

    # ---- 参考材料（skill 文件放末尾） ----
    parts.append(_build_skill_reference())

    return "\n\n".join(parts)


def _truncate_detail(detail_text: str, desc_budget: int) -> str:
    """智能截断专利详情：保留 Abstract+Claims 完整，按预算截断 Description。

    结构: [Abstract]\n...\n\n[Inventors]\n...\n\n[Assignee]\n...\n\n
           [Claims]\n...\n\n[Description]\n...
    """
    if desc_budget >= 5000:
        return detail_text  # 不超过 5000 时直接全保留（实际约 10K）

    # 找到 [Description] 的位置
    desc_start = detail_text.find("\n[Description] ")
    if desc_start == -1:
        desc_start = detail_text.find("[Description] ")

    if desc_start == -1:
        # 没有 Description 段，直接截总长
        return detail_text[:6000]

    # 保留 Description 之前的所有内容（Abstract+Inventors+Assignee+Claims）
    before_desc = detail_text[:desc_start].strip()
    description = detail_text[desc_start:]

    if desc_budget == 0:
        return before_desc + f"\n[Description] (已截断，共省略 {len(description)} 字符)"

    # 截断 Description 到预算
    truncated_desc = description[:desc_budget]
    omitted = len(description) - len(truncated_desc)
    if omitted > 0:
        truncated_desc += f"...(省略 {omitted} 字符)"

    return before_desc + "\n" + truncated_desc


if __name__ == "__main__":
    sp = build_system_prompt()
    print(f"System prompt 长度: {len(sp)} 字符")
    print(f"前 500 字符:\n{sp[:500]}")

    # 也看一下参考材料的长度
    ref = _build_skill_reference()
    print(f"\nSkill 参考材料长度: {len(ref)} 字符")
