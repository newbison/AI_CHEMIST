"""Deep Search — 三轮迭代专利全景检索引擎。

消费 VOC Scout 输出（公司 + 关键词 + IPC + FTO 备注），运行迭代检索，
产出完整专利全景：
  - 公司/专利完整映射
  - CTQ 对比表（带来源标签）
  - 技术路线分类
  - FTO 风险评估
  - 短/中/长期建议

三轮方法论：
  Round 1: 公司定向搜索 + 关键词/IPC 扫描
  Round 2: 提取新词 → 用新关键词再搜
  Round 3: 收敛验证（无新路线 → 完成）

⚠️ 绝对规则：Deep Search 永不编造专利号、公司名或 CTQ 值。
   所有专利数据来自 patent_search.py 的返回值。
   LLM 仅用于对已检索专利文本的自然语言分析——
   绝不作为实际专利检索的替代。
"""
from __future__ import annotations

import concurrent.futures
import json
import os
import re
from openai import OpenAI
from pydantic import BaseModel, Field

from patent_search import (  # ← 关键：Deep Search 引擎，唯一数据源
    Patent,
    search_patentsview,
    search_google_patents,
    search_epo_ops,
    search_wipo_patentscope,
    search_cn_patents,
    search_by_strategies,
    fetch_patent_detail,
    _translate_keywords,
)


# -- CTQ 类型 -----------------------------------------------------------------

class CTQEntry(BaseModel):
    """从专利或产品 TDS 提取的单个 CTQ 数据点。"""
    parameter: str = Field(description="CTQ 名，如 '溶胀率', 'MVTR'")
    value: str = Field(description="测量值+单位，如 '<30% vol'")
    condition: str = Field(default="", description="测试条件")
    method: str = Field(default="", description="测试方法/标准")
    source: str = Field(description="[P] 专利 / [T] TDS / [A] 论文 / [C] 临床 / [D] 领域 / [E] 估算")


# -- 公司与路线类型 -----------------------------------------------------------

class DeepSearchCompany(BaseModel):
    """Deep Search 中发现的一家公司。"""
    name: str
    level: str = Field(default="P2", description="P0 / P1 / P2")
    patent_number: str = Field(default="")
    patent_status: str = Field(default="")
    product: str = Field(default="")
    tech_summary: str = Field(default="")
    ctq: dict[str, CTQEntry] = Field(default_factory=dict)
    fto_risk: str = Field(default="", description="none / medium / high / check")
    notes: str = Field(default="")


class DeepSearchRoute(BaseModel):
    """一条技术路线及其所有公司。"""
    name: str
    principle: str = Field(default="")
    company_count: int = 0
    companies: list[DeepSearchCompany] = Field(default_factory=list)


# -- FTO 与建议类型 -----------------------------------------------------------

class FTOItem(BaseModel):
    patent: str
    company: str
    expiry_est: str = Field(default="")
    note: str = Field(default="")


class FTOAssessment(BaseModel):
    high_risk: list[FTOItem] = Field(default_factory=list)
    medium_risk: list[FTOItem] = Field(default_factory=list)
    expired_free: list[FTOItem] = Field(default_factory=list)
    recommended_sweep_query: str = Field(default="")
    sweep_ipc: list[str] = Field(default_factory=list)
    avoidance_notes: list[str] = Field(default_factory=list)


class Recommendation(BaseModel):
    short_term: str = Field(default="")
    medium_term: str = Field(default="")
    long_term: str = Field(default="")


# -- 收敛追踪 -----------------------------------------------------------------

class ConvergenceStatus(BaseModel):
    converged: bool = False
    total_rounds: int = 1
    new_routes_this_round: int = 0
    new_companies_this_round: int = 0
    new_ipc_this_round: int = 0
    new_concepts_this_round: int = 0
    reason: str = Field(default="")


class NewTermsExtract(BaseModel):
    """一轮 Deep Search 后提取的新词。"""
    keywords: list[str] = Field(default_factory=list)
    company_names: list[str] = Field(default_factory=list)
    ipc_codes: list[str] = Field(default_factory=list)
    new_routes: list[str] = Field(default_factory=list, description="之前未见的技术路线")


# -- 完整管线类型 -------------------------------------------------------------

class DeepSearchInput(BaseModel):
    """输入：VOC Scout 产出的全部内容。"""
    voc: str
    domain_class: str = Field(default="")
    p0_companies: list[str] = Field(default_factory=list)
    p1_companies: list[str] = Field(default_factory=list)
    core_keywords: list[str] = Field(default_factory=list)
    supp_keywords: list[str] = Field(default_factory=list)
    exclude_keywords: list[str] = Field(default_factory=list)
    core_ipc: list[str] = Field(default_factory=list)
    supp_ipc: list[str] = Field(default_factory=list)
    fto_notes: list[str] = Field(default_factory=list)
    round_history: list[dict] = Field(default_factory=list)


class DeepSearchOutput(BaseModel):
    """Deep Search 完整输出——完整专利全景。"""
    voc: str
    domain_class: str = Field(default="")
    confidence: str = Field(default="★★☆")
    search_path: str = Field(default="")
    converged: bool = False
    total_rounds: int = 0
    total_companies_found: int = 0
    routes: list[DeepSearchRoute] = Field(default_factory=list)
    ctq_table: list[dict] = Field(default_factory=list)
    fto: FTOAssessment = Field(default_factory=FTOAssessment)
    recommendation: Recommendation = Field(default_factory=Recommendation)
    user_corrections: list[dict] = Field(default_factory=list)
    convergence: ConvergenceStatus = Field(default_factory=ConvergenceStatus)


# -- LLM 客户端（仅用于文本分析，绝不用于专利数据合成） -----------------------

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


# -- 专利检索包装器（用 patent_search.py，绝不 LLM 合成） ---------------------

def search_round_company(
    company_name: str,
    keywords: list[str] | None = None,
    ipc: str = "",
) -> list[Patent]:
    """用 patent_search.py 引擎为指定公司检索专利。

    本函数绝不编造或合成专利数据。它始终返回 patent_search.py 函数的真实
    专利记录。若所有引擎返回空，则返回空列表——不回退到 LLM 合成。

    Args:
        company_name: 受让人名，如 "Arkema" 或 "巴斯夫"
        keywords: 与公司名组合的搜索关键词
        ipc: 可选 IPC 分类以收窄搜索

    Returns:
        Patent 对象列表（可能为空）
    """
    if not keywords:
        keywords = []

    base_query = f'"{company_name}"'
    if ipc:
        base_query += f" AND {ipc}"
    if keywords:
        base_query += " AND " + " AND ".join(f'"{kw}"' for kw in keywords[:3])

    all_patents: list[Patent] = []
    seen_numbers: set[str] = set()

    engines = [
        ("google_patents", lambda: search_google_patents(base_query, num=20, country="US")),
        ("epo_ops", lambda: search_epo_ops(base_query, num=10)),
        ("wipo", lambda: search_wipo_patentscope(base_query, num=10)),
        ("patentsview", lambda: search_patentsview(base_query, num=10)),
        ("cn_patents", lambda: search_cn_patents(base_query, num=20)),
    ]

    for engine_name, engine_fn in engines:
        try:
            results = engine_fn()
            for p in results:
                if p.patent_number and p.patent_number not in seen_numbers:
                    seen_numbers.add(p.patent_number)
                    all_patents.append(p)
        except Exception as e:
            print(f"[deep_search] {engine_name} failed for '{company_name}': {e}")

    return all_patents


def fetch_patent_full_texts(patent_numbers: list[str]) -> dict[str, str]:
    """为一批专利号抓取全文。

    用 patent_search.fetch_patent_detail() 从 Google Patents / EPO / WIPO
    获取 Abstract + Claims + Description。
    """
    texts: dict[str, str] = {}
    for num in patent_numbers:
        try:
            detail = fetch_patent_detail(num, timeout=8.0)
            if detail:
                texts[num] = detail
        except Exception as e:
            print(f"[deep_search] fetch_patent_full_texts: {num} failed: {e}")
    return texts


# -- IPC 适配器（按搜索引擎归一化 IPC 格式） ----------------------------------

IPC_ADAPTER = {
    "google_patents": lambda ipc: f" IPC={ipc.replace(' ', '').replace('/', '')}",
    "epo_ops":        lambda ipc: f' ic = "{ipc}"',       # CQL 语法
    "wipo":           lambda ipc: f" IC/{ipc.replace(' ', '/')}",
    "patentsview":    lambda ipc: ipc,                    # 透传，事后过滤
    "cn_patents":     lambda ipc: f" IPC分类号={ipc}",
}


def append_ipc_to_query(query: str, ipc: str, engine: str) -> str:
    """用引擎专属语法把 IPC 分类附加到关键词查询。"""
    adapter = IPC_ADAPTER.get(engine)
    if adapter:
        return query + adapter(ipc)
    return query  # 未知引擎：跳过 IPC


# -- 去重逻辑 -----------------------------------------------------------------

def dedup_patents(patents: list) -> list:
    """按 patent_number 去重（大小写不敏感、去空格）。

    同族专利（如 US10717890B2 + CN108123456B）不合并，因为各国法律状态不同。
    它们留给 Reduce 阶段按公司归并 CTQ 值。
    """
    seen: set[str] = set()
    result = []
    for p in patents:
        key = (p.patent_number or "").strip().upper().replace(" ", "")
        if key and key not in seen:
            seen.add(key)
            result.append(p)
    return result


# -- 新词提取（LLM 用于已检索文本的结构化分析，非合成） -----------------------

EXTRACT_TERMS_SYSTEM = """You are an expert at extracting structured information from
patent and product search results.

Given a batch of search results (patent titles, abstracts, company names, product
descriptions), extract FOUR categories of new information:

1. NEW KEYWORDS — terms that appear frequently in results but were NOT in the
   original search keywords. These are technical terms the searcher doesn't know yet.
2. NEW COMPANY NAMES — patent assignees or product manufacturers that appear in the
   results but were NOT in the known company list.
3. NEW IPC CODES — International Patent Classification codes that appear in the
   results but were NOT in the known IPC list.
4. NEW TECH ROUTES — if the results reveal a fundamentally different technical
   approach that was NOT covered in the initial analysis.

For each extracted item, provide:
- The term/name/code
- How many times it appeared
- Which patent/document it comes from

Return ONLY valid JSON matching:
{
  "keywords": [{"term": "...", "count": 3, "from": "US2025XXXXX"}],
  "company_names": [{"name": "...", "count": 5, "from": "...", "country": "CN"}],
  "ipc_codes": [{"code": "C09J 7/10", "count": 4, "meaning": "..."}],
  "new_routes": [{"name": "...", "representative_patent": "...", "difference": "..."}]
}"""


def extract_new_terms(
    search_results_text: str,
    known_keywords: list[str] | None = None,
    known_companies: list[str] | None = None,
    known_ipc: list[str] | None = None,
) -> dict:
    """从搜索结果中提取新词，供下一轮迭代使用。

    Args:
        search_results_text: 搜索结果的标题/摘要拼接文本。
        known_keywords: 之前轮次已用关键词。
        known_companies: 已发现的公司。
        known_ipc: 已知 IPC。

    Returns:
        含 keys: keywords, company_names, ipc_codes, new_routes 的字典。
    """
    client = _get_llm_client()
    prompt = (
        f"Search results:\n{search_results_text[:16000]}\n\n"
        f"Known keywords: {known_keywords or []}\n"
        f"Known companies: {known_companies or []}\n"
        f"Known IPC: {known_ipc or []}"
    )
    resp = client.chat.completions.create(
        model=os.environ.get("DEEPSEEK_MODEL", "deepseek-v4-pro"),
        messages=[
            {"role": "system", "content": EXTRACT_TERMS_SYSTEM},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
        max_tokens=2048,
        response_format={"type": "json_object"},
        extra_body={"thinking": {"type": "disabled"}},
    )
    raw = resp.choices[0].message.content.strip()
    data = _parse_json_safe(raw)
    return data if data else {"keywords": [], "company_names": [], "ipc_codes": [], "new_routes": []}


# -- 收敛判断 -----------------------------------------------------------------

def judge_convergence(
    round_number: int,
    new_routes: int,
    new_companies: int,
    prev_new_companies: int,
    new_ipc: int,
    new_concepts: int,
) -> ConvergenceStatus:
    """判断 Deep Search 在本轮后是否收敛。

    量化阈值：
        new_companies / prev_new_companies < 30% → 收敛信号
        new_ipc == 0 → 收敛信号
        new_concepts < 3 → 收敛信号
        new_routes == 0 → 收敛信号（最重要）

    4 个信号中满足 3 个 → 收敛。

    Returns:
        含 converged 标志和原因的 ConvergenceStatus。
    """
    company_ratio = (new_companies / prev_new_companies) if prev_new_companies > 0 else 0.0
    signals = [
        new_routes == 0,
        company_ratio < 0.30,
        new_ipc == 0,
        new_concepts < 3,
    ]
    signal_count = sum(signals)
    converged = signal_count >= 3

    parts = [
        f"Round {round_number}",
        f"New routes: {new_routes} (surge? {new_routes > 0})",
        f"New companies: {new_companies} / prev {prev_new_companies} = {company_ratio:.0%}",
        f"New IPC: {new_ipc}",
        f"New concepts: {new_concepts}",
        f"Signals passed: {signal_count}/4 → {'CONVERGED' if converged else 'NOT CONVERGED'}",
    ]

    return ConvergenceStatus(
        converged=converged,
        total_rounds=round_number,
        new_routes_this_round=new_routes,
        new_companies_this_round=new_companies,
        new_ipc_this_round=new_ipc,
        new_concepts_this_round=new_concepts,
        reason=" | ".join(parts),
    )


# -- Map-Reduce 专利分析管线 --------------------------------------------------
# 3 轮迭代确认关键词+IPC 后，patent_search.py 引擎返回 50-100+ 专利号。
# 一次 LLM 调用读全部全文会溢出上下文（80 × 10K = 800K 字符）。
# Map-Reduce：每篇专利提取 CTQ 记录（~200 字符），再聚合。

CTQ_EXTRACT_SYSTEM = """You are a patent analysis expert. Given the full text of ONE patent,
extract all Critical-To-Quality (CTQ) parameters with NUMERICAL values.

For each CTQ parameter you find, record:
- name: parameter name (e.g. "溶胀率", "MVTR", "铅笔硬度")
- value: measured value with unit (e.g. "<30% vol", ">3000 g/m²/24h")
- condition: test conditions (temperature, time, solvent etc.)
- method: test method/standard if mentioned
- unit: the unit of measurement

Rules:
- ONLY extract parameters with NUMERICAL values. Skip purely qualitative claims.
- If the patent mentions multiple CTQ parameters, extract ALL of them.
- Each CTQ entry should be concise — the entire output MUST stay under 300 characters.
- Include the priority date and patent status if you can determine them.
- If no quantitative CTQ is found, return an empty 'ctq' array.
- Return ONLY valid JSON matching the schema — no markdown, no explanation.

Schema:
{
  "patent_number": "US...",
  "assignee": "...",
  "tech_route": "1-line technical approach",
  "priority_date": "YYYY-MM-DD or empty",
  "ctq": [
    {"name": "...", "value": "...", "condition": "...", "method": "...", "unit": "..."}
  ],
  "patent_status": "active/expired/pending/unknown",
  "expiry_est": "~YYYY or empty",
  "fto_flag": "check_claims/safe/expired/unknown",
  "notes": "any additional observations (keep short)"
}"""


def extract_ctq_single(patent_number: str, full_text: str) -> dict:
    """从单篇专利全文提取 CTQ。返回记录必须 ≤300 字符。

    Args:
        patent_number: 如 "US10717890B2"
        full_text: 来自 fetch_patent_detail() 的 Abstract + Claims + Description

    Returns:
        匹配 CTQ_EXTRACT_SYSTEM schema 的结构化 CTQ 记录（dict）。
    """
    text = (full_text or "").strip()
    if not text or len(text) < 50:
        return {
            "patent_number": patent_number,
            "assignee": "",
            "tech_route": "",
            "priority_date": "",
            "ctq": [],
            "patent_status": "unknown",
            "expiry_est": "",
            "fto_flag": "unknown",
            "notes": "No full text available",
        }

    client = _get_llm_client()
    resp = client.chat.completions.create(
        model=os.environ.get("DEEPSEEK_MODEL", "deepseek-v4-pro"),
        messages=[
            {"role": "system", "content": CTQ_EXTRACT_SYSTEM},
            {"role": "user", "content": f"Patent {patent_number}:\n{text[:12000]}"},
        ],
        temperature=0.1,
        max_tokens=512,
        response_format={"type": "json_object"},
        extra_body={"thinking": {"type": "disabled"}},
    )
    raw = resp.choices[0].message.content.strip()
    data = _parse_json_safe(raw)
    return data if data else {
        "patent_number": patent_number, "ctq": [],
        "patent_status": "unknown", "fto_flag": "unknown", "notes": "Parse failed",
    }


# -- 预筛（必须在抓全文前调用，否则成本翻倍） ---------------------------------

PRESCREEN_SYSTEM = """You are a patent screening expert. Given {N} patent snippets,
select the 30-50 most relevant patents worth reading in full text.

Selection criteria (in priority order):
1. Patent mentions QUANTITATIVE performance metrics (e.g. "<30% vol", ">3000 g/m²/24h")
2. Patent is from a market-leading company in this field
3. Prefer patents from 2000 onwards — older patents (especially expired ones) often
   contain foundational data and have ZERO FTO risk, making them highly valuable
4. EXCLUDE: pure method/equipment patents (no material/product composition parameters)
5. EXCLUDE: patents whose snippet contains zero numerical values

Return ONLY valid JSON: {"selected_patent_numbers": ["US...", "CN..."], "rationale": "1-liner"}"""


def prescreen_patents(
    patent_numbers: list[str],
    max_select: int = 50,
) -> list[str]:
    """按相关性排序专利，返回前 N 供全文阅读。"""
    if len(patent_numbers) <= max_select:
        return patent_numbers

    client = _get_llm_client()
    resp = client.chat.completions.create(
        model=os.environ.get("DEEPSEEK_MODEL", "deepseek-v4-pro"),
        messages=[
            {"role": "system", "content": PRESCREEN_SYSTEM},
            {"role": "user", "content": f"Patent numbers:\n{json.dumps(patent_numbers)}"},
        ],
        temperature=0.1,
        max_tokens=1024,
        response_format={"type": "json_object"},
        extra_body={"thinking": {"type": "disabled"}},
    )
    raw = resp.choices[0].message.content.strip()
    data = _parse_json_safe(raw) or {}
    return data.get("selected_patent_numbers", patent_numbers[:max_select])


# -- Map-Reduce 协调器（含容错） ----------------------------------------------

def run_map_reduce_pipeline(
    patent_numbers: list[str],
    max_patents: int = 50,
    parallel_workers: int = 10,
    on_progress: "Callable[[int, int, str, bool], None] | None" = None,
) -> dict:
    """运行完整 Map-Reduce：抓全文 → 提 CTQ → 聚合。含容错与统计。

    Map 阶段用 ThreadPoolExecutor 并发（默认 10 路），每篇专利独立抓全文
    并提取 CTQ 记录（~200 字符），避免单篇 10K 字符 × N 篇撑爆上下文。

    Reduce 阶段将全部 CTQ 记录（~10K 字符总计）送入一次 LLM 调用聚合成
    公司对比表。

    Args:
        patent_numbers: 来自 patent_search.py 搜索结果的专利号。
        max_patents: 处理专利上限（LLM 成本控制）。
        parallel_workers: 最大并发 LLM 调用（API 限流）。
        on_progress: 可选进度回调 (completed_count, total, patent_number, fetch_ok)。

    Returns:
        含 'ctq_records' (list)、'ctq_comparison_table' (list)、'stats' 的字典。
    """
    # Step 0: 预筛（必须在抓全文前）
    screened = prescreen_patents(patent_numbers, max_select=max_patents)
    print(f"[deep_search] Map-Reduce: prescreened {len(patent_numbers)} → {len(screened)} patents")

    # Step 1: Map — 并发抓全文 + 逐篇提 CTQ
    def _process_one(patent_number: str) -> dict:
        """处理单篇专利：抓全文 → 提 CTQ。失败返回空记录。

        _fetch_ok 标记全文抓取是否成功（独立于 CTQ 提取是否找到参数）。
        """
        try:
            full_text = fetch_patent_detail(patent_number, timeout=8.0)
            if full_text and len(full_text.strip()) > 50:
                record = extract_ctq_single(patent_number, full_text)
                record["_fetch_ok"] = True
                return record
            else:
                return {
                    "patent_number": patent_number,
                    "ctq": [],
                    "notes": "Empty/too-short full text",
                    "_fetch_ok": False,
                }
        except Exception as e:
            return {
                "patent_number": patent_number,
                "ctq": [],
                "notes": f"Fetch failed: {e}",
                "_fetch_ok": False,
            }

    ctq_records: list[dict] = []
    fetch_ok = 0
    fetch_fail = 0
    completed = 0

    # 按 parallel_workers 分批并发
    actual_workers = min(parallel_workers, len(screened), 16)
    with concurrent.futures.ThreadPoolExecutor(max_workers=actual_workers) as executor:
        future_map = {
            executor.submit(_process_one, num): num
            for num in screened
        }
        for future in concurrent.futures.as_completed(future_map):
            record = future.result()
            ctq_records.append(record)
            completed += 1
            # _fetch_ok tracks whether patent full-text was successfully fetched
            # (independent of whether CTQ parameters were found in the text)
            patent_number = record.get("patent_number", "")
            if record.pop("_fetch_ok", False):
                fetch_ok += 1
                if on_progress:
                    on_progress(completed, len(screened), patent_number, True)
            else:
                fetch_fail += 1
                if on_progress:
                    on_progress(completed, len(screened), patent_number, False)

    total = fetch_ok + fetch_fail
    success_rate = fetch_ok / total if total > 0 else 0

    # 容错检查
    if success_rate < 0.60:
        return {
            "error": f"Fetch success rate too low ({success_rate:.0%}), please retry",
            "ctq_records": ctq_records,
            "stats": {
                "total_requested": len(screened),
                "fetch_ok": fetch_ok,
                "fetch_fail": fetch_fail,
                "ctq_extracted": sum(1 for r in ctq_records if r.get("ctq")),
                "ctq_empty": sum(1 for r in ctq_records if not r.get("ctq")),
                "rate": f"{success_rate:.0%}",
            },
        }

    # Step 2: Reduce — 按公司归并，挑最佳 CTQ 值
    reduce_input = json.dumps(ctq_records, ensure_ascii=False)
    reduce_prompt = (
        "Below are CTQ records from multiple patents.\n"
        "1. Group by assignee (company). Same-family patents from different\n"
        "   countries should be recognized as same company, pick best CTQ value.\n"
        "2. For each CTQ parameter, pick the BEST value across all patents for that company.\n"
        "3. Sort companies by: commercialization status → CTQ performance.\n"
        "4. Return JSON: {'companies': [{...}], 'notes': [...]}"
    )
    client = _get_llm_client()
    resp = client.chat.completions.create(
        model=os.environ.get("DEEPSEEK_MODEL", "deepseek-v4-pro"),
        messages=[
            {"role": "system", "content": "You are a patent analyst. Output valid JSON only."},
            {"role": "user", "content": f"{reduce_input[:16000]}\n\n{reduce_prompt}"},
        ],
        temperature=0.2,
        max_tokens=4096,
        response_format={"type": "json_object"},
        extra_body={"thinking": {"type": "disabled"}},
    )
    raw = resp.choices[0].message.content.strip()
    comparison = _parse_json_safe(raw) or {}

    rate_label = "✅" if success_rate > 0.80 else "⚠️" if success_rate >= 0.60 else "❌"

    return {
        "ctq_records": ctq_records,
        "ctq_comparison_table": comparison.get("companies", []),
        "stats": {
            "total_requested": len(screened),
            "fetch_ok": fetch_ok,
            "fetch_fail": fetch_fail,
            "ctq_extracted": sum(1 for r in ctq_records if r.get("ctq")),
            "ctq_empty": sum(1 for r in ctq_records if not r.get("ctq")),
            "fetch_success_rate": f"{rate_label} {success_rate:.0%}",
        },
        "notes": comparison.get("notes", []),
    }


# -- 完整 Deep Search 三轮迭代管线 ------------------------------------------------

def run_deep_search_pipeline(inp: DeepSearchInput) -> dict:
    """运行完整的三轮迭代 Deep Search 管线。

    使用 patent_search.py 引擎（永不通过 LLM 合成专利数据）。

    Round 1: P0/P1 公司定向搜索 + 核心关键词/IPC 宽搜
    Round 2: 新词提取 → 用新关键词/公司/IPC 重搜
    Round 3: 收敛验证 → 若未收敛再做一轮 → 终判

    返回包含 all_patent_numbers、convergence、search_path 等字段的 dict，
    供 DeepSearchOutput 组装和后续 Map-Reduce 消费。

    Args:
        inp: VOC Scout 产出的 DeepSearchInput（公司、关键词、IPC、FTO 备注等）

    Returns:
        含 keys: all_patent_numbers, search_path, converged, total_rounds,
        total_companies_found, convergence, fto, recommendation 的 dict。
    """
    from patent_search import search_google_patents

    all_patents: list[Patent] = []
    known_companies = set(inp.p0_companies + inp.p1_companies)
    known_ipc = set(inp.core_ipc + inp.supp_ipc)
    search_path_parts: list[str] = []
    total_rounds = 0

    # 翻译中文关键词 → 英文（Google Patents 用英文索引，中文搜不到）
    raw_core_kw = inp.core_keywords
    raw_supp_kw = inp.supp_keywords
    en_core_kw = [_translate_keywords(kw) for kw in raw_core_kw]
    en_supp_kw = [_translate_keywords(kw) for kw in raw_supp_kw]
    # 去重合并：英文翻译 + 中文原文（备用）
    known_keywords = set(raw_core_kw + raw_supp_kw + en_core_kw + en_supp_kw)
    # 优先用英文翻译作为搜索关键词，翻译失败的保留中文原文走 WIPO/CN 备用
    search_core_kw = [kw for kw in en_core_kw if kw and kw != raw_core_kw[en_core_kw.index(kw)]] if len(en_core_kw) == len(raw_core_kw) else en_core_kw
    # 简化：取翻译后的关键词，长度异常的（翻译失败回退中文）保留原文
    final_core_kw: list[str] = []
    for i, en_kw in enumerate(en_core_kw):
        orig = raw_core_kw[i] if i < len(raw_core_kw) else ""
        if en_kw and en_kw != orig:  # 翻译成功
            final_core_kw.append(en_kw)
        else:  # 翻译失败，保留原文
            final_core_kw.append(orig)
    final_supp_kw: list[str] = []
    for i, en_kw in enumerate(en_supp_kw):
        orig = raw_supp_kw[i] if i < len(raw_supp_kw) else ""
        if en_kw and en_kw != orig:
            final_supp_kw.append(en_kw)
        else:
            final_supp_kw.append(orig)
    print(f"[deep_search] Keywords translated: core {raw_core_kw} → {final_core_kw}, supp {raw_supp_kw} → {final_supp_kw}")

    # --- Round 1: 初始宽搜 -------------------------------------------------
    total_rounds += 1
    search_path_parts.append("R1(initial company + keyword scan)")
    r1_new: list[Patent] = []

    # 1a: P0 公司定向搜索（用英文翻译后的关键词）
    for company in inp.p0_companies:
        try:
            patents = search_round_company(company, final_core_kw)
            r1_new.extend(patents)
        except Exception as e:
            print(f"[deep_search] R1 company search failed for '{company}': {e}")

    # 1b: P1 公司定向搜索
    for company in inp.p1_companies:
        try:
            patents = search_round_company(company, final_core_kw[:2])
            r1_new.extend(patents)
        except Exception as e:
            print(f"[deep_search] R1 company search failed for '{company}': {e}")

    # 1c: 核心关键词 + IPC 宽搜（不限公司，用英文关键词）
    for kw in final_core_kw[:3]:
        try:
            q = kw
            if inp.core_ipc:
                q += " " + " ".join(inp.core_ipc[:2])
            patents = search_google_patents(q, num=10, country="US")
            r1_new.extend(patents)
        except Exception as e:
            print(f"[deep_search] R1 keyword search failed for '{kw}': {e}")

    # 1d: 补充关键词搜索
    for kw in final_supp_kw[:4]:
        try:
            q = kw
            if inp.supp_ipc:
                q += " " + " ".join(inp.supp_ipc[:2])
            patents = search_google_patents(q, num=8, country="US")
            r1_new.extend(patents)
        except Exception as e:
            print(f"[deep_search] R1 supp keyword search failed for '{kw}': {e}")

    r1_new = dedup_patents(r1_new)
    all_patents = r1_new
    r1_company_count = len(set(p.assignee for p in r1_new if p.assignee))
    print(f"[deep_search] R1 done: {len(r1_new)} unique patents, ~{r1_company_count} companies")

    # --- Round 2: 新词提取 + 重搜 ------------------------------------------
    total_rounds += 1
    search_path_parts.append("R2(new term extraction + re-search)")

    # 拼接 R1 结果文本供 LLM 提取新词
    r1_text_parts: list[str] = []
    for p in r1_new[:60]:
        line = f"{p.patent_number or ''} | {p.title or ''} | {p.assignee or ''} | {p.snippet[:200] if p.snippet else ''}"
        r1_text_parts.append(line)
    r1_text = "\n".join(r1_text_parts)

    r1_new_terms = extract_new_terms(
        r1_text,
        known_keywords=list(known_keywords),
        known_companies=list(known_companies),
        known_ipc=list(known_ipc),
    )

    r2_new: list[Patent] = []

    # 2a: 用新关键词搜
    new_kw_items = r1_new_terms.get("keywords", [])
    for nk in new_kw_items[:4]:
        term = nk if isinstance(nk, str) else nk.get("term", "")
        if term and term not in known_keywords:
            try:
                patents = search_google_patents(term, num=10, country="US")
                r2_new.extend(patents)
                known_keywords.add(term)
            except Exception as e:
                print(f"[deep_search] R2 new keyword search failed for '{term}': {e}")

    # 2b: 用新公司搜
    new_co_items = r1_new_terms.get("company_names", [])
    for nc in new_co_items[:4]:
        name = nc if isinstance(nc, str) else nc.get("name", "")
        if name and name not in known_companies:
            try:
                patents = search_round_company(name, final_core_kw[:2])
                r2_new.extend(patents)
                known_companies.add(name)
            except Exception as e:
                print(f"[deep_search] R2 new company search failed for '{name}': {e}")

    # 2c: 用新 IPC 搜
    new_ipc_items = r1_new_terms.get("ipc_codes", [])
    for ni in new_ipc_items[:3]:
        code = ni if isinstance(ni, str) else ni.get("code", "")
        if code and code not in known_ipc:
            try:
                q = " ".join(inp.core_keywords[:2]) if inp.core_keywords else inp.voc[:80]
                patents = search_google_patents(q + " " + code, num=10, country="US")
                r2_new.extend(patents)
                known_ipc.add(code)
            except Exception as e:
                print(f"[deep_search] R2 new IPC search failed for '{code}': {e}")

    r2_new = dedup_patents(r2_new)
    # 去重后合并（R2 中可能有一部分与 R1 重叠）
    all_numbers_before = {p.patent_number for p in all_patents if p.patent_number}
    r2_truly_new = [p for p in r2_new if p.patent_number not in all_numbers_before]
    all_patents = dedup_patents(all_patents + r2_truly_new)

    r2_new_companies = len(set(p.assignee for p in r2_truly_new if p.assignee))
    r2_new_routes = len(r1_new_terms.get("new_routes", []))
    r2_new_ipc = len(new_ipc_items)
    r2_new_concepts = len(new_kw_items)
    print(f"[deep_search] R2 done: {len(r2_truly_new)} new patents, {r2_new_companies} new companies")

    # --- Round 3: 收敛验证 + 必要时终搜 -------------------------------------
    total_rounds += 1
    prev_new_companies = r1_company_count  # R1 公司数作为基线

    status = judge_convergence(
        round_number=3,
        new_routes=r2_new_routes,
        new_companies=r2_new_companies,
        prev_new_companies=prev_new_companies if prev_new_companies > 0 else 1,
        new_ipc=r2_new_ipc,
        new_concepts=r2_new_concepts,
    )

    r3_new: list[Patent] = []
    if not status.converged:
        search_path_parts.append("R3(not converged — final sweep)")
        # 拼 R2 文本，再提新词
        r2_text_parts = []
        for p in r2_truly_new[:40]:
            line = f"{p.patent_number or ''} | {p.title or ''} | {p.assignee or ''} | {p.snippet[:200] if p.snippet else ''}"
            r2_text_parts.append(line)
        r2_text = "\n".join(r2_text_parts)

        r2_new_terms = extract_new_terms(
            r2_text,
            known_keywords=list(known_keywords),
            known_companies=list(known_companies),
            known_ipc=list(known_ipc),
        )

        # 最后一轮搜新词
        for nk in r2_new_terms.get("keywords", [])[:2]:
            term = nk if isinstance(nk, str) else nk.get("term", "")
            if term and term not in known_keywords:
                try:
                    patents = search_google_patents(term, num=8, country="US")
                    r3_new.extend(patents)
                    known_keywords.add(term)
                except Exception as e:
                    print(f"[deep_search] R3 keyword search failed for '{term}': {e}")

        r3_new = dedup_patents(r3_new)
        all_numbers_before = {p.patent_number for p in all_patents if p.patent_number}
        r3_truly_new = [p for p in r3_new if p.patent_number not in all_numbers_before]
        all_patents = dedup_patents(all_patents + r3_truly_new)

        r3_new_companies = len(set(p.assignee for p in r3_truly_new if p.assignee))
        r3_new_ipc = len(r2_new_terms.get("ipc_codes", []))
        r3_new_concepts = len(r2_new_terms.get("keywords", []))

        status = judge_convergence(
            round_number=3,
            new_routes=len(r2_new_terms.get("new_routes", [])),
            new_companies=r3_new_companies,
            prev_new_companies=r2_new_companies if r2_new_companies > 0 else 1,
            new_ipc=r3_new_ipc,
            new_concepts=r3_new_concepts,
        )
    else:
        search_path_parts.append("R3(converged — verified)")

    all_patent_numbers = [p.patent_number for p in all_patents if p.patent_number]
    total_found = len(all_patent_numbers)
    total_companies = len(set(p.assignee for p in all_patents if p.assignee))

    # --- 自动上限：专利太多时预筛到 Top N，无需用户手动选数量 ----------
    # Map-Reduce 最佳处理量 ≈ 50 篇（LLM 成本 + 上下文限制）
    # >100 篇 → 展示 Top 100，MR 处理 Top 50
    # 50-100 篇 → 全部展示，MR 处理 Top 50
    # ≤50 篇 → 全部展示，全部 MR 处理
    MAP_REDUCE_CAP = 50
    DISPLAY_CAP = 100

    capped_for_mr: list[str] = []
    cap_note = ""
    if total_found <= MAP_REDUCE_CAP:
        capped_for_mr = all_patent_numbers
        cap_note = f"全部 {total_found} 篇专利均可用于分析"
    elif total_found <= DISPLAY_CAP:
        capped_for_mr = prescreen_patents(all_patent_numbers, max_select=MAP_REDUCE_CAP)
        cap_note = f"共 {total_found} 篇相关专利，自动筛取最相关 Top {len(capped_for_mr)} 篇用于 CTQ 提取"
    else:
        capped_for_mr = prescreen_patents(all_patent_numbers, max_select=MAP_REDUCE_CAP)
        cap_note = f"共 {total_found} 篇相关专利（>100），自动预筛到 Top {MAP_REDUCE_CAP} 篇用于 CTQ 提取。展示 Top {DISPLAY_CAP} 篇"

    display_patents = all_patents[:DISPLAY_CAP]
    print(f"[deep_search] Auto-cap: {total_found} found → {len(capped_for_mr)} for Map-Reduce, {len(display_patents)} for display")

    # --- 构建 FTO 风险评估 --------------------------------------------------
    fto = _build_fto_assessment(all_patents, inp)

    # --- 构建建议 -----------------------------------------------------------
    recommendation = _build_recommendation(inp, status, all_patents)

    return {
        "all_patent_numbers": all_patent_numbers,
        "capped_patent_numbers": capped_for_mr,
        "cap_note": cap_note,
        "all_patents": [p.to_dict() for p in display_patents],
        "total_found": total_found,
        "capped_to": len(capped_for_mr),
        "total_companies_found": total_companies,
        "search_path": " → ".join(search_path_parts),
        "converged": status.converged,
        "total_rounds": total_rounds,
        "convergence": status.model_dump(),
        "fto": fto.model_dump(),
        "recommendation": recommendation.model_dump(),
        "new_terms_round2": r1_new_terms if total_rounds >= 2 else {},
    }


def _build_fto_assessment(all_patents: list[Patent], inp: DeepSearchInput) -> FTOAssessment:
    """从专利列表 + FTO 备注构建 FTO 风险评估。

    通过 publication_date 估算过期状态（>20 年 ≈ 过期），
    结合 P0 公司匹配度分级风险。
    """
    import datetime
    high_risk: list[FTOItem] = []
    medium_risk: list[FTOItem] = []
    expired_free: list[FTOItem] = []
    current_year = datetime.datetime.now().year

    for p in all_patents:
        # 尝试从 publication_date 提取年份估算过期
        pub_year = 0
        if p.publication_date:
            try:
                pub_year = int(p.publication_date[:4])
            except (ValueError, IndexError):
                pub_year = 0

        # 20 年专利有效期粗略估算
        likely_expired = pub_year > 0 and (current_year - pub_year) > 20

        # 也检查标题/摘要中是否有过期暗示
        combined_text = f"{p.title or ''} {p.snippet or ''}".lower()
        expired_hint = any(kw in combined_text for kw in ["expired", "abandoned", "lapsed"])

        item = FTOItem(
            patent=p.patent_number or "",
            company=p.assignee or "",
            expiry_est=f"~{pub_year + 20}" if pub_year > 0 else "",
            note="Likely expired (>20yr)" if likely_expired else "",
        )

        if likely_expired or expired_hint:
            expired_free.append(item)
        elif inp.p0_companies and any(
            c.lower() in (p.assignee or "").lower() for c in inp.p0_companies
        ):
            high_risk.append(item)
        else:
            medium_risk.append(item)

    return FTOAssessment(
        high_risk=high_risk[:8],
        medium_risk=medium_risk[:12],
        expired_free=expired_free[:8],
        recommended_sweep_query=" AND ".join(inp.core_keywords[:3]) if inp.core_keywords else "",
        sweep_ipc=inp.core_ipc[:5],
        avoidance_notes=inp.fto_notes[:5],
    )


def _build_recommendation(
    inp: DeepSearchInput,
    status: ConvergenceStatus,
    all_patents: list[Patent],
) -> Recommendation:
    """基于收敛状态和检索结果构建短/中/长期建议。"""
    company_count = len(set(p.assignee for p in all_patents if p.assignee))
    patent_count = len(all_patents)

    short = ""
    medium = ""
    long = ""

    if status.converged:
        short = (
            f"专利全景已收敛，共找到 {company_count} 家相关公司、{patent_count} 篇专利。"
            "建议对 P0 公司活跃专利逐篇做 FTO 分析；对已过期专利直接使用。"
        )
        medium = "针对 Map-Reduce 产出的 CTQ 对比表中的前 3 名公司，收集产品 TDS 与白皮书补充验证。"
        long = "持续监控该领域新公开的专利申请，每季度更新一次全景。"
    else:
        short = (
            f"专利全景经过 {status.total_rounds} 轮搜索仍未完全收敛（{status.reason}）。"
            "建议先针对已发现的 {company_count} 家公司做局部决策，后续继续补充搜索。"
        )
        medium = "对已知盲区（新 IPC 分类、非英文专利）进行一次补搜。"
        long = "待收敛后，建立该领域的专利监控仪表板。"

    return Recommendation(short_term=short, medium_term=medium, long_term=long)
