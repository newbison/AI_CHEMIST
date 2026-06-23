"""VOC 分析模块 — 用 LLM 从客户需求拆解出多角度专利搜索策略。

核心思路：VOC 往往包含多个技术维度（产品本体/关键材料/工艺/性能要求）。
直接拿 VOC 原文搜索会丢失语义、且中文检索质量差。本模块用 DeepSeek
把 VOC 拆成 3-5 个技术角度，每个角度生成精准英文搜索关键词，供后续
分别检索 Google Patents 后合并去重，覆盖最全。
"""
from __future__ import annotations

import json
import logging
import os
import re
from typing import TypedDict

from openai import OpenAI

from common.json_utils import parse_json_with_fallback, parse_json_array_with_fallback  # noqa: E402

# 配置日志
logger = logging.getLogger(__name__)


class SearchStrategy(TypedDict):
    """单条搜索策略。"""
    angle: str       # 中文角度说明，如"胶粘剂配方"
    query: str       # 英文搜索关键词，如 "acrylic adhesive electrolyte resistant battery"
    rationale: str   # 为什么从这角度搜（简短中文说明）


def _get_client() -> OpenAI:
    key = os.environ.get("DEEPSEEK_API_KEY", "")
    if not key:
        raise RuntimeError("未设置 DEEPSEEK_API_KEY")
    return OpenAI(
        api_key=key,
        base_url=os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
        timeout=60.0,
    )


def analyze_voc_to_strategies(voc: str, *, num_angles: int = 4) -> list[SearchStrategy]:
    """用 LLM 分析 VOC，生成多角度英文专利搜索策略。

    Args:
        voc: 客户需求描述（中英文均可）
        num_angles: 拆解角度数，默认 4

    Returns:
        搜索策略列表，每条含 angle/query/rationale
    """
    client = _get_client()

    prompt = f"""你是专利检索策略专家。分析下面的客户需求(VOC)，拆解出 {num_angles} 个互补的技术角度，
每个角度生成一组精准的英文专利搜索关键词。

VOC:
{voc}

要求：
1. 从产品本体、关键材料、核心工艺、性能/失效机理等维度拆解，角度之间尽量互补不重叠
2. 每组 query 用 3-7 个英文词，是 Google Patents 能精准命中的技术术语组合（不要整句）
3. query 要聚焦"专利里会怎么写这个技术"，而不是泛泛的应用场景
4. 优先能命中 US 专利的英文术语
5. 只返回 JSON 数组，不要任何解释文字

示例（VOC: 锂电池终止胶带，耐电解液浸泡）:
[
  {{"angle": "胶带本体结构", "query": "pressure sensitive adhesive tape battery termination", "rationale": "直接命中终止胶带产品类专利"}},
  {{"angle": "胶粘剂耐电解液配方", "query": "acrylic adhesive electrolyte resistant lithium battery", "rationale": "聚焦胶粘剂配方的耐电解液性能"}},
  {{"angle": "基材与绝缘层", "query": "polyimide PET film insulation battery tape", "rationale": "基材选型与电气绝缘相关专利"}},
  {{"angle": "高温老化与粘接力保持", "query": "adhesive peel strength high temperature electrolyte aging", "rationale": "性能测试与失效机理类专利"}}
]"""

    resp = client.chat.completions.create(
        model=os.environ.get("DEEPSEEK_MODEL", "deepseek-v4-pro"),
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=1024,
    )
    text = resp.choices[0].message.content.strip()

    # 使用公共 JSON 解析函数
    items = parse_json_array_with_fallback(text)
    if not items:
        logger.warning(f"[voc_analyzer] JSON 解析失败, 原始返回: {text[:200]}")
        return []
    if not isinstance(items, list):
        logger.warning(f"[voc_analyzer] 解析结果不是数组: {type(items)}")
        return []

    strategies: list[SearchStrategy] = []
    for item in items[:num_angles]:
        q = (item.get("query") or "").strip()
        if not q:
            continue
        strategies.append(SearchStrategy(
            angle=(item.get("angle") or "").strip(),
            query=q,
            rationale=(item.get("rationale") or "").strip(),
        ))
    return strategies


class ClarifyQuestion(TypedDict):
    """单道澄清问题。"""
    id: str               # "q1", "q2"
    question: str         # 题干
    options: list[str]    # 2-4 个选项
    allow_custom: bool    # 是否允许"以上都不是"+自定义输入


class ClarifyResult(TypedDict):
    """clarify_voc 的返回。"""
    questions: list[ClarifyQuestion]
    analysis: str         # 对 VOC 的简要分析（发现的缺口/矛盾）


class EnrichResult(TypedDict):
    """enrich_voc 的返回。"""
    enriched_voc: str     # 增强版 VOC
    changes: list[str]    # 变更摘要


def clarify_voc(voc: str, *, num_questions: int = 4) -> ClarifyResult:
    """用 LLM 分析 VOC，生成澄清选择题。

    Args:
        voc: 客户需求描述
        num_questions: 问题数量，默认 4（范围 3-5）

    Returns:
        ClarifyResult，含问题和分析。失败时返回空问题列表。
    """
    num_questions = max(3, min(5, num_questions))
    client = _get_client()

    prompt = f"""你是材料科学研发需求分析专家。分析下面的客户需求(VOC)，找出信息缺口和潜在矛盾，
生成 {num_questions} 道单选题帮助用户明确需求。

VOC:
{voc}

要求：
1. 聚焦最关键的信息缺口：应用场景、性能指标数值、约束条件、目标基材/体系、失效机理
2. 每题 2-4 个选项，选项要具体（如"85°C/72h"而非"高温"）
3. 选项要覆盖常见情况，避免都能选/都不能选
4. 不要问 VOC 里已经明确的信息
5. 如发现 VOC 里有矛盾（如"耐高温"但没给温度），优先问矛盾点

只返回 JSON，不要任何解释文字：
{{
  "analysis": "对 VOC 的简要分析（发现的缺口/矛盾，1-2句话）",
  "questions": [
    {{"id": "q1", "question": "题干", "options": ["选项A", "选项B", "选项C"], "allow_custom": true}}
  ]
}}"""

    try:
        resp = client.chat.completions.create(
            model=os.environ.get("DEEPSEEK_MODEL", "deepseek-v4-pro"),
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=2048,
        )
        text = resp.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"[clarify_voc] LLM 调用失败: {e}")
        return ClarifyResult(questions=[], analysis="")

    # 使用公共 JSON 解析函数
    data = parse_json_with_fallback(text, expected_keys=["questions", "analysis"])
    if not data or not isinstance(data, dict):
        logger.warning(f"[clarify_voc] JSON 解析失败, 原始返回: {text[:200]}")
        return ClarifyResult(questions=[], analysis="")

    questions: list[ClarifyQuestion] = []
    for item in (data.get("questions") or [])[:num_questions]:
        qid = (item.get("id") or "").strip()
        question = (item.get("question") or "").strip()
        options = [str(o).strip() for o in (item.get("options") or []) if str(o).strip()]
        allow_custom = bool(item.get("allow_custom", True))
        if qid and question and len(options) >= 2:
            questions.append(ClarifyQuestion(
                id=qid, question=question, options=options, allow_custom=allow_custom,
            ))

    analysis = (data.get("analysis") or "").strip()
    return ClarifyResult(questions=questions, analysis=analysis)


def enrich_voc(
    original_voc: str,
    questions: list[dict],
    answers: dict[str, str],
) -> EnrichResult:
    """根据用户对澄清问题的答案，生成增强版 VOC。

    Args:
        original_voc: 原始 VOC
        questions: 澄清问题列表（含 id/question/options）
        answers: 用户答案 {qid: "选项" 或 "custom:自定义文本"}

    Returns:
        EnrichResult，含增强版 VOC 和变更摘要。失败时返回原 VOC。
    """
    client = _get_client()

    # 构建问答文本
    qa_lines: list[str] = []
    for q in questions:
        qid = q.get("id", "")
        question = q.get("question", "")
        answer = answers.get(qid, "（未回答）")
        qa_lines.append(f"Q: {question}\nA: {answer}")
    qa_text = "\n\n".join(qa_lines) or "（用户跳过了所有问题）"

    prompt = f"""你是材料科学研发需求分析专家。根据用户的原始 VOC 和澄清答案，生成一个增强版 VOC。

原始 VOC:
{original_voc}

澄清问答:
{qa_text}

要求：
1. 保留原始 VOC 的所有信息
2. 把答案中的新信息自然融入（不要简单拼接）
3. 用专业但清晰的语言重写，结构化呈现（产品/材料/性能/约束/目标）
4. 标注哪些是新增信息（用【补充】前缀）
5. 如发现答案与原 VOC 矛盾，以答案为准并标注【修正】

只返回 JSON，不要任何解释文字：
{{
  "enriched_voc": "增强版 VOC 全文",
  "changes": ["补充了应用场景：动力电池电芯", "明确了温度范围：85°C/72h"]
}}"""

    try:
        resp = client.chat.completions.create(
            model=os.environ.get("DEEPSEEK_MODEL", "deepseek-v4-pro"),
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=2048,
        )
        text = resp.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"[enrich_voc] LLM 调用失败: {e}")
        # 降级：简单拼接
        return EnrichResult(
            enriched_voc=original_voc + "\n\n【澄清补充】\n" + qa_text,
            changes=["LLM 调用失败，已简单拼接答案"],
        )

    # 使用公共 JSON 解析函数
    data = parse_json_with_fallback(text, expected_keys=["enriched_voc", "changes"])
    if not data or not isinstance(data, dict):
        logger.warning(f"[enrich_voc] JSON 解析失败, 原始返回: {text[:200]}")
        return EnrichResult(
            enriched_voc=original_voc + "\n\n【澄清补充】\n" + qa_text,
            changes=["LLM 返回解析失败，已简单拼接答案"],
        )

    enriched = (data.get("enriched_voc") or "").strip() or original_voc
    changes = [str(c).strip() for c in (data.get("changes") or []) if str(c).strip()]
    return EnrichResult(enriched_voc=enriched, changes=changes)


class VocIdea(TypedDict):
    """一条 AI 生成的 VOC 创意。"""
    voc: str
    why: str


def generate_voc_ideas(
    product: str,
    context: str = "",
    direction: str = "",
    *,
    num_ideas: int = 10,
) -> list[VocIdea]:
    """用 LLM 生成 VOC 创意供用户选择。

    Args:
        product: 产品类别，如 "UV-curable hard coats for automotive glazing"
        context: 行业背景/痛点，如 "Our formulation yellows after 2 years"
        direction: 创新方向，"next-gen" / "cost-down" / "adjacent" / ""
        num_ideas: 生成创意数，默认 10

    Returns:
        VocIdea 列表。失败时返回空列表。
    """
    client = _get_client()

    direction_hint = ""
    if direction == "next-gen":
        direction_hint = (
            "Focus on breakthrough performance improvements: "
            "next-generation materials, novel architectures, "
            "step-change in key properties."
        )
    elif direction == "cost-down":
        direction_hint = (
            "Focus on cost reduction: cheaper raw materials, "
            "simpler processing, fewer steps, higher throughput."
        )
    elif direction == "adjacent":
        direction_hint = (
            "Focus on adjacent market opportunities: new applications, "
            "cross-industry technology transfer, different use cases."
        )

    prompt = f"""You are a materials science R&D strategist. A company makes this product:

Product: {product}
{f"Context: {context}" if context else ""}
{f"Direction: {direction_hint}" if direction_hint else ""}

Generate {num_ideas} specific, well-formed research questions (VOCs) that
this company should investigate. Each VOC should be like a customer
requirement that can be researched through patent analysis.

Requirements for each VOC:
1. Be specific: name the material system, include target property values
   with numbers, mention test methods if relevant
2. Vary across different technical approaches — not just minor variations
   of the same idea
3. Write like a real customer need: "We need X material with Y property
   > Z value under W conditions..."
4. For each VOC, write a 1-2 sentence "why" explaining the
   technical/commercial importance

Return ONLY a JSON array, no other text:
[
  {{
    "voc": "We need a UV-curable hard coat for polycarbonate with 9H...",
    "why": "The current market leader offers 5-year weatherability but..."
  }}
]"""

    try:
        resp = client.chat.completions.create(
            model=os.environ.get("DEEPSEEK_MODEL", "deepseek-v4-pro"),
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=4096,
        )
        text = resp.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"[generate_voc_ideas] LLM call failed: {e}")
        return []

    # 使用公共 JSON 解析函数
    items = parse_json_array_with_fallback(text)
    if not items:
        logger.warning(f"[generate_voc_ideas] JSON 解析失败, 原始返回: {text[:200]}")
        return []
    if not isinstance(items, list):
        logger.warning(f"[generate_voc_ideas] 解析结果不是数组: {type(items)}")
        return []

    ideas: list[VocIdea] = []
    for item in items[:num_ideas]:
        voc = (item.get("voc") or "").strip()
        why = (item.get("why") or "").strip()
        if voc:
            ideas.append(VocIdea(voc=voc, why=why))

    return ideas


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    from pathlib import Path
    load_dotenv(Path(__file__).resolve().parents[2] / ".env")
    load_dotenv()

    # Test generate_voc_ideas
    ideas = generate_voc_ideas("UV-curable hard coats for automotive glazing")
    print(f"Generated {len(ideas)} ideas:")
    for i, idea in enumerate(ideas, 1):
        print(f"  {i}. {idea['voc'][:80]}...")
        print(f"     {idea['why'][:80]}...")

    voc = "锂电池电芯终止胶带，要求在电解液（碳酸酯类，含 LiPF6）长期浸泡（85°C/72h 及以上）下保持粘接力不脱落、不溶胀、无残胶、不污染电解液"
    print(f"VOC: {voc[:80]}...\n")
    strategies = analyze_voc_to_strategies(voc)
    print(f"生成 {len(strategies)} 条搜索策略:")
    for i, s in enumerate(strategies, 1):
        print(f"  {i}. [{s['angle']}] {s['query']}")
        print(f"     {s['rationale']}")
