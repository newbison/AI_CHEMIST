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
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
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
from docx_export import markdown_to_docx  # noqa: E402
from pptx_export import markdown_to_pptx, markdown_to_pptx_designed  # noqa: E402
from ppt_designer import design_ppt_slides_safe  # noqa: E402
from voc_analyzer import analyze_voc_to_strategies  # noqa: E402

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


class GenerateRequest(BaseModel):
    voc: str
    patents: list[dict]  # 用户确认的入选专利列表
    fetch_details: bool = True  # 是否抓取每篇专利详情


class ExportDocxRequest(BaseModel):
    report: str  # Markdown 格式的报告文本
    filename: str | None = None
    title: str | None = None


class ExportPptxRequest(BaseModel):
    report: str  # Markdown 格式的报告文本
    filename: str | None = None
    title: str | None = None


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
        patents = search_by_strategies(strategies, num_per_angle=8, total=req.num)
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
    system_prompt = build_system_prompt()

    def event_stream():
        # 先推送元信息 —— 让前端立即建立连接、显示进度
        yield f"data: {json.dumps({'type': 'meta', 'patent_count': len(patents)})}\n\n"

        # 用独立局部变量承载（可能被详情补全替换），避免对闭包变量赋值导致 UnboundLocalError
        working_patents = patents

        # 可选：抓取每篇专利详情（带可达性预检，避免不可达时整段同步卡死）
        if req.fetch_details:
            reachable = _patents_source_reachable()
            if not reachable:
                yield f"data: {json.dumps({'type': 'progress', 'stage': 'detail_skipped', 'reason': 'patents.google.com 不可达，使用已有摘要继续生成'})}\n\n"
            else:
                enriched: list[dict] = []
                for i, p in enumerate(patents, 1):
                    num = p.get("patent_number", "")
                    detail = ""
                    if num:
                        detail = fetch_patent_detail(num)
                    if detail:
                        p = {**p, "detail_text": detail}
                    enriched.append(p)
                    yield f"data: {json.dumps({'type': 'progress', 'stage': 'detail', 'index': i, 'total': len(patents), 'patent_number': num, 'ok': bool(detail)})}\n\n"
                working_patents = enriched

        user_prompt = build_user_prompt(req.voc, working_patents)

        # 通知前端：即将调用 LLM（首 token 可能需要 20-60 秒，让前端知道在处理）
        prompt_size = len(system_prompt) + len(user_prompt)
        yield f"data: {json.dumps({'type': 'progress', 'stage': 'llm_calling', 'prompt_size': prompt_size})}\n\n"

        # 流式推送报告内容
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


@app.post("/api/export-docx")
def export_docx(req: ExportDocxRequest):
    """把 Markdown 报告转成 Word (.docx) 文件下载。"""
    from fastapi.responses import Response

    docx_bytes = markdown_to_docx(req.report, title=req.title)
    filename = req.filename or f"rd-report-{__import__('datetime').datetime.now().strftime('%Y%m%d')}.docx"

    return Response(
        content=docx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.post("/api/export-pptx")
def export_pptx(req: ExportPptxRequest):
    """把 Markdown 报告转成 PowerPoint (.pptx) 文件下载。

    流程：先调用 DeepSeek 读取 ppt-design-skill 生成设计方案 JSON，
    再按设计方案渲染美化版 PPT。若 LLM 设计失败，回退到普通模板渲染。
    """
    from fastapi.responses import Response

    # 阶段1：LLM 设计
    design_plan = design_ppt_slides_safe(req.report)
    designed_bytes = markdown_to_pptx_designed(design_plan, title=req.title)

    # 阶段2：渲染（设计方案有效用美化版，否则回退普通版）
    if designed_bytes:
        pptx_bytes = designed_bytes
    else:
        pptx_bytes = markdown_to_pptx(req.report, title=req.title)

    filename = req.filename or f"rd-report-{__import__('datetime').datetime.now().strftime('%Y%m%d')}.pptx"

    return Response(
        content=pptx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ---------------------------------------------------------------------------
# 辅助
# ---------------------------------------------------------------------------

def _patents_source_reachable(timeout: float = 4.0) -> bool:
    """快速预检 patents.google.com 是否可达。

    在网络受限环境（如本机）下 Google Patents 不可达，逐篇抓取会串行卡满
    N×12s 超时、且发生在 SSE 首字节之前，导致前端"一直生成中"。
    预检失败则跳过详情抓取，直接用检索阶段已有的摘要生成报告。
    """
    import httpx
    try:
        with httpx.Client(
            headers={"User-Agent": "Mozilla/5.0", "Accept": "*/*"},
            timeout=timeout,
        ) as client:
            resp = client.head("https://patents.google.com/", follow_redirects=True)
            return resp.status_code < 500
    except Exception:
        return False


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
# ---------------------------------------------------------------------------
FRONTEND_DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"
if FRONTEND_DIST.is_dir():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIST), html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn

    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8001"))
    uvicorn.run("main:app", host=host, port=port, reload=False)
