"""专利检索模块 — 多源回退，适应网络受限环境。

数据源优先级（自动回退，用户无感知）：
1. Google Patents xhr/query          — 最快，US/全球
2. USPTO PatentsView API             — 美国政府 API
3. EPO OPS API（欧洲专利局）          — 国内可达
4. WIPO Patentscope（联合国 WIPO）    — 国内可达
5. Google Scholar Patents            — 谷歌学术，国内常可通
6. LLM 生成（DeepSeek 训练知识）      — 网络受限时的保底
7. 本地真实专利缓存                   — 纯兜底

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

import base64
import html as html_mod
import json
import os
import re
import time
import urllib.parse
from dataclasses import dataclass, asdict
from pathlib import Path

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

# 专利数据源代理（Clash/V2Ray 本地代理）
# 默认 http://127.0.0.1:7890（Clash 默认端口）
# 设为空字符串则禁用代理（直连，国内会 503）
# 可通过环境变量 PATENT_PROXY 覆盖
_PATENT_PROXY = os.environ.get("PATENT_PROXY", "http://127.0.0.1:7890") or None

# EPO OPS API — 免费注册 developers.epo.org 获取
EPO_TOKEN_URL = "https://ops.epo.org/3.2/auth/accesstoken"
EPO_SEARCH_URL = "https://ops.epo.org/3.2/rest-services/published-data/search/biblio/"

# EPO token 缓存（20 分钟有效）
_epo_token: tuple[str, float] | None = None  # (token, expires_at)


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
    对于复杂 VOC（多句中文），会拆成 2-3 组核心技术词分别翻译再拼接。
    """
    if not _needs_translation(keywords):
        return keywords

    api_key = os.environ.get("DEEPSEEK_API_KEY", "")
    if not api_key:
        print("[translate] 无 API key，跳过翻译")
        return keywords

    # 如果 VOC 很长（整段描述），先提取核心技术词再翻译，避免整段文学翻译
    # 长 VOC 的文学翻译往往把技术术语意译掉，不适合专利搜索
    to_translate = keywords
    if len(keywords) > 60:
        to_translate = (
            f"Extract 3-5 core technical keyword groups (English preferred, with synonyms) "
            f"from this Chinese requirement for patent search:\n{keywords}"
        )

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        prompt = (
            "Translate the following Chinese technical keywords into concise English "
            "patent search queries. Keep technical terms precise (e.g. '感光干膜' → "
            "'dry film photoresist'). Add relevant English synonyms. "
            "Output ONLY the English keywords, no explanation, no Chinese.\n\n"
            f"{to_translate}"
        )
        resp = client.chat.completions.create(
            model=os.environ.get("DEEPSEEK_MODEL", "deepseek-v4-pro"),
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            max_tokens=512,
            extra_body={"thinking": {"type": "disabled"}},
        )
        translated = resp.choices[0].message.content.strip()
        # 清洗：去掉翻译器可能追加的前缀文本
        for prefix in ("English:", "Translation:", "Keywords:"):
            if translated.lower().startswith(prefix.lower()):
                translated = translated[len(prefix):].strip()
        if translated and _needs_translation(translated):
            # 翻译后仍是中文（V4 thinking 污染等边缘情况）→ 丢弃
            print(f"[translate] 翻译结果仍含中文，丢弃: {translated[:100]}")
            return keywords
        if translated:
            print(f"[translate] 翻译成功: {keywords[:60]}... → {translated[:120]}")
            return translated
        return keywords
    except Exception as e:
        print(f"[translate] 翻译失败: {e}")
        return keywords


# ---------------------------------------------------------------------------
# 1. USPTO PatentsView API（若可达）
# ---------------------------------------------------------------------------

def search_patentsview(
    keywords: str, *, num: int = 20, timeout: float = 8.0
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
        with httpx.Client(headers=BROWSER_HEADERS, timeout=timeout, proxy=_PATENT_PROXY) as client:
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
    keywords: str, *, num: int = 20, country: str = "US", timeout: float = 6.0,
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
            proxy=_PATENT_PROXY,
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
# 3. Google Scholar 专利搜索（谷歌学术，国内常可通）
# ---------------------------------------------------------------------------

def search_google_scholar(
    keywords: str, *, num: int = 20, timeout: float = 6.0
) -> list[Patent]:
    """从 Google Scholar 检索专利。

    Google Scholar 在国内通常可访问（不同于其他 Google 服务）。
    as_sdt=7 表示包含专利结果。
    """
    url = "https://scholar.google.com/scholar"
    params = {
        "q": keywords,
        "as_sdt": "7,50",  # 7=include patents, 50=include citations
        "num": str(min(num, 20)),
        "hl": "en",
    }
    headers = {
        **BROWSER_HEADERS,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    try:
        with httpx.Client(headers=headers, timeout=timeout, follow_redirects=True, proxy=_PATENT_PROXY) as client:
            resp = client.get(url, params=params)
            resp.raise_for_status()
            html_text = resp.text
    except Exception as e:
        print(f"[google_scholar] 检索失败: {e}")
        return []

    return _parse_scholar_html(html_text, keywords)[:num]


def _parse_scholar_html(html_text: str, keywords: str) -> list[Patent]:
    """解析 Google Scholar 搜索结果 HTML，提取专利信息。"""
    patents: list[Patent] = []

    # Scholar 结果块：<div class="gs_r gs_or gs_scl" data-cid="..."> ... </div>
    # 注意：class 后面可能有 data-cid 等其他属性，不能要求 > 紧跟 class
    # 用非贪婪匹配到下一个 gs_r 块或页面底部
    result_blocks = re.findall(
        r'<div\s+class="gs_r\s+gs_or\s+gs_scl"[^>]*>(.*?)(?=<div\s+class="gs_r\s+gs_or\s+gs_scl"|<div\s+id="gs_nmd"|<div\s+id="gs_ft")',
        html_text, re.DOTALL,
    )
    if not result_blocks:
        # 备选：更宽松的匹配
        result_blocks = re.findall(
            r'<div\s+class="gs_r[^"]*"[^>]*>(.*?)(?=<div\s+class="gs_r[^"]*"|<div\s+id="gs_ft")',
            html_text, re.DOTALL,
        )

    for block in result_blocks:
        # 提取标题：<h3 class="gs_rt">...<a href="...">title</a>...</h3>
        title_match = re.search(
            r'<h3\s+class="gs_rt"[^>]*>.*?<a[^>]*>(.*?)</a>',
            block, re.DOTALL | re.IGNORECASE,
        )
        if not title_match:
            continue
        title = _clean_html(title_match.group(1))

        # 提取元信息（作者/专利号/日期）：<div class="gs_a">
        meta_match = re.search(
            r'<div\s+class="gs_a"[^>]*>(.*?)</div>',
            block, re.DOTALL | re.IGNORECASE,
        )
        meta = _clean_html(meta_match.group(1)) if meta_match else ""

        # 提取专利号：优先从 patents.google.com 链接或 PDF 链接提取
        # Scholar meta 里是 "US Patent App. 18/400,360" 格式（申请号，非专利号）
        # 真正的专利号在 href="https://patents.google.com/patent/US20240136686A1/en" 里
        patent_num = ""
        country = ""
        pat_link = re.search(
            r'href="https?://patents\.google\.com/patent/([A-Z]{2}\d{6,12}[AB]\d?)/en"',
            block, re.IGNORECASE,
        )
        if pat_link:
            patent_num = pat_link.group(1)
            country = patent_num[:2]
        else:
            # 备选：PDF 链接 patentimages.../{num}.pdf
            pdf_link = re.search(
                r'href="https?://patentimages[^"]*/([A-Z]{2}\d{6,12}[AB]\d?)\.pdf"',
                block, re.IGNORECASE,
            )
            if pdf_link:
                patent_num = pdf_link.group(1)
                country = patent_num[:2]

        # 提取片段：<div class="gs_rs">
        snippet_match = re.search(
            r'<div\s+class="gs_rs"[^>]*>(.*?)</div>',
            block, re.DOTALL | re.IGNORECASE,
        )
        snippet = _clean_html(snippet_match.group(1)) if snippet_match else ""

        # 提取链接
        url_link = ""
        if patent_num:
            url_link = f"https://patents.google.com/patent/{patent_num}/en"
        else:
            link_match = re.search(
                r'<h3\s+class="gs_rt"[^>]*>.*?<a\s+href="([^"]+)"',
                block, re.DOTALL | re.IGNORECASE,
            )
            if link_match:
                url_link = link_match.group(1)
                if url_link.startswith("/"):
                    url_link = f"https://scholar.google.com{url_link}"

        # 提取 assignee：从 meta 中取 "- " 之后的部分
        assignee = ""
        if " - " in meta:
            assignee = meta.rsplit(" - ", 1)[-1].strip()
            # 去掉末尾的 "Google Patents" 等来源标识
            assignee = re.sub(r'\s*Google\s+Patents?\s*$', '', assignee, flags=re.IGNORECASE).strip()

        # 提取日期
        pub_date = ""
        date_match = re.search(r'(\d{4})', meta)
        if date_match:
            pub_date = date_match.group(1)

        if not patent_num:
            # 没有专利号的结果跳过（可能是论文而非专利）
            continue

        patents.append(Patent(
            patent_number=patent_num,
            title=title[:300],
            assignee=assignee[:200],
            snippet=snippet[:500],
            publication_date=pub_date,
            source="google_scholar",
            url=url_link,
            country=country or patent_num[:2],
        ))

    return patents


def _clean_html(html_str: str) -> str:
    """去除 HTML 标签并解码实体。"""
    text = re.sub(r'<[^>]+>', ' ', html_str)
    text = html_mod.unescape(text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


# ---------------------------------------------------------------------------
# 4. EPO OPS API（欧洲专利局 — 国内可达）
# ---------------------------------------------------------------------------

def _get_epo_token() -> str | None:
    """获取 EPO OAuth2 access token（缓存 20 分钟）。"""
    global _epo_token
    key = os.environ.get("EPO_OPS_KEY", "")
    secret = os.environ.get("EPO_OPS_SECRET", "")
    if not key or not secret:
        return None

    now = time.time()
    if _epo_token and _epo_token[1] > now + 60:
        return _epo_token[0]

    credentials = f"{key}:{secret}"
    encoded = base64.b64encode(credentials.encode()).decode()
    try:
        with httpx.Client(timeout=10.0, proxy=_PATENT_PROXY) as client:
            resp = client.post(
                EPO_TOKEN_URL,
                data={"grant_type": "client_credentials"},
                headers={
                    "Authorization": f"Basic {encoded}",
                    "Content-Type": "application/x-www-form-urlencoded",
                },
            )
            resp.raise_for_status()
            data = resp.json()
            token = data.get("access_token", "")
            expires_in = data.get("expires_in", 1200)  # 默认 20 分钟
            if token:
                _epo_token = (token, now + expires_in)
                return token
    except Exception as e:
        print(f"[epo_ops] 获取 token 失败: {e}")
    return None


def search_epo_ops(
    keywords: str, *, num: int = 20, timeout: float = 8.0
) -> list[Patent]:
    """从 EPO Open Patent Services 检索全球专利。

    需要免费注册 EPO OPS API key：https://developers.epo.org/
    设置环境变量 EPO_OPS_KEY 和 EPO_OPS_SECRET。
    未配置时静默跳过。
    """
    token = _get_epo_token()
    if not token:
        return []

    # EPO OPS 使用 CQL (Contextual Query Language) 或简单文本
    # 将关键词转为 CQL 全文搜索
    cql = ' or '.join(f'txt="{w}"' for w in keywords.split() if len(w) > 1)
    if not cql:
        cql = f'txt="{keywords}"'

    url = EPO_SEARCH_URL
    params = {"q": cql, "Range": f"1-{min(num, 25)}"}

    try:
        with httpx.Client(
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/xml",
                "User-Agent": BROWSER_HEADERS["User-Agent"],
            },
            timeout=timeout,
            proxy=_PATENT_PROXY,
        ) as client:
            resp = client.get(url, params=params)
            if resp.status_code == 403:
                # Token 过期，清除缓存下次重试
                global _epo_token
                _epo_token = None
                print("[epo_ops] token 过期，下次将刷新")
                return []
            resp.raise_for_status()
            xml_text = resp.text
    except Exception as e:
        print(f"[epo_ops] 检索失败: {e}")
        return []

    return _parse_epo_search_xml(xml_text)


def _parse_epo_search_xml(xml_text: str) -> list[Patent]:
    """解析 EPO OPS search/biblio XML 响应，提取专利信息。"""
    patents: list[Patent] = []

    # 每个专利在一个 <ops:search-result> 或 <exchange-document> 块中
    # EPO OPS 返回的 XML 结构较复杂，用正则提取关键字段

    # 匹配每个专利文档块
    doc_blocks = re.findall(
        r'<ops:search-result\s[^>]*>(.*?)</ops:search-result>',
        xml_text, re.DOTALL,
    )
    if not doc_blocks:
        # 备选：匹配 exchange-document
        doc_blocks = re.findall(
            r'<exchange-document[^>]*>(.*?)</exchange-document>',
            xml_text, re.DOTALL,
        )

    for block in doc_blocks:
        # 提取 publication-reference 中的专利号
        pub_ref = re.search(
            r'<ops:publication-reference[^>]*>(.*?)</ops:publication-reference>',
            block, re.DOTALL,
        )
        if not pub_ref:
            pub_ref = re.search(
                r'<publication-reference[^>]*>(.*?)</publication-reference>',
                block, re.DOTALL,
            )

        country = ""
        doc_number = ""
        kind = ""
        if pub_ref:
            doc_id = pub_ref.group(1)
            country_m = re.search(r'<country[^>]*>([A-Z]{2})</country>', doc_id)
            number_m = re.search(r'<doc-number[^>]*>(\d+)</doc-number>', doc_id)
            kind_m = re.search(r'<kind[^>]*>([AB]\d?)</kind>', doc_id)
            country = country_m.group(1) if country_m else ""
            doc_number = number_m.group(1) if number_m else ""
            kind = kind_m.group(1) if kind_m else ""

        patent_number = f"{country}{doc_number}{kind}" if country and doc_number else ""

        # 提取标题（invention-title）
        title = ""
        title_m = re.search(
            r'<invention-title[^>]*>(.*?)</invention-title>',
            block, re.DOTALL | re.IGNORECASE,
        )
        if title_m:
            title = _clean_xml(title_m.group(1))

        # 提取摘要
        abstract = ""
        ab_m = re.search(
            r'<abstract[^>]*>(.*?)</abstract>',
            block, re.DOTALL | re.IGNORECASE,
        )
        if ab_m:
            # 摘要里可能有 <p> 等标签
            abstract = _clean_xml(ab_m.group(1))

        # 提取申请人/受让人
        assignee = ""
        applicant_m = re.search(
            r'<applicant[^>]*>.*?<applicant-name[^>]*>(.*?)</applicant-name>',
            block, re.DOTALL | re.IGNORECASE,
        )
        if applicant_m:
            assignee = _clean_xml(applicant_m.group(1))

        # 提取公开日
        pub_date = ""
        date_m = re.search(
            r'<publication-date[^>]*>(\d{4}-\d{2}-\d{2})</publication-date>',
            block,
        )
        if date_m:
            pub_date = date_m.group(1)
        else:
            # 备选：从 document-id 的 date 取
            date_m2 = re.search(r'<date[^>]*>(\d{4})(\d{2})(\d{2})</date>', block)
            if date_m2:
                pub_date = f"{date_m2.group(1)}-{date_m2.group(2)}-{date_m2.group(3)}"

        if not patent_number:
            continue

        url = f"https://worldwide.espacenet.com/patent/{patent_number}" if patent_number else ""

        patents.append(Patent(
            patent_number=patent_number,
            title=title[:300],
            assignee=assignee[:200],
            snippet=abstract[:500],
            publication_date=pub_date,
            source="epo_ops",
            url=url,
            country=country,
        ))

    return patents


def _clean_xml(xml_str: str) -> str:
    """去除 XML/HTML 标签并解码实体。"""
    text = re.sub(r'<[^>]+>', ' ', xml_str)
    text = html_mod.unescape(text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


# ---------------------------------------------------------------------------
# 5. WIPO Patentscope（联合国 WIPO — 国内可达）
# ---------------------------------------------------------------------------

def search_wipo_patentscope(
    keywords: str, *, num: int = 20, timeout: float = 8.0
) -> list[Patent]:
    """从 WIPO Patentscope 检索国际专利。

    WIPO 是联合国机构，国内通常可达。使用 JSF 表单提交搜索。
    """
    try:
        with httpx.Client(
            headers={
                **BROWSER_HEADERS,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            },
            timeout=timeout,
            follow_redirects=True,
            proxy=_PATENT_PROXY,
        ) as client:
            # Step 1: GET 搜索页面，获取 JSF ViewState 和 cookies
            search_url = "https://patentscope.wipo.int/search/en/search.jsf"
            resp = client.get(search_url)
            resp.raise_for_status()
            html_page = resp.text

            # 提取 javax.faces.ViewState
            viewstate_m = re.search(
                r'name="javax\.faces\.ViewState"\s+id="[^"]*"\s+value="([^"]+)"',
                html_page,
            )
            if not viewstate_m:
                # 新版可能使用不同的 id
                viewstate_m = re.search(
                    r'<input[^>]+name="javax\.faces\.ViewState"[^>]+value="([^"]+)"',
                    html_page,
                )
            if not viewstate_m:
                print("[wipo] 未找到 ViewState")
                return []
            viewstate = viewstate_m.group(1)

            # Step 2: POST 搜索表单
            form_data = {
                "searchForm": "searchForm",
                "searchForm:searchServer": "searchForm:searchServer",
                "searchForm:queryStr": keywords,
                "searchForm:commandSearch": "Search",
                "javax.faces.ViewState": viewstate,
                "javax.faces.source": "searchForm:commandSearch",
            }

            resp2 = client.post(
                search_url,
                data=form_data,
                headers={
                    **BROWSER_HEADERS,
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Referer": search_url,
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                },
            )
            resp2.raise_for_status()
            result_html = resp2.text
    except Exception as e:
        print(f"[wipo] 检索失败: {e}")
        return []

    return _parse_wipo_html(result_html)[:num]


def _parse_wipo_html(html_text: str) -> list[Patent]:
    """解析 WIPO Patentscope 搜索结果 HTML。"""
    patents: list[Patent] = []

    # WIPO 结果行可能包含在 <table> 中
    # 匹配结果行中的数据
    # 常见模式：<a class="resultNumber"> 包含专利号链接

    # 方式 1：匹配专利号链接（如 WO2023123456）
    patent_links = re.findall(
        r'<a[^>]*href="[^"]*/(WO|US|EP|CN|JP|KR)(\d{6,12})[^"]*"[^>]*>(.*?)</a>',
        html_text, re.DOTALL | re.IGNORECASE,
    )

    seen: set[str] = set()
    for country, num, title_text in patent_links:
        patent_num = f"{country}{num}"
        if patent_num in seen:
            continue
        seen.add(patent_num)
        title = _clean_html(title_text)
        if len(title) < 3:
            title = patent_num

        patents.append(Patent(
            patent_number=patent_num,
            title=title[:300],
            assignee="",
            snippet="",
            publication_date="",
            source="wipo_patentscope",
            url=f"https://patentscope.wipo.int/search/en/detail.jsf?docId={patent_num}",
            country=country,
        ))

    # 方式 2：如果方式 1 没找到，尝试匹配 table 行
    if not patents:
        rows = re.findall(
            r'<tr[^>]*class="[^"]*result[^"]*"[^>]*>(.*?)</tr>',
            html_text, re.DOTALL,
        )
        for row in rows:
            # 提取所有文本
            cells = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', row, re.DOTALL)
            texts = [_clean_html(c) for c in cells if _clean_html(c)]

            if not texts:
                continue

            # 第一个非空文本通常是专利号
            patent_num = ""
            for t in texts:
                pat_m = re.match(r'([A-Z]{2}\d{6,12}[AB]\d?)', t)
                if pat_m:
                    patent_num = pat_m.group(1)
                    break

            if not patent_num:
                continue

            title = texts[1] if len(texts) > 1 else ""
            pub_date = texts[2] if len(texts) > 2 else ""
            assignee = texts[3] if len(texts) > 3 else ""

            patents.append(Patent(
                patent_number=patent_num,
                title=title[:300],
                assignee=assignee[:200],
                snippet="",
                publication_date=pub_date,
                source="wipo_patentscope",
                url=f"https://patentscope.wipo.int/search/en/detail.jsf?docId={patent_num}",
                country=patent_num[:2],
            ))

    return patents


# ---------------------------------------------------------------------------
# 6. LLM 生成候选专利（当所有外部 API 均不可达时的保底）
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
            model="deepseek-v4-pro",
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
# 7. 中国专利回退
# ---------------------------------------------------------------------------

def search_cn_patents(keywords: str, *, num: int = 20, timeout: float = 12.0) -> list[Patent]:
    """中国专利回退：Google Patents 全球检索后过滤 CN。"""
    all_pats = search_google_patents(keywords, num=num * 2, country="", timeout=timeout)
    return [p for p in all_pats if p.country == "CN"][:num]


# ---------------------------------------------------------------------------
# 8. 专利详情抓取
# ---------------------------------------------------------------------------

def fetch_patent_detail(patent_number: str, *, timeout: float = 6.0) -> str:
    """抓取单篇专利的全文文本。

    优先级：
    1. Google Patents（全文 Claims+Description，国内常 503）
    2. EPO Espacenet（全文，国内常 403）
    3. Google Scholar 按专利号搜索（仅摘要，国内可达的兜底）
    """
    num_clean = patent_number.strip()

    # 路径 1：Google Patents
    url = f"https://patents.google.com/patent/{num_clean}/en"
    try:
        with httpx.Client(
            headers={**BROWSER_HEADERS, "Referer": "https://patents.google.com/"},
            timeout=timeout,
            proxy=_PATENT_PROXY,
        ) as client:
            resp = client.get(url)
            resp.raise_for_status()
            html_text = resp.text
            detail = _extract_patent_detail_from_html(html_text)
            if detail:
                print(f"[detail] OK Google Patents {num_clean}: {len(html_text)//1024}KB HTML -> {len(detail)} chars")
                return detail
            else:
                print(f"[detail] WARN Google Patents {num_clean}: {len(html_text)//1024}KB HTML but parser empty")
    except Exception as e:
        print(f"[detail] FAIL Google Patents {num_clean}: {type(e).__name__}: {e}")

    # 路径 2：EPO Espacenet（国内可达）
    epo_url = f"https://worldwide.espacenet.com/patent/search/family/{num_clean}/en"
    try:
        with httpx.Client(
            headers={**BROWSER_HEADERS, "Referer": "https://worldwide.espacenet.com/"},
            timeout=timeout,
            proxy=_PATENT_PROXY,
        ) as client:
            resp = client.get(epo_url)
            if resp.status_code >= 400:
                epo_url2 = f"https://worldwide.espacenet.com/patent/{num_clean}"
                resp = client.get(epo_url2)
            resp.raise_for_status()
            html_text = resp.text
            detail = _extract_patent_detail_from_html(html_text)
            if detail:
                print(f"[detail] OK EPO Espacenet {num_clean}: {len(detail)} chars")
                return detail
            else:
                print(f"[detail] WARN EPO Espacenet {num_clean}: HTML parsed but empty")
    except Exception as e:
        print(f"[detail] FAIL EPO Espacenet {num_clean}: {type(e).__name__}: {e}")

    # 路径 3：Google Scholar 按专利号搜索（兜底，仅摘要）
    # 当 Google Patents 503 + EPO 403 时，用 Scholar 搜专利号能拿到摘要
    try:
        scholar_pats = search_google_scholar(num_clean, num=3, timeout=8.0)
        for p in scholar_pats:
            if p.patent_number == num_clean and p.snippet:
                print(f"[detail] OK Google Scholar {num_clean}: {len(p.snippet)} chars (摘要兜底)")
                return f"[Abstract] {p.snippet}"
        # Scholar 没精确匹配，但有结果时也返回第一条摘要
        if scholar_pats and scholar_pats[0].snippet:
            print(f"[detail] OK Google Scholar {num_clean} (模糊匹配 {scholar_pats[0].patent_number}): {len(scholar_pats[0].snippet)} chars")
            return f"[Abstract] {scholar_pats[0].snippet}"
    except Exception as e:
        print(f"[detail] FAIL Google Scholar {num_clean}: {type(e).__name__}: {e}")

    print(f"[detail] FAIL ALL {num_clean}: all sources failed")
    return ""


def _extract_patent_detail_from_html(html_text: str) -> str:
    """从专利 HTML 页面提取详情文本（Google Patents / Espacenet 通用）。

    新版 Google Patents（2024+）使用 server-rendered HTML，数据在
    <meta>/<abstract>/<section> 标签中，不需要 JS 渲染。
    """
    text_parts: list[str] = []

    # 1. 摘要：优先 <abstract> 标签（Google Patents 新版），
    #    回退到 <meta name="description">
    abstract = re.search(
        r'<abstract[^>]*>(.*?)</abstract>',
        html_text, re.DOTALL | re.IGNORECASE,
    )
    if abstract:
        ab_text = re.sub(r"<[^>]+>", " ", abstract.group(1))
        ab_text = re.sub(r"\s+", " ", ab_text).strip()
        if ab_text and len(ab_text) > 30:
            text_parts.append(f"[Abstract] {ab_text}")
    else:
        desc = re.search(
            r'<meta[^>]+name="description"[^>]+content="([^"]+)"',
            html_text, re.IGNORECASE,
        )
        if desc:
            d_text = desc.group(1).strip()
            if d_text and len(d_text) > 30:
                text_parts.append(f"[Abstract] {d_text}")

    # 2. 专利权人 + 发明人（来自 meta 标签）
    inventors: list[str] = []
    assignee = ""
    for m in re.finditer(
        r'<meta\s+name="DC\.contributor"\s+content="([^"]+)"\s+scheme="(\w+)"',
        html_text, re.IGNORECASE,
    ):
        name = m.group(1).strip()
        scheme = m.group(2)
        if scheme == "inventor" and name:
            inventors.append(name)
        elif scheme == "assignee" and name:
            assignee = name
    if inventors:
        text_parts.append(f"[Inventors] {', '.join(inventors[:20])}")
    if assignee:
        text_parts.append(f"[Assignee] {assignee}")

    # 3. 权利要求 — V4 Pro 1M 上下文，无需激进截断
    claims = re.search(
        r'<section[^>]*itemprop="claims"[^>]*>(.*?)</section>',
        html_text, re.DOTALL | re.IGNORECASE,
    )
    if claims:
        claims_text = re.sub(r"<[^>]+>", " ", claims.group(1))
        claims_text = re.sub(r"\s+", " ", claims_text).strip()
        if claims_text:
            text_parts.append(f"[Claims] {claims_text[:8000]}")

    # 4. 详细描述 — V4 Pro 1M 上下文，保留更多实验数据
    desc_sec = re.search(
        r'<section[^>]*itemprop="description"[^>]*>(.*?)</section>',
        html_text, re.DOTALL | re.IGNORECASE,
    )
    if desc_sec:
        desc_text = re.sub(r"<[^>]+>", " ", desc_sec.group(1))
        desc_text = re.sub(r"\s+", " ", desc_text).strip()
        # 描述的"Cross Reference"部分通常很长且信息量低，截掉前 500 字符
        # 如果开头是 "CROSS REFERENCE" 就跳过去
        if desc_text.upper().startswith("CROSS REFERENCE"):
            # 找第一个有意义段落（"FIELD" 或 "BACKGROUND" 之后）
            field = re.search(
                r'(FIELD|BACKGROUND|TECHNICAL FIELD|SUMMARY|DETAILED DESCRIPTION)',
                desc_text, re.IGNORECASE,
            )
            if field:
                desc_text = desc_text[field.start():]
        if desc_text:
            text_parts.append(f"[Description] {desc_text[:16000]}")

    return "\n\n".join(text_parts) if text_parts else ""


# ---------------------------------------------------------------------------
# 9. 统一入口：多级回退
# ---------------------------------------------------------------------------

def search_patents_with_fallback(
    keywords: str, *, num: int = 20, prefer_us: bool = True
) -> list[Patent]:
    """多级回退检索 — 6 级自动切换，优先 Google，被墙自动跳下一级。

    回退链（每级拿 >= 5 条结果就提前返回）：
      1. Google Patents xhr/query（US first → global）
         └─ 含中文关键词 → 自动翻译英文重试
      2. USPTO PatentsView API（美国政府，国内可能可达）
      3. EPO OPS API（欧洲专利局，国内可达，需免费注册）
      4. WIPO Patentscope（联合国 WIPO，国内可达）
      5. Google Scholar Patents（谷歌学术，国内常可通）
      6. 中国专利过滤（via Google Patents，如果还能通）
      7. LLM 生成（需 PATENTS_ALLOW_LLM_FALLBACK=1）
      8. 本地真实专利缓存（纯保底）
    """
    # 将收集结果和去重合并的逻辑提取为闭包
    all_candidates: dict[str, Patent] = {}  # patent_number → Patent

    def collect(pats: list[Patent], label: str) -> bool:
        """添加候选专利，返回是否 >= num 条不同的结果"""
        for p in pats:
            if p.patent_number and p.patent_number not in all_candidates:
                all_candidates[p.patent_number] = p
        if len(all_candidates) >= 5:
            print(f"[fallback] {label} 满足阈值 ({len(all_candidates)} 条)，返回")
            return True
        return False

    # ---- 处理翻译 ----
    en_kw = keywords
    if _HAS_CHINESE_RE.search(keywords):
        en_kw = _translate_keywords(keywords)
        if en_kw == keywords:
            en_kw = keywords  # 翻译失败，用原文

    best_kw = en_kw if en_kw != keywords else keywords  # 优先用翻译后的英文

    # ---- 第 1 级：Google Patents（单次快速探测，5s 超时） ----
    # 被墙时 TCP 连接会挂到超时，4 次尝试 = 48s+，砍成 1 次全球检索 5s 超时
    gp = search_google_patents(best_kw, num=num, country="", timeout=5.0)
    if collect(gp, "Google Patents"):
        return list(all_candidates.values())[:num]

    if not gp:
        print("[fallback] Google Patents 不可达（被墙/503），切换到备选源")

    # ---- 第 2 级：USPTO PatentsView（美国专利，8s 超时） ----
    if prefer_us:
        us_pats = search_patentsview(best_kw, num=num, timeout=8.0)
        if collect(us_pats, "USPTO PatentsView"):
            return list(all_candidates.values())[:num]

    # ---- 第 3 级：EPO OPS（欧洲专利局，8s 超时） ----
    epo_pats = search_epo_ops(best_kw, num=num, timeout=8.0)
    if collect(epo_pats, "EPO OPS"):
        return list(all_candidates.values())[:num]

    # ---- 第 4 级：WIPO Patentscope（联合国，8s 超时） ----
    wipo_pats = search_wipo_patentscope(best_kw, num=num, timeout=8.0)
    if collect(wipo_pats, "WIPO Patentscope"):
        return list(all_candidates.values())[:num]

    # ---- 第 5 级：Google Scholar（谷歌学术，6s 超时） ----
    scholar_pats = search_google_scholar(best_kw, num=num, timeout=6.0)
    if collect(scholar_pats, "Google Scholar"):
        return list(all_candidates.values())[:num]

    # ---- 第 6 级：中国专利过滤 ----
    cn_pats = search_cn_patents(keywords, num=num)
    if collect(cn_pats, "CN Patents"):
        return list(all_candidates.values())[:num]

    # ---- 第 7 级：LLM 生成 ----
    if os.environ.get("PATENTS_ALLOW_LLM_FALLBACK", "0") == "1":
        llm_pats = search_via_llm(keywords, num=num)
        if collect(llm_pats, "LLM Generated"):
            return list(all_candidates.values())[:num]

    # ---- 第 8 级：本地真实专利缓存 ----
    local_pats = search_local_cache(keywords)
    if collect(local_pats, "Local Cache"):
        return list(all_candidates.values())[:num]

    # 全失败：返回已收集到的（即使 < 5 条）
    result = list(all_candidates.values())
    print(f"[fallback] 所有源已尝试，最终返回 {len(result)} 条")
    return result[:num]


# ---------------------------------------------------------------------------
# 10. 多策略搜索合并（VOC 拆解后逐角度搜索，合并去重）
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
            time.sleep(0.5)
        # 主源：Google Patents 快速探测（5s超时，被墙时快速失败）
        hits = search_google_patents(query, num=num_per_angle, country="US", timeout=5.0)
        if len(hits) < 3:
            time.sleep(0.5)
            hits = search_google_patents(query, num=num_per_angle, country="", timeout=5.0)

        # 备份源：Google Patents 不可达（503/被墙）时用 Google Scholar 兜底
        if not hits:
            print(f"[search_by_strategies] Google Patents 失败，角度 {i+1} 回退 Google Scholar")
            scholar_hits = search_google_scholar(query, num=num_per_angle, timeout=8.0)
            if scholar_hits:
                hits = scholar_hits

        if not hits:
            consecutive_failures += 1
            # 第 1 个角度失败 → Google 被墙，立即回退
            if consecutive_failures >= 1 and not patent_map:
                print(f"[search_by_strategies] 角度 {i+1} 失败，Google Patents+Scholar 均不可达，立即回退")
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