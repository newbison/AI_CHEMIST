"""VOC Scout — 交互式技术全景探索模块。

两轮对话流程：
  Round 1: 给定原始 VOC，搜索并呈现 4-6 个技术方向，用户多选 N 个。
  Round 2: 钻入选定方向——展示公司、专利、关键 CTQ 值、FTO 备注。
  输出:    "三件套"（公司 + 关键词 + IPC + FTO 备注），供 Deep Search 使用。

市场份额搜索（Step 0）在专利搜索之前运行——专利数 ≠ 市场地位。

Deep Search 由 deep_search.py 处理，本模块只做交互式 scout 阶段。
"""
from __future__ import annotations

import json
import os
import re
from openai import OpenAI
from pydantic import BaseModel, Field


# -- Round 1 类型 -------------------------------------------------------------

class ScoutTechRoute(BaseModel):
    """Round 1 中呈现给用户的单个技术方向。"""
    id: str = Field(description="路线标识，如 '1', '2'")
    name: str = Field(description="简称，如 'BASF 路线 — 高固含通用型'")
    description: str = Field(description="1-2 句技术概述")
    companies: list[str] = Field(default_factory=list, description="代表公司")
    products: list[str] = Field(default_factory=list, description="已知产品名")
    key_diff: str = Field(default="", description="关键差异点")
    patent_status_hint: str = Field(default="", description="'expired' | 'active' | 'pending'")
    confidence: str = Field(default="★★☆", description="该路线置信度")


class ScoutRound1Output(BaseModel):
    """VOC Scout Round 1 输出。"""
    domain_class: str = Field(description="如 '材料/化工', '电子', '医疗', '法规驱动型'")
    confidence: str = Field(default="★★☆", description="总体置信度: ★★★ / ★★☆ / ★☆☆")
    analysis: str = Field(description="VOC 领域与发现的简短分析")
    routes: list[ScoutTechRoute] = Field(description="4-6 个技术方向")
    contradictions: list[str] = Field(default_factory=list, description="标注的矛盾点")


# -- Round 2 类型 -------------------------------------------------------------

class ScoutCompanyDetail(BaseModel):
    """Round 2 中某条路线下一家公司的详情。"""
    level: str = Field(description="P0 (必看) / P1 (重要) / P2 (参考)")
    name: str
    tech_summary: str = Field(description="1-2 句技术描述")
    patent_number: str = Field(default="")
    patent_status: str = Field(default="", description="expired / active / pending / ''")
    key_ctq: dict[str, str] = Field(default_factory=dict, description="CTQ 名 -> 值 + 来源")
    notes: list[str] = Field(default_factory=list)
    source_labels: list[str] = Field(default_factory=list, description="[P] [T] [A] [D] 等")


class ScoutRouteDetail(BaseModel):
    """Round 2 中某条技术路线的展开详情。"""
    route_id: str
    route_name: str
    companies: list[ScoutCompanyDetail] = Field(default_factory=list)


class ScoutRound2Input(BaseModel):
    """Round 2 输入。"""
    voc: str
    selected_route_ids: list[str] = Field(min_length=1, description="用户在 Round 1 选中的 ID")
    focus: str = Field(default="", description="可选用户备注，如 '只看胶带级'")


class ScoutRound2Output(BaseModel):
    """Round 2 输出。"""
    routes: list[ScoutRouteDetail]
    contradictions: list[str] = Field(default_factory=list)
    confidence: str = Field(default="★★☆")


# -- LLM 客户端 ---------------------------------------------------------------

def _get_llm_client() -> OpenAI:
    key = os.environ.get("DEEPSEEK_API_KEY", "")
    if not key:
        raise RuntimeError("DEEPSEEK_API_KEY not set")
    return OpenAI(
        api_key=key,
        base_url=os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
        timeout=120.0,
    )


def _parse_json_safe(raw: str) -> dict | None:
    """解析 JSON，兼容 markdown 代码围栏。"""
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            pass
    m2 = re.search(r"\{.*\}", raw, re.DOTALL)
    if m2:
        try:
            return json.loads(m2.group())
        except json.JSONDecodeError:
            pass
    return None


# -- 市场份额搜索（Step 0，专利搜索之前） -------------------------------------

MARKET_SHARE_SYSTEM = """You are a market research analyst. Given an industry/product name,
identify the TOP 10 global suppliers by market share (revenue or unit volume).

Search for:
  English: "<industry> global market share top suppliers 2024"
  Chinese: "<行业> 市场规模 竞争格局 龙头企业"

Output ONLY valid JSON:
{
  "market_size": {"value": 4300, "unit": "million USD", "year": 2024, "source": "[D]"},
  "top_suppliers": [
    {"rank": 1, "name": "3M", "country": "US", "share_pct": 15, "source": "[D]"}
  ],
  "concentration": "CR5 = 35%",
  "notes": "Additional observations"
}"""


def market_share_search(voc: str, industry_hint: str = "") -> dict:
    """双语市场份额搜索，按销量/收入识别头部供应商。

    在任何专利搜索之前运行。专利数不是市场地位的代理指标。

    Args:
        voc: 原始 VOC 文本
        industry_hint: 可选的行业名覆盖

    Returns:
        含 market_size、top_suppliers (按份额排序)、concentration 的字典。
    """
    client = _get_llm_client()
    industry = industry_hint or voc
    prompt = (
        f"Industry/Product: {industry}\n\n"
        "Find the latest market share rankings. Search in both English and Chinese."
    )
    resp = client.chat.completions.create(
        model=os.environ.get("DEEPSEEK_MODEL", "deepseek-v4-pro"),
        messages=[
            {"role": "system", "content": MARKET_SHARE_SYSTEM},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
        max_tokens=2048,
        response_format={"type": "json_object"},
        extra_body={"thinking": {"type": "disabled"}},
    )
    raw = resp.choices[0].message.content.strip()
    data = _parse_json_safe(raw)
    return data if data else {"top_suppliers": [], "notes": "Market share search failed"}


# -- Round 1 执行 -------------------------------------------------------------

SCOUT_ROUND1_SYSTEM = """You are a patent search strategist specializing in materials science,
chemical engineering, electronics, and medical devices.

Your task: Given a raw customer requirement (VOC), do two things:
1. Classify the VOC domain (材料/化工, 电子, 医疗, 法规驱动型, 机械)
2. Identify 4-6 distinct technology routes/directions in this field

For each route, provide:
- id: "1", "2", etc.
- name: "<Company> route — <feature>" format
- description: 1-2 sentence technical summary
- companies: list of representative company names
- products: known product/brand names (empty list if none found)
- key_diff: one key differentiator (e.g. "69% solids, core patent expired")
- patent_status_hint: "expired" | "active" | "pending" | ""
- confidence: ★★★ (high) / ★★☆ (medium) / ★☆☆ (low) per route

Also flag any obvious contradictions in the VOC (e.g. "high solids + low viscosity"
are inherently in tension).

Rules:
- Output 4-6 routes. Do NOT output fewer than 4.
- Every route MUST name at least one company.
- Use your training data + real knowledge of the industry.
- Do NOT fabricate patent numbers in this round.
- Do NOT use generic labels like "Option A / Option B".
- Return ONLY valid JSON, no markdown fences, no explanation text.

Output JSON schema:
{
  "domain_class": "...",
  "confidence": "★★☆",
  "analysis": "1-2 sentence analysis...",
  "routes": [
    {
      "id": "1",
      "name": "...",
      "description": "...",
      "companies": ["..."],
      "products": ["..."],
      "key_diff": "...",
      "patent_status_hint": "...",
      "confidence": "★★☆"
    }
  ],
  "contradictions": []
}"""


def scout_round1(voc: str, market_share: dict | None = None) -> ScoutRound1Output:
    """执行 VOC Scout Round 1：探索技术方向。

    Args:
        voc: 客户需求文本（中/英）
        market_share: 来自 market_share_search() 的市场份额数据，用于按真实市场地位
            排序路线选项，而非按专利数。

    Returns:
        含领域分类、4-6 条路线、初始分析的 ScoutRound1Output。

    Raises:
        ValueError: VOC 为空或仅空白时。
    """
    voc = voc.strip()
    if not voc:
        raise ValueError("VOC cannot be empty")

    client = _get_llm_client()
    user_prompt = f"VOC: {voc}"
    if market_share and market_share.get("top_suppliers"):
        # 把市场份额头部供应商注入 prompt，让模型优先围绕真实市场玩家组织路线
        top = market_share["top_suppliers"][:10]
        user_prompt += (
            "\n\nMarket share context (use to prioritize real market players in routes):\n"
            + json.dumps(top, ensure_ascii=False)
        )

    resp = client.chat.completions.create(
        model=os.environ.get("DEEPSEEK_MODEL", "deepseek-v4-pro"),
        messages=[
            {"role": "system", "content": SCOUT_ROUND1_SYSTEM},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.4,
        max_tokens=4096,
        response_format={"type": "json_object"},
        extra_body={"thinking": {"type": "disabled"}},
    )
    raw = resp.choices[0].message.content.strip()

    data = _parse_json_safe(raw)
    if data is None:
        raise RuntimeError(f"scout_round1: failed to parse LLM output: {raw[:500]}")

    routes = [
        ScoutTechRoute(
            id=r.get("id", str(i + 1)),
            name=r.get("name", ""),
            description=r.get("description", ""),
            companies=r.get("companies", []),
            products=r.get("products", []),
            key_diff=r.get("key_diff", ""),
            patent_status_hint=r.get("patent_status_hint", ""),
            confidence=r.get("confidence", "★★☆"),
        )
        for i, r in enumerate(data.get("routes", []))
    ]

    # 若有市场份额数据，把头部供应商名合并进匹配路线的公司列表并前置
    if market_share and market_share.get("top_suppliers"):
        share_by_name = {
            (s.get("name") or "").lower(): s.get("share_pct", 0)
            for s in market_share["top_suppliers"]
        }

        def _route_market_score(route: ScoutTechRoute) -> float:
            return max(
                (share_by_name.get(c.lower(), 0) for c in route.companies),
                default=0,
            )

        routes.sort(key=_route_market_score, reverse=True)

    return ScoutRound1Output(
        domain_class=data.get("domain_class", ""),
        confidence=data.get("confidence", "★★☆"),
        analysis=data.get("analysis", ""),
        routes=routes[:6],  # 强制最多 6 条
        contradictions=data.get("contradictions", []),
    )


# -- Round 2 执行 -------------------------------------------------------------

SCOUT_ROUND2_SYSTEM = """You are a patent search strategist specializing in materials science
and engineering. The user has selected specific technology routes from Round 1.
Now drill deeper into each selected route.

For EACH selected route, provide:
- Key companies working in this direction
- For each company: core patent number + status (expired/active/pending), key CTQ values with numbers, source labels ([P]=patent, [T]=product TDS, [A]=paper, [D]=domain knowledge)
- Priority ranking: P0 (market leader with commercial products), P1 (important player), P2 (reference only)

Also flag contradictions between the user's selections and practical reality.

Output ONLY valid JSON matching this schema:
{
  "routes": [
    {
      "route_id": "1",
      "route_name": "...",
      "companies": [
        {
          "level": "P0",
          "name": "...",
          "tech_summary": "...",
          "patent_number": "...",
          "patent_status": "expired",
          "key_ctq": {"solid_content": "69%", "source": "[T]"},
          "notes": ["..."],
          "source_labels": ["[T]", "[P]"]
        }
      ]
    }
  ],
  "contradictions": [],
  "confidence": "★★☆"
}"""


def scout_round2(inp: ScoutRound2Input) -> ScoutRound2Output:
    """执行 VOC Scout Round 2：钻入选定路线。

    Args:
        inp: Round 2 输入（选中路线 ID + 可选 focus）

    Returns:
        含每条路线公司详情的 ScoutRound2Output。
    """
    client = _get_llm_client()
    user_prompt = (
        f"VOC: {inp.voc}\n"
        f"Selected routes: {inp.selected_route_ids}\n"
        + (f"User focus: {inp.focus}\n" if inp.focus else "")
    )

    resp = client.chat.completions.create(
        model=os.environ.get("DEEPSEEK_MODEL", "deepseek-v4-pro"),
        messages=[
            {"role": "system", "content": SCOUT_ROUND2_SYSTEM},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
        max_tokens=8192,
        response_format={"type": "json_object"},
        extra_body={"thinking": {"type": "disabled"}},
    )
    raw = resp.choices[0].message.content.strip()

    data = _parse_json_safe(raw)
    if data is None:
        raise RuntimeError(f"scout_round2: failed to parse LLM output: {raw[:500]}")

    routes = []
    for rd in data.get("routes", []):
        companies = []
        for cd in rd.get("companies", []):
            companies.append(ScoutCompanyDetail(
                level=cd.get("level", "P2"),
                name=cd.get("name", ""),
                tech_summary=cd.get("tech_summary", ""),
                patent_number=cd.get("patent_number", ""),
                patent_status=cd.get("patent_status", ""),
                key_ctq=cd.get("key_ctq", {}),
                notes=cd.get("notes", []),
                source_labels=cd.get("source_labels", []),
            ))
        routes.append(ScoutRouteDetail(
            route_id=rd.get("route_id", ""),
            route_name=rd.get("route_name", ""),
            companies=companies,
        ))

    return ScoutRound2Output(
        routes=routes,
        contradictions=data.get("contradictions", []),
        confidence=data.get("confidence", "★★☆"),
    )
