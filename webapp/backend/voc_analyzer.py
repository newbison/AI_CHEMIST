"""VOC 分析模块 — 用 LLM 从客户需求拆解出多角度专利搜索策略。

核心思路：VOC 往往包含多个技术维度（产品本体/关键材料/工艺/性能要求）。
直接拿 VOC 原文搜索会丢失语义、且中文检索质量差。本模块用 DeepSeek
把 VOC 拆成 3-5 个技术角度，每个角度生成精准英文搜索关键词，供后续
分别检索 Google Patents 后合并去重，覆盖最全。
"""
from __future__ import annotations

import json
import os
import re
from typing import TypedDict

from openai import OpenAI


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
        model=os.environ.get("DEEPSEEK_MODEL", "deepseek-chat"),
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=1024,
    )
    text = resp.choices[0].message.content.strip()

    # 提取 JSON 数组
    m = re.search(r'\[.*\]', text, re.DOTALL)
    if not m:
        print(f"[voc_analyzer] 未找到 JSON 数组, 原始返回: {text[:200]}")
        return []
    try:
        items = json.loads(m.group())
    except json.JSONDecodeError as e:
        print(f"[voc_analyzer] JSON 解析失败: {e}")
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


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    from pathlib import Path
    load_dotenv(Path(__file__).resolve().parents[2] / ".env")
    load_dotenv()

    voc = "锂电池电芯终止胶带，要求在电解液（碳酸酯类，含 LiPF6）长期浸泡（85°C/72h 及以上）下保持粘接力不脱落、不溶胀、无残胶、不污染电解液"
    print(f"VOC: {voc[:80]}...\n")
    strategies = analyze_voc_to_strategies(voc)
    print(f"生成 {len(strategies)} 条搜索策略:")
    for i, s in enumerate(strategies, 1):
        print(f"  {i}. [{s['angle']}] {s['query']}")
        print(f"     {s['rationale']}")
