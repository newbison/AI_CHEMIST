"""专利检索模块 — 适应网络受限环境。

数据源优先级：
1. USPTO PatentsView API（官方 US 专利 API）— 若网络可达
2. Google Patents xhr/query — 若网络可达
3. LLM 生成（DeepSeek 基于训练知识生成候选专利）— 网络受限时的主路径
4. 中国专利回退

每个专利返回统一结构：
{
    "patent_number": str,
    "title": str,
    "assignee": str,
    "snippet": str,
    "publication_date": str,
    "source": str,
    "url": str,
    "country": str,
}
"""
from __future__ import annotations

import json
import os
import re
import urllib.parse
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable

import httpx

BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
}


@dataclass
class Patent:
    patent_number: str
    title: str
    assignee: str
    snippet: str
    publication_date: str
    source: str
    url: str
    country: str

    def to_dict(self) -> dict:
        return asdict(self)


# ---------------------------------------------------------------------------
# 0. 本地真实专利缓存（agent 侧联网检索后落地，供网络受限环境使用）
# ---------------------------------------------------------------------------

_LOCAL_CACHE_PATH = Path(__file__).resolve().parent / "local_patents.json"


def search_local_cache(keywords: str) -> list[Patent]:
    """读取本地真实专利缓存。

    本机防火墙仅放行 DeepSeek，所有专利站点(Google Patents/xjishu/jigao616)
    均不可达。为避免回退到 LLM 编造专利(source=llm_generated)，由 agent 侧
    联网检索真实专利后写入 local_patents.json，本函数读取并按关键词粗筛。
    每条专利都带可追溯的 source_url 与 retrieved_date。
    """
    if not _LOCAL_CACHE_PATH.exists():
        return []
    try:
        with open(_LOCAL_CACHE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"[local_cache] 读取失败: {e}")
        return []

    cache_kws = [k.lower() for k in data.get("cache_keywords", [])]
    q = (keywords or "").lower()
    # 命中任一缓存关键词即返回该缓存集；无关键词时也返回（兜底）
    matched = any(k and k in q for k in cache_kws) if q else True
    if not matched:
        return []

    patents: list[Patent] = []
    for item in data.get("patents", []):
        num = item.get("patent_number", "")
        if not num:
            continue
        patents.append(Patent(
            patent_number=num,
            title=item.get("title", "").strip(),
            assignee=item.get("assignee", "").strip(),
            snippet=item.get("snippet", "").strip(),
            publication_date=item.get("publication_date", ""),
            source="local_cache",
            url=item.get("source_url", ""),
            country=item.get("country", "CN"),
        ))
    return patents


# ---------------------------------------------------------------------------
# 0b. 关键词翻译 — 中文→英文，提升 Google Patents 命中率
# ---------------------------------------------------------------------------

_HAS_CHINESE_RE = re.compile(r"[一-鿿]")


def _needs_translation(keywords: str) -> bool:
    """检测关键词中是否包含中文字符。"""
    return bool(_HAS_CHINESE_RE.search(keywords))


def _translate_keywords(keywords: str) -> str:
    """用 DeepSeek 将中文关键词翻译成英文（用于 Google Patents 搜索）。

    返回翻译后的英文关键词，如翻译失败则原样返回。
    """
    if not _needs_translation(keywords):
        return keywords
    api_key = os.environ.get("DEEPSEEK_API_KEY", "")
    if not api_key:
        return keywords
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        prompt = (
            "Translate the following Chinese keywords into an English search query "
            "for patent searching (keep key technical terms in English, add synonyms).\n"
            f"Chinese: {keywords}\n"
            "English:"
        )
        resp = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            max_tokens=256,
        )
        translated = resp.choices[0].message.content.strip()
        if translated and _needs_translation(translated):
            # 翻译后仍是中文则丢弃
            return keywords
        return translated or keywords
    except Exception as e:
        print(f"[translate] 翻译失败: {e}")
        return keywords


# ---------------------------------------------------------------------------
# 1. USPTO PatentsView API（若可达）
# ---------------------------------------------------------------------------

def search_patentsview(
    keywords: str, *, num: int = 20, timeout: float = 15.0
) -> list[Patent]:
    """从 USPTO PatentsView API 检索美国专利。"""
    url = "https://api.patentsview.org/patents/query"
    params = {
        "q": json.dumps({"_text": keywords}),
        "f": json.dumps([
            "patent_number", "patent_title", "patent_date",
            "assignee_organization", "patent_abstract",
        ]),
        "o": json.dumps({"per_page": min(num, 50), "page": 1}),
    }
    try:
        with httpx.Client(headers=BROWSER_HEADERS, timeout=timeout) as client:
            resp = client.get(url, params=params, follow_redirects=True)
            resp.raise_for_status()
            data = resp.json()
    except Exception as e:
        print(f"[patentsview] 检索失败: {e}")
        return []

    patents: list[Patent] = []
    try:
        for item in data.get("patents", []):
            num_raw = item.get("patent_number", "")
            assignees = item.get("assignees", [])
            assignee = assignees[0].get("assignee_organization", "") if assignees else ""
            abstract = item.get("patent_abstract", "") or ""
            patents.append(Patent(
                patent_number=num_raw,
                title=item.get("patent_title", "").strip(),
                assignee=assignee.strip(),
                snippet=abstract[:300].strip(),
                publication_date=item.get("patent_date", ""),
                source="uspto_patentsview",
                url=f"https://patents.google.com/patent/US{num_raw}/en" if num_raw else "",
                country="US",
            ))
    except (KeyError, TypeError) as e:
        print(f"[patentsview] 解析失败: {e}")
    return patents


# ---------------------------------------------------------------------------
# 2. Google Patents xhr/query（若可达）
# ---------------------------------------------------------------------------

def search_google_patents(
    keywords: str, *, num: int = 20, country: str = "US", timeout: float = 12.0,
    max_retries: int = 0,
) -> list[Patent]:
    """从 Google Patents xhr/query 端点检索。

    503 限流时不重试（Google Patents 限流至少持续几分钟，几秒内重试无意义）。
    调用方应通过角度间间隔预防限流，而非靠重试。
    """
    query_str = f"q={urllib.parse.quote(keywords)}"
    if country:
        query_str += f"&country={country}"
    query_str += "&language=ENGLISH"
    url = "https://patents.google.com/xhr/query"
    params = {"url": query_str, "exp": "", "num": str(num)}
    try:
        with httpx.Client(
            headers={**BROWSER_HEADERS, "Referer": "https://patents.google.com/"},
            timeout=timeout,
        ) as client:
            resp = client.get(url, params=params)
            if resp.status_code == 503:
                print(f"[google_patents] 503 限流（不重试，限流通常持续数分钟）")
                return []
            resp.raise_for_status()
            data = resp.json()
    except Exception as e:
        print(f"[google_patents] 检索失败: {e}")
        return []

    patents: list[Patent] = []
    try:
        cluster = data.get("results", {}).get("cluster", [])
        if not cluster:
            return []
        for item in cluster[0].get("result", []):
            pat = item.get("patent", {})
            num_raw = pat.get("publication_number", "")
            patents.append(Patent(
                patent_number=num_raw,
                title=pat.get("title", "").strip(),
                assignee=pat.get("assignee", "").strip(),
                snippet=pat.get("snippet", "").strip(),
                publication_date=pat.get("publication_date", ""),
                source="google_patents",
                url=f"https://patents.google.com/patent/{num_raw}/en" if num_raw else "",
                country=num_raw[:2] if len(num_raw) >= 2 else "",
            ))
    except (KeyError, IndexError, TypeError) as e:
        print(f"[google_patents] 解析失败: {e}")
    return patents


# ---------------------------------------------------------------------------
# 3. LLM 生成候选专利（网络受限时的主路径）
# ---------------------------------------------------------------------------

def search_via_llm(keywords: str, *, num: int = 15) -> list[Patent]:
    """用 DeepSeek 基于训练知识生成相关专利列表。

    LLM 会返回 JSON 格式的专利列表。注意：LLM 生成的专利号可能不完全准确，
    需要后续验证。source 标记为 "llm_generated"。
    """
    import os
    from openai import OpenAI

    api_key = os.environ.get("DEEPSEEK_API_KEY", "")
    if not api_key:
        print("[llm_search] 无 DEEPSEEK_API_KEY，跳过")
        return []

    try:
        base_url = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        client = OpenAI(api_key=api_key, base_url=base_url)
        prompt = f"""你是专利检索专家。根据以下技术关键词，列出 {num} 个最相关的真实专利。

关键词: {keywords}

要求：
1. **优先美国专利（US开头）和日本专利（JP开头）**，其次中国专利（CN开头）
2. 优先列出国际大公司的专利（如 Nitto Denko/日东电工、Tesa/德莎、3M、Soken Chemical/综研化学、Lintec/琳得科、Zeon/瑞翁、DuPont/杜邦等）
3. 每个专利必须包含：patent_number, title, assignee, abstract, publication_date, country
4. 只返回你确信存在的真实专利，不要编造
5. 返回 JSON 数组格式，不要其他文字

示例格式:
[
  {{"patent_number": "US11685841B2", "title": "Pressure-sensitive adhesive tape for battery", "assignee": "Nitto Denko Corporation", "abstract": "A pressure-sensitive adhesive tape for a battery...", "publication_date": "2023-06-20", "country": "US"}}
]"""

        resp = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=4096,
        )
        text = resp.choices[0].message.content.strip()

        # 提取 JSON 数组
        json_match = re.search(r'\[.*\]', text, re.DOTALL)
        if not json_match:
            print("[llm_search] 未找到 JSON 数组")
            return []

        items = json.loads(json_match.group())
        patents: list[Patent] = []
        for item in items[:num]:
            num_raw = item.get("patent_number", "")
            patents.append(Patent(
                patent_number=num_raw,
                title=item.get("title", "").strip(),
                assignee=item.get("assignee", "").strip(),
                snippet=item.get("abstract", "")[:300].strip(),
                publication_date=item.get("publication_date", ""),
                source="llm_generated",
                url=f"https://patents.google.com/patent/{num_raw}/en" if num_raw else "",
                country=item.get("country", num_raw[:2] if len(num_raw) >= 2 else ""),
            ))
        return patents
    except Exception as e:
        print(f"[llm_search] 失败: {e}")
        return []


# ---------------------------------------------------------------------------
# 4. 中国专利回退
# ---------------------------------------------------------------------------

def search_cn_patents(keywords: str, *, num: int = 20, timeout: float = 12.0) -> list[Patent]:
    """中国专利回退：Google Patents 全球检索后过滤 CN。"""
    all_pats = search_google_patents(keywords, num=num * 2, country="", timeout=timeout)
    return [p for p in all_pats if p.country == "CN"][:num]


# ---------------------------------------------------------------------------
# 5. 专利详情抓取
# ---------------------------------------------------------------------------

def fetch_patent_detail(patent_number: str, *, timeout: float = 12.0) -> str:
    """抓取单篇专利的全文文本。尝试 Google Patents 单篇页。"""
    num_clean = patent_number.strip()
    url = f"https://patents.google.com/patent/{num_clean}/en"
    try:
        with httpx.Client(
            headers={**BROWSER_HEADERS, "Referer": "https://patents.google.com/"},
            timeout=timeout,
        ) as client:
            resp = client.get(url)
            resp.raise_for_status()
            html = resp.text
    except Exception as e:
        print(f"[detail] 抓取 {num_clean} 失败: {e}")
        return ""

    text_parts: list[str] = []
    desc = re.search(r'<meta name="description" content="([^"]+)"', html, re.IGNORECASE)
    if desc:
        text_parts.append(f"[Abstract] {desc.group(1)}")

    claims = re.search(
        r'<section[^>]*itemprop="claims"[^>]*>(.*?)</section>',
        html, re.IGNORECASE | re.DOTALL,
    )
    if claims:
        claims_text = re.sub(r"<[^>]+>", " ", claims.group(1))
        claims_text = re.sub(r"\s+", " ", claims_text).strip()
        text_parts.append(f"[Claims] {claims_text[:3000]}")

    desc2 = re.search(
        r'<section[^>]*itemprop="description"[^>]*>(.*?)</section>',
        html, re.IGNORECASE | re.DOTALL,
    )
    if desc2:
        desc_text = re.sub(r"<[^>]+>", " ", desc2.group(1))
        desc_text = re.sub(r"\s+", " ", desc_text).strip()
        text_parts.append(f"[Description] {desc_text[:5000]}")

    return "\n\n".join(text_parts)


# ---------------------------------------------------------------------------
# 6. 统一入口：多级回退
# ---------------------------------------------------------------------------

def search_patents_with_fallback(
    keywords: str, *, num: int = 20, prefer_us: bool = True
) -> list[Patent]:
    """多级回退检索。

    普通场景（网络可达）：
      1. USPTO PatentsView（US 专利）— 若 >= 5 条返回
      2. Google Patents（US 优先，扩全球）— 若 >= 5 条返回
         如果关键词含中文且 Google 返回 < 5 条，自动翻译成英文重试
      3. 中国专利 — Google Patents 全球结果中过滤 CN
      4. LLM 生成（DeepSeek 训练知识）— 默认关闭，需 PATENTS_ALLOW_LLM_FALLBACK=1

    网络完全受限时的保底（如所有外部 API 均不通）：
      5. 本地真实专利缓存 — 纯保底，仅在以上全失败时启用
    """
    us_pats: list[Patent] = []
    gp_us: list[Patent] = []
    gp_global: list[Patent] = []
    llm_pats: list[Patent] = []

    # 第一级：USPTO PatentsView
    if prefer_us:
        us_pats = search_patentsview(keywords, num=num)
        if len(us_pats) >= 5:
            return us_pats[:num]

    # 第二级：Google Patents 先用原始关键词
    gp_us = search_google_patents(keywords, num=num, country="US")
    if len(gp_us) >= 5:
        return gp_us[:num]

    # 如果原始关键词含中文且 Google 返回不足，自动翻译成英文重试
    if _HAS_CHINESE_RE.search(keywords):
        en_kw = _translate_keywords(keywords)
        if en_kw and en_kw != keywords:
            print(f"[fallback] 中文关键词返回不足，尝试英文翻译: \"{en_kw}\"")
            gp_us_en = search_google_patents(en_kw, num=num, country="US")
            if len(gp_us_en) >= 5:
                return gp_us_en[:num]
            gp_global_en = search_google_patents(en_kw, num=num, country="")
            if len(gp_global_en) >= 5:
                return gp_global_en[:num]

    gp_global = search_google_patents(keywords, num=num, country="")
    if len(gp_global) >= 5:
        return gp_global[:num]

    # 第三级：中国专利（Google Patents 全球中过滤 CN）
    cn_pats = search_cn_patents(keywords, num=num)
    if cn_pats:
        return cn_pats[:num]

    # 第四级：LLM 生成 —— 默认关闭，防止编造专利。
    # 仅当显式设置 PATENTS_ALLOW_LLM_FALLBACK=1 时启用。
    if os.environ.get("PATENTS_ALLOW_LLM_FALLBACK", "0") == "1":
        llm_pats = search_via_llm(keywords, num=num)
        if len(llm_pats) >= 5:
            return llm_pats[:num]

    # 第五级：本地真实专利缓存（纯保底，仅在前四级全失败时启用）
    local_pats = search_local_cache(keywords)
    if local_pats:
        return local_pats[:num]

    # 全失败：合并已有的
    seen: set[str] = set()
    merged: list[Patent] = []
    for p in us_pats + gp_us + gp_global + llm_pats:
        if p.patent_number and p.patent_number not in seen:
            seen.add(p.patent_number)
            merged.append(p)
    return merged[:num]


# ---------------------------------------------------------------------------
# 7. 多策略搜索合并（VOC 拆解后逐角度搜索，合并去重）
# ---------------------------------------------------------------------------

def search_by_strategies(
    strategies: list[dict], *, num_per_angle: int = 8, total: int = 20
) -> list[Patent]:
    """对每个搜索策略分别检索 Google Patents，合并去重后返回。

    - 角度间间隔 2 秒，避免触发 Google Patents 503 限流
    - 前 2 个角度连续失败（503）则停止后续角度，直接返回空
    - 调用方应回退到 search_patents_with_fallback

    Args:
        strategies: [{"angle": ..., "query": ..., "rationale": ...}, ...]
        num_per_angle: 每个角度取前 N 条
        total: 合并后总上限

    Returns:
        去重后的专利列表（按命中角度数排序，多角度命中的排前）
    """
    import time

    patent_angles: dict[str, list[str]] = {}
    patent_map: dict[str, Patent] = {}
    consecutive_failures = 0

    for i, strat in enumerate(strategies):
        query = (strat.get("query") or "").strip()
        angle = strat.get("angle", "")
        if not query:
            continue
        # 角度间间隔 2 秒（第一个不等待），降低 503 风险
        if i > 0:
            time.sleep(2)
        # 每个角度走 Google Patents（US 优先 + 全球兜底）
        hits = search_google_patents(query, num=num_per_angle, country="US")
        if len(hits) < 3:
            time.sleep(1)
            hits = search_google_patents(query, num=num_per_angle, country="")

        if not hits:
            consecutive_failures += 1
            # 前 2 个角度连续失败 → Google Patents 大概率在限流，停止后续
            if consecutive_failures >= 2 and not patent_map:
                print(f"[search_by_strategies] 前 {consecutive_failures} 个角度连续失败，停止后续（Google Patents 可能限流）")
                return []
        else:
            consecutive_failures = 0

        for p in hits:
            key = p.patent_number
            if not key:
                continue
            if key not in patent_map:
                patent_map[key] = p
                patent_angles[key] = []
            if angle and angle not in patent_angles[key]:
                patent_angles[key].append(angle)

    if not patent_map:
        print("[search_by_strategies] 所有角度搜索均失败（可能 Google Patents 限流）")
        return []

    # 排序：被多角度命中的优先
    def sort_key(p: Patent) -> tuple:
        n_angles = len(patent_angles.get(p.patent_number, []))
        return (-n_angles,)

    ranked = sorted(patent_map.values(), key=sort_key)
    return ranked[:total]


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    load_dotenv()

    print("=== Testing search (with fallback) ===")
    results = search_patents_with_fallback("lithium battery termination tape electrolyte", num=15)
    print(f"Found {len(results)} patents:")
    for p in results[:8]:
        print(f"  [{p.source}] {p.patent_number} | {p.title[:55]} | {p.assignee[:25]}")