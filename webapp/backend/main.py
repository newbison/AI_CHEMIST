"""FastAPI 后端 — R&D 智能报告生成器。

路由：
  GET  /api/health              — 健康检查
  POST /api/search              — 专利检索（三级回退）
  POST /api/generate            — 报告生成（SSE 流式）

生产模式：
  - 前端由本后端在 /app 路由挂载静态文件（需先 npm run build）
  - 所有 /api/* 请求由 FastAPI 处理，其他请求返回 index.html
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# 加载 .env（优先项目根目录，再本地目录）
load_dotenv(Path(__file__).resolve().parents[2] / ".env")
load_dotenv()

from patent_search import (  # noqa: E402
    Patent,
    fetch_patent_detail,
    search_patents_with_fallback,
    search_by_strategies,
)
from prompt_builder import build_system_prompt, build_user_prompt  # noqa: E402
from llm_client import stream_report  # noqa: E402
from doc_analyzer import (  # noqa: E402
    analyze_document,
    extract_text_from_docx,
    extract_text_from_pdf,
)
from docx_export import markdown_to_docx  # noqa: E402
from pptx_export import markdown_to_pptx, markdown_to_pptx_via_pptxgenjs  # noqa: E402
from voc_analyzer import (  # noqa: E402
    analyze_voc_to_strategies,
    clarify_voc,
    enrich_voc,
    generate_voc_ideas,
)
from voc_scout import (  # noqa: E402
    scout_round1,
    scout_round2,
    market_share_search,
    ScoutRound2Input,
)
from deep_search import (  # noqa: E402
    DeepSearchInput,
    DeepSearchOutput,
    extract_new_terms,
    judge_convergence,
    run_map_reduce_pipeline,
    run_deep_search_pipeline,
    prescreen_patents,
)

app = FastAPI(title="R&D Intelligence Report Generator", version="1.0.0")

# CORS — 生产环境下同源部署无需 CORS；开发时需要 Vite 跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# 数据模型
# ---------------------------------------------------------------------------

class SearchRequest(BaseModel):
    voc: str
    keywords: str | None = None  # 可选自定义关键词，否则从 VOC 提取
    num: int = 20
    # 用户确认后的搜索策略（来自 /api/analyze-voc 的结果，可被用户修改）
    strategies: list[dict] | None = None


class AnalyzeVocRequest(BaseModel):
    voc: str
    num_angles: int = 4


class ClarifyVocRequest(BaseModel):
    voc: str
    num_questions: int = 4


class EnrichVocRequest(BaseModel):
    original_voc: str
    questions: list[dict]
    answers: dict[str, str]


class ExploreVocRequest(BaseModel):
    product: str
    context: str = ""
    direction: str = ""  # "next-gen" | "cost-down" | "adjacent" | ""
    num_ideas: int = 10


class GenerateRequest(BaseModel):
    voc: str
    patents: list[dict]  # 用户确认的入选专利列表
    fetch_details: bool = True  # 是否抓取每篇专利详情
    doc_analysis: str | None = None  # 用户上传文档的分析结果
    language: str = "en"  # "en" or "zh"
    deep_search_data: dict | None = None  # Deep Search 全景（市场份额、CTQ 表、技术路线、FTO、局限等）


class ExportDocxRequest(BaseModel):
    report: str  # Markdown 格式的报告文本
    filename: str | None = None
    title: str | None = None
    language: str = "en"


class ExportPptxRequest(BaseModel):
    report: str  # Markdown 格式的报告文本
    filename: str | None = None
    title: str | None = None
    language: str = "en"


# ---------------------------------------------------------------------------
# 路由
# ---------------------------------------------------------------------------

@app.get("/api/health")
def health() -> dict:
    return {
        "status": "ok",
        "deepseek_key_set": bool(os.environ.get("DEEPSEEK_API_KEY")),
    }


@app.post("/api/analyze-voc")
def analyze_voc(req: AnalyzeVocRequest) -> dict:
    """只做 VOC 分析，返回多角度搜索策略，不执行检索。

    供前端"先生成关键词 → 用户修改/确认 → 再检索"的两阶段流程使用。
    """
    strategies = analyze_voc_to_strategies(req.voc, num_angles=req.num_angles)
    if not strategies:
        # LLM 分析失败，回退到粗暴提取
        kw = _extract_keywords(req.voc)
        return {
            "strategies": [],
            "fallback_keywords": kw,
            "warning": "VOC 分析失败，已回退到关键词提取，可直接使用或手动修改",
        }
    return {
        "strategies": strategies,
        "fallback_keywords": "",
        "warning": "",
    }


@app.post("/api/clarify-voc")
def clarify_voc_endpoint(req: ClarifyVocRequest) -> dict:
    """分析 VOC，生成澄清选择题供用户作答。

    返回 3-5 道单选题，帮助用户明确 VOC 中的信息缺口和矛盾。
    """
    result = clarify_voc(req.voc, num_questions=req.num_questions)
    if not result["questions"]:
        return {
            "questions": [],
            "analysis": "",
            "warning": "VOC 澄清问题生成失败，可直接生成检索关键词",
        }
    return {
        "questions": result["questions"],
        "analysis": result["analysis"],
        "warning": "",
    }


@app.post("/api/upload-doc")
async def upload_doc(
    file: UploadFile = File(...),
    doc_name: str = Form(""),
) -> dict:
    """接收用户上传的 PDF/Word 文件，提取文本并调用 LLM 生成技术分析。

    请求：multipart/form-data
        - file: 文件（二进制）
        - doc_name: 文件名（可选）

    响应：{analysis, doc_name, text_preview}
    """
    from fastapi.responses import JSONResponse

    if not doc_name:
        doc_name = file.filename or "未知文件"

    # 检查文件类型
    ALLOWED_TYPES = {
        "application/pdf": "pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    }
    content_type = file.content_type or ""
    file_ext = ALLOWED_TYPES.get(content_type)

    # 尝试从文件名判断类型
    if not file_ext and file.filename:
        ext = file.filename.lower().split(".")[-1]
        if ext in ("pdf", "docx"):
            file_ext = ext

    if not file_ext:
        raise HTTPException(
            status_code=400,
            detail="不支持的文件格式，仅支持 PDF 和 Word (.docx)",
        )

    # 读取文件内容
    file_bytes = await file.read()

    # 检查文件大小（10MB）
    MAX_SIZE = 10 * 1024 * 1024
    if len(file_bytes) > MAX_SIZE:
        raise HTTPException(
            status_code=413,
            detail="文件超过 10MB 限制",
        )

    # 提取文本
    try:
        if file_ext == "pdf":
            text = extract_text_from_pdf(file_bytes)
        else:
            text = extract_text_from_docx(file_bytes)
    except ValueError as e:
        return JSONResponse(
            status_code=422,
            content={"error": str(e), "doc_name": doc_name, "text_preview": ""},
        )

    # 文本预览（取前500字符）
    text_preview = text[:500] + ("..." if len(text) > 500 else "")

    # 调用 LLM 分析
    analysis = analyze_document(text, doc_name)

    return {
        "analysis": analysis,
        "doc_name": doc_name,
        "text_preview": text_preview,
    }


@app.post("/api/enrich-voc")
def enrich_voc_endpoint(req: EnrichVocRequest) -> dict:
    """根据用户对澄清问题的答案，生成增强版 VOC。

    把原始 VOC 和用户答案合并，生成结构化的增强版 VOC。
    """
    result = enrich_voc(req.original_voc, req.questions, req.answers)
    return {
        "enriched_voc": result["enriched_voc"],
        "changes": result["changes"],
    }


@app.post("/api/explore-voc")
def explore_voc(req: ExploreVocRequest) -> dict:
    """Generate VOC ideas from product category + industry context."""
    ideas = generate_voc_ideas(
        req.product,
        context=req.context,
        direction=req.direction,
        num_ideas=req.num_ideas,
    )
    if not ideas:
        return {
            "ideas": [],
            "warning": (
                "AI failed to generate ideas. Please try a more specific "
                "product category, or enter your own VOC."
            ),
        }
    return {
        "ideas": [{"voc": i["voc"], "why": i["why"]} for i in ideas],
        "warning": "",
    }


@app.post("/api/search")
def search_patents(req: SearchRequest) -> dict:
    """专利检索 — VOC 驱动的多角度发现流程。

    流程：
    1. 若用户给了已确认的 strategies → 直接按策略逐角度检索（新路径，支持用户修改后的策略）
    2. 若用户给了自定义 keywords → 走单次回退检索（老路径）
    3. 否则 → 用 LLM 分析 VOC 拆解出多个技术角度 → 逐角度搜 Google Patents → 合并去重
    4. 若多角度搜索全失败（如 Google Patents 限流）→ 回退到单次搜索
    """
    # 路径1：用户已确认的策略（来自 /api/analyze-voc，可能被修改过）
    if req.strategies:
        strategies = [
            {
                "angle": s.get("angle", ""),
                "query": s.get("query", ""),
                "rationale": s.get("rationale", ""),
            }
            for s in req.strategies
            if s.get("query", "").strip()
        ]
        if not strategies:
            return {
                "keywords": "",
                "strategies": [],
                "total": 0,
                "patents": [],
                "warning": "没有有效的搜索策略",
            }
        # num_per_angle 按 total 动态计算，避免用户要 50 篇只拿到 32 篇
        num_per_angle = max(10, req.num // len(strategies) + 5)
        patents = search_by_strategies(strategies, num_per_angle=num_per_angle, total=req.num)
        # 全失败回退
        if not patents:
            fallback_query = strategies[0]["query"]
            patents = search_patents_with_fallback(fallback_query, num=req.num, prefer_us=True)
        warning = "" if patents else "Google Patents 暂时不可用（可能限流），请等待 1-2 分钟后重试"
        return {
            "keywords": " | ".join(s["query"] for s in strategies),
            "strategies": strategies,
            "total": len(patents),
            "patents": [p.to_dict() for p in patents],
            "warning": warning,
        }

    # 用户显式给了关键词：走老路径（单次检索）
    if req.keywords and req.keywords.strip():
        patents = search_patents_with_fallback(req.keywords.strip(), num=req.num, prefer_us=True)
        return {
            "keywords": req.keywords.strip(),
            "strategies": [],
            "total": len(patents),
            "patents": [p.to_dict() for p in patents],
            "warning": "" if patents else "未找到专利，Google Patents 可能限流，请稍后重试",
        }

    # 默认：VOC 驱动的多角度发现
    strategies = analyze_voc_to_strategies(req.voc)
    if not strategies:
        # LLM 分析失败，回退到粗暴提取
        kw = _extract_keywords(req.voc)
        patents = search_patents_with_fallback(kw, num=req.num, prefer_us=True)
        return {
            "keywords": kw,
            "strategies": [],
            "total": len(patents),
            "patents": [p.to_dict() for p in patents],
            "warning": "" if patents else "VOC 分析失败且未找到专利，请稍后重试",
        }

    patents = search_by_strategies(strategies, num_per_angle=8, total=req.num)

    # 多角度搜索全失败（如 Google Patents 503 限流）→ 回退到单次搜索
    if not patents:
        # 用第一个策略的 query 做单次搜索
        fallback_query = strategies[0].get("query", "")
        if fallback_query:
            patents = search_patents_with_fallback(fallback_query, num=req.num, prefer_us=True)

    warning = ""
    if not patents:
        warning = "Google Patents 暂时不可用（可能限流），请等待 1-2 分钟后重试"

    return {
        "keywords": " | ".join(s["query"] for s in strategies),
        "strategies": strategies,
        "total": len(patents),
        "patents": [p.to_dict() for p in patents],
        "warning": warning,
    }


@app.post("/api/generate")
def generate_report(req: GenerateRequest) -> StreamingResponse:
    """流式生成报告（SSE）。

    关键：专利详情抓取移到流内部进行，并先发 meta 事件，避免在
    网络不可达时整段同步阻塞、前端长时间无响应（"一直生成中"根因）。
    """
    patents = req.patents

    # 2. 构建 prompt（详情在流内补）
    system_prompt = build_system_prompt(req.language)

    def event_stream():
        # 先推送元信息 —— 让前端立即建立连接、显示进度
        yield f"data: {json.dumps({'type': 'meta', 'patent_count': len(patents)})}\n\n"

        # 用独立局部变量承载（可能被详情补全替换），避免对闭包变量赋值导致 UnboundLocalError
        working_patents = patents

        # 逐篇抓取专利详情（每篇 8s 超时；连续 3 篇失败则跳过剩余）
        if req.fetch_details:
            print(f"[generate] 开始抓取 {len(patents)} 篇专利详情...")
            enriched: list[dict] = []
            consecutive_failures = 0
            fetched_count = 0
            for i, p in enumerate(patents, 1):
                num = p.get("patent_number", "")
                detail = ""
                if num:
                    try:
                        detail = fetch_patent_detail(num, timeout=8.0)
                    except Exception as e:
                        print(f"[generate] 抓取 {num} 异常: {e}")
                        detail = ""
                if detail:
                    p = {**p, "detail_text": detail}
                    fetched_count += 1
                    consecutive_failures = 0
                    print(f"[generate] OK {i}/{len(patents)} {num}: {len(detail)} chars")
                else:
                    consecutive_failures += 1
                    print(f"[generate] FAIL {i}/{len(patents)} {num}: empty (fail {consecutive_failures}/3)")
                enriched.append(p)
                yield f"data: {json.dumps({'type': 'progress', 'stage': 'detail', 'index': i, 'total': len(patents), 'patent_number': num, 'ok': bool(detail)})}\n\n"
                # 连续 3 篇失败 → 数据源不可达，跳过剩余
                if consecutive_failures >= 3:
                    print(f"[generate] 连续 {consecutive_failures} 篇失败，跳过剩余 {len(patents) - i} 篇")
                    yield f"data: {json.dumps({'type': 'progress', 'stage': 'detail_skipped', 'reason': f'连续 {consecutive_failures} 篇抓取失败，数据源不可达，跳过剩余 {len(patents) - i} 篇，已抓取 {fetched_count} 篇'})}\n\n"
                    # 剩余专利不加 detail_text，直接追加
                    for p2 in patents[i:]:
                        enriched.append(p2)
                    break
            print(f"[generate] 详情抓取完成: {fetched_count}/{len(patents)} 篇成功, 总 enriched 专利 {len(enriched)} 篇")
            working_patents = enriched
        else:
            print(f"[generate] fetch_details=False, 跳过详情抓取")

        user_prompt = build_user_prompt(
            req.voc, working_patents,
            doc_analysis=req.doc_analysis,
            deep_search_data=req.deep_search_data,
        )

        # 诊断：确认详情文本确实进了 prompt
        detail_count = user_prompt.count('[Abstract]')
        claim_count = user_prompt.count('[Claims]')
        desc_count = user_prompt.count('[Description]')
        print(f"[generate] Prompt: {len(user_prompt)} chars ~{len(user_prompt)//4} tokens | "
              f"[Abstract]x{detail_count} [Claims]x{claim_count} [Description]x{desc_count} | "
              f"patents with detail_text: {sum(1 for p in working_patents if p.get('detail_text'))}")

        # 通知前端：即将调用 LLM（首 token 可能需要 20-60 秒，让前端知道在处理）
        prompt_size = len(system_prompt) + len(user_prompt)
        yield f"data: {json.dumps({'type': 'progress', 'stage': 'llm_calling', 'prompt_size': prompt_size})}\n\n"

        # 流式推送报告内容（stream_report 内置自动续写，输出截断时自动续写最多 5 次）
        try:
            for chunk in stream_report(system_prompt, user_prompt):
                yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
        except Exception as e:
            import traceback
            err_detail = traceback.format_exc()
            print(f"[generate] LLM 流式输出失败: {e}\n{err_detail}")
            yield f"data: {json.dumps({'type': 'error', 'message': f'LLM 生成失败: {e}'})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


def _make_content_disposition(filename: str) -> str:
    """构建支持 Unicode 的 Content-Disposition header (RFC 5987)。

    纯 ASCII 文件名直接引用；含中文等非 ASCII 字符时，追加 filename*=UTF-8''...
    确保浏览器下载时文件名不乱码，也不因 latin-1 编码限制而崩溃。
    """
    # ASCII fallback：取扩展名，用日期兜底
    ext = filename.rsplit(".", 1)[-1] if "." in filename else "bin"
    ascii_fallback = f"rd-report.{ext}"
    try:
        filename.encode("latin-1")
        return f'attachment; filename="{filename}"'
    except UnicodeEncodeError:
        from urllib.parse import quote
        encoded = quote(filename, safe="")
        return f"attachment; filename=\"{ascii_fallback}\"; filename*=UTF-8''{encoded}"


@app.post("/api/export-docx")
def export_docx(req: ExportDocxRequest):
    """把 Markdown 报告转成 Word (.docx) 文件下载。"""
    from fastapi.responses import Response

    docx_bytes = markdown_to_docx(req.report, title=req.title)
    filename = req.filename or f"rd-report-{__import__('datetime').datetime.now().strftime('%Y%m%d')}.docx"

    return Response(
        content=docx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": _make_content_disposition(filename)},
    )


@app.post("/api/export-pptx")
def export_pptx(req: ExportPptxRequest):
    """把 Markdown 报告转成 PowerPoint (.pptx) 文件下载。

    两条路径：
    1. **PptxGenJS 路径（优先）**：DeepSeek → JS 代码 → Node.js 执行 → 高质量 PPT
    2. **python-pptx 路径（回退）**：直接解析 Markdown 用 python-pptx 渲染

    只有 PptxGenJS 路径失败时才会走回退路径。
    """
    from fastapi.responses import Response

    # 路径 1：PptxGenJS（DeepSeek 生成 JS → Node.js 执行）
    pptx_bytes = markdown_to_pptx_via_pptxgenjs(req.report, title=req.title)

    # 路径 2（回退）：python-pptx 直接渲染
    if not pptx_bytes:
        print("[export-pptx] PptxGenJS 路径失败，回退到 python-pptx")
        pptx_bytes = markdown_to_pptx(req.report, title=req.title)

    filename = req.filename or f"rd-report-{__import__('datetime').datetime.now().strftime('%Y%m%d')}.pptx"

    return Response(
        content=pptx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        headers={"Content-Disposition": _make_content_disposition(filename)},
    )


# ---------------------------------------------------------------------------
# VOC Scout + Deep Search 端点
# ---------------------------------------------------------------------------

class ScoutRound2Request(BaseModel):
    voc: str
    selected_route_ids: list[str]
    focus: str = ""


class ScoutOutputRequest(BaseModel):
    """从用户最终选择组装三件套。"""
    voc: str
    selected_route_ids: list[str]
    selected_company_names: list[str] = []
    round_history: list[dict] = []


class ScoutOutputResponse(BaseModel):
    companies: dict
    keywords: dict
    ipc: dict
    fto: dict
    round_history: list[dict]
    confidence: str


class DeepSearchRequest(BaseModel):
    voc: str
    domain_class: str = ""
    p0_companies: list[str] = []
    p1_companies: list[str] = []
    core_keywords: list[str] = []
    supp_keywords: list[str] = []
    exclude_keywords: list[str] = []
    core_ipc: list[str] = []
    supp_ipc: list[str] = []
    fto_notes: list[str] = []
    round_history: list[dict] = []


class DeepSearchResponse(BaseModel):
    voc: str
    domain_class: str
    confidence: str
    search_path: str
    converged: bool
    total_rounds: int
    total_companies_found: int
    routes: list[dict]
    ctq_table: list[dict]
    fto: dict
    recommendation: dict
    convergence: dict
    user_corrections: list[dict] = []


class MapReduceRequest(BaseModel):
    patent_numbers: list[str]
    max_patents: int = 50


@app.post("/api/voc-scout/round1")
def voc_scout_round1(req: AnalyzeVocRequest) -> dict:
    """VOC Scout Round 1：从原始 VOC 探索技术方向。

    先跑双语市场份额搜索（Step 0），再用真实市场地位排序技术路线。
    返回 4-6 条技术路线 + 领域分类 + 置信度 + 市场份额数据。
    """
    # Step 0: 市场份额搜索（专利搜索之前，专利数 ≠ 市场地位）
    market_share = market_share_search(req.voc)
    result = scout_round1(req.voc, market_share=market_share)
    return {
        "domain_class": result.domain_class,
        "confidence": result.confidence,
        "analysis": result.analysis,
        "routes": [r.model_dump() for r in result.routes],
        "contradictions": result.contradictions,
        "market_share": market_share,
    }


@app.post("/api/voc-scout/round2")
def voc_scout_round2(req: ScoutRound2Request) -> dict:
    """VOC Scout Round 2：钻入选定路线。

    返回每条路线的公司详情（专利状态 + CTQ 值）。
    """
    result = scout_round2(ScoutRound2Input(
        voc=req.voc,
        selected_route_ids=req.selected_route_ids,
        focus=req.focus,
    ))
    return {
        "routes": [
            {
                "route_id": r.route_id,
                "route_name": r.route_name,
                "companies": [c.model_dump() for c in r.companies],
            }
            for r in result.routes
        ],
        "contradictions": result.contradictions,
        "confidence": result.confidence,
    }


@app.post("/api/voc-scout/output")
def voc_scout_output(req: ScoutOutputRequest) -> ScoutOutputResponse:
    """从用户最终选择组装三件套工具包。

    输出可直接喂给 Deep Search。
    """
    from openai import OpenAI as _OAI
    client = _OAI(
        api_key=os.environ.get("DEEPSEEK_API_KEY", ""),
        base_url=os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
        timeout=120.0,
    )
    prompt = (
        f"VOC: {req.voc}\n"
        f"Selected routes: {req.selected_route_ids}\n"
        f"Selected companies: {req.selected_company_names}\n"
        f"Round history: {json.dumps(req.round_history, ensure_ascii=False)}\n\n"
        "Based on the above, produce the final three-piece toolkit.\n"
        "Return ONLY valid JSON with keys: companies, keywords, ipc, fto, confidence.\n"
        "companies: {priority: [{level, name, product, tech, patent_status, patent, note}], domestic_reference: [...]}\n"
        "keywords: {core: [...], supplement: [...], exclude: [...]}\n"
        "ipc: {core: [...], supplement: [...]}\n"
        "fto: {notes: [...], sweep_query: \"...\"}"
    )
    resp = client.chat.completions.create(
        model=os.environ.get("DEEPSEEK_MODEL", "deepseek-v4-pro"),
        messages=[
            {"role": "system", "content": "You are a patent search strategist. Output only valid JSON."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
        max_tokens=4096,
        response_format={"type": "json_object"},
        extra_body={"thinking": {"type": "disabled"}},
    )
    raw = resp.choices[0].message.content.strip()
    data = _parse_json_safe_main(raw)

    # LLM 可能返回 float (0.85) 或 string ("★★☆")，统一转成 string
    confidence_raw = data.get("confidence", "★★☆")
    if isinstance(confidence_raw, (int, float)):
        if confidence_raw >= 0.8:
            confidence = "★★★"
        elif confidence_raw >= 0.5:
            confidence = "★★☆"
        else:
            confidence = "★☆☆"
    else:
        confidence = str(confidence_raw) if confidence_raw else "★★☆"

    return ScoutOutputResponse(
        companies=data.get("companies", {}),
        keywords=data.get("keywords", {}),
        ipc=data.get("ipc", {}),
        fto=data.get("fto", {}),
        round_history=req.round_history + [{"phase": "output"}],
        confidence=confidence,
    )


@app.post("/api/deep-search/start")
def deep_search_start(req: DeepSearchRequest) -> dict:
    """Deep Search：运行三轮迭代专利/产品检索。

    使用 patent_search.py 引擎（永不通过 LLM 合成专利数据）。
    Round 1: 公司定向搜索 + 关键词/IPC 宽搜
    Round 2: 新词提取 → 用新关键词/公司/IPC 重搜
    Round 3: 收敛验证

    返回完整专利全景（公司映射 + 收敛状态 + FTO + 建议）。
    Map-Reduce CTQ 提取请通过 /api/deep-search/map-reduce 单独调用。
    """
    inp = DeepSearchInput(**req.model_dump())
    result = run_deep_search_pipeline(inp)

    return {
        "voc": inp.voc,
        "domain_class": inp.domain_class,
        "confidence": "★★☆",
        "search_path": result["search_path"],
        "converged": result["converged"],
        "total_rounds": result["total_rounds"],
        "total_companies_found": result["total_companies_found"],
        "total_found": result["total_found"],
        "capped_to": result["capped_to"],
        "cap_note": result["cap_note"],
        "patents": result["all_patents"],
        "patent_count": result["capped_to"],
        "patent_numbers": result["capped_patent_numbers"],
        "convergence": result["convergence"],
        "fto": result["fto"],
        "recommendation": result["recommendation"],
    }


@app.post("/api/deep-search/map-reduce")
def deep_search_map_reduce(req: MapReduceRequest):
    """对一批专利号运行 Map-Reduce（SSE 流式，逐篇推送进度）。

    通过 patent_search.py 抓全文，逐篇提取 CTQ 记录，
    聚合成对比表。每完成一篇专利即推送进度事件。
    """
    import queue
    import threading

    q: queue.Queue = queue.Queue()

    def _on_progress(completed: int, total: int, patent_number: str, ok: bool):
        q.put({
            "type": "progress",
            "stage": "ctq",
            "completed": completed,
            "total": total,
            "patent_number": patent_number,
            "ok": ok,
        })

    def event_stream():
        result_holder: list = []
        error_holder: list = []

        def worker():
            try:
                from deep_search import run_map_reduce_pipeline
                result_holder.append(
                    run_map_reduce_pipeline(
                        patent_numbers=req.patent_numbers,
                        max_patents=req.max_patents,
                        on_progress=_on_progress,
                    )
                )
                q.put({"type": "reduce_start"})
                q.put({"type": "done", "result": result_holder[0]})
            except Exception as e:
                import traceback
                traceback.print_exc()
                error_holder.append(str(e))
                q.put({"type": "error", "message": str(e)})

        t = threading.Thread(target=worker, daemon=True)
        t.start()

        total_est = len(req.patent_numbers)
        yield f"data: {json.dumps({'type': 'meta', 'total': total_est})}\n\n"

        while True:
            try:
                msg = q.get(timeout=0.5)
                if msg["type"] == "done":
                    yield f"data: {json.dumps(msg)}\n\n"
                    break
                elif msg["type"] == "error":
                    yield f"data: {json.dumps(msg)}\n\n"
                    break
                else:
                    yield f"data: {json.dumps(msg)}\n\n"
            except queue.Empty:
                # 心跳，保持连接
                yield ": heartbeat\n\n"

        t.join(timeout=5)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.post("/api/deep-search/prescreen")
def deep_search_prescreen(req: MapReduceRequest) -> dict:
    """预筛：排序并选出值得读全文的前 30-50 篇专利。

    必须在 Map-Reduce 之前调用。不调用则成本翻倍。
    """
    selected = prescreen_patents(req.patent_numbers, max_select=req.max_patents)
    return {"selected_patent_numbers": selected, "total_input": len(req.patent_numbers)}


def _parse_json_safe_main(raw: str) -> dict:
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
    return {}


# ---------------------------------------------------------------------------
# 辅助
# ---------------------------------------------------------------------------

def _extract_keywords(voc: str) -> str:
    """从 VOC 粗提取检索关键词。

    简单策略：取 VOC 前 200 字符，去掉常见停用词，拼成关键词串。
    实际生产中可让 LLM 提取，但这里保持轻量。
    """
    # 中英文混合处理：英文取名词，中文直接用
    text = voc.strip()[:200]
    # 简单清理
    text = text.replace("\n", " ").replace("，", " ").replace("。", " ")
    return text


# ---------------------------------------------------------------------------
# 生产模式静态文件（必须在所有 API 路由之后挂载）
# 本地开发请用 Vite dev server + proxy，不要启用此模式
# ---------------------------------------------------------------------------
if os.environ.get("SERVE_STATIC", "0") == "1":
    # 优先用环境变量指定的路径（Docker/生产环境）
    dist_env = os.environ.get("FRONTEND_DIST", "")
    if dist_env:
        FRONTEND_DIST = Path(dist_env)
    else:
        # 本地开发回退：从 main.py 位置推算（..\..\frontend\dist）
        FRONTEND_DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"
    if FRONTEND_DIST.is_dir():
        print(f"[static] Mounting frontend from {FRONTEND_DIST}")
        app.mount("/", StaticFiles(directory=str(FRONTEND_DIST), html=True), name="frontend")
    else:
        print(f"[static] WARNING: SERVE_STATIC=1 but dist not found at {FRONTEND_DIST}")


if __name__ == "__main__":
    import uvicorn

    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8001"))
    uvicorn.run("main:app", host=host, port=port, reload=False)
