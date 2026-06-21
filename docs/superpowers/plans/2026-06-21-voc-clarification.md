# VOC 澄清环节实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 VOC 输入和检索策略生成之间插入澄清环节：LLM 生成 3-5 道选择题 → 用户作答（可跳过）→ LLM 合并答案生成增强版 VOC → 用户确认后进入检索策略生成。

**Architecture:** 后端新增两个函数（`voc_analyzer.py` 的 `clarify_voc()` 和 `enrich_voc()`）+ 两个端点（`main.py` 的 `/api/clarify-voc` 和 `/api/enrich-voc`）。前端 `InputStep.tsx` 的 `phase` 状态机从 `'input' | 'keywords'` 扩展为 `'input' | 'clarify' | 'enriched' | 'keywords'`，新增两个阶段的 UI。

**Tech Stack:** Python 3.11+, FastAPI, Pydantic, React, TypeScript, DeepSeek API

---

## 文件结构

| 文件 | 责任 | 改动类型 |
|------|------|---------|
| `webapp/backend/voc_analyzer.py` | VOC 分析 | 修改：新增 `clarify_voc()` 和 `enrich_voc()` |
| `webapp/backend/main.py` | FastAPI 路由 | 修改：新增两个端点 + 数据模型 |
| `webapp/frontend/src/types.ts` | TS 类型 | 修改：新增 3 个接口 |
| `webapp/frontend/src/components/InputStep.tsx` | 输入页 | 修改：新增 clarify/enriched 两阶段 UI |
| `webapp/frontend/src/styles.css` | 样式 | 修改：新增选择题卡片等样式 |

---

## Task 1: 后端 — `voc_analyzer.py` 新增 `clarify_voc()` 和 `enrich_voc()`

**Files:**
- Modify: `d:\coding_is_fun\AI_CHEMIST_SKILL_2\webapp\backend\voc_analyzer.py`

- [ ] **Step 1: 在 `voc_analyzer.py` 末尾（`if __name__` 之前）新增两个函数**

在 `analyze_voc_to_strategies` 函数之后、`if __name__ == "__main__":` 之前，插入以下代码：

```python
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
            model=os.environ.get("DEEPSEEK_MODEL", "deepseek-chat"),
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=2048,
        )
        text = resp.choices[0].message.content.strip()
    except Exception as e:
        print(f"[clarify_voc] LLM 调用失败: {e}")
        return ClarifyResult(questions=[], analysis="")

    # JSON 解析（三重兜底）
    data: dict | None = None
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        m = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
        if m:
            try:
                data = json.loads(m.group(1))
            except json.JSONDecodeError:
                pass
        if data is None:
            m2 = re.search(r'\{.*\}', text, re.DOTALL)
            if m2:
                try:
                    data = json.loads(m2.group())
                except json.JSONDecodeError:
                    pass

    if not data or not isinstance(data, dict):
        print(f"[clarify_voc] JSON 解析失败, 原始返回: {text[:200]}")
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
            model=os.environ.get("DEEPSEEK_MODEL", "deepseek-chat"),
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=2048,
        )
        text = resp.choices[0].message.content.strip()
    except Exception as e:
        print(f"[enrich_voc] LLM 调用失败: {e}")
        # 降级：简单拼接
        return EnrichResult(
            enriched_voc=original_voc + "\n\n【澄清补充】\n" + qa_text,
            changes=["LLM 调用失败，已简单拼接答案"],
        )

    # JSON 解析（三重兜底）
    data: dict | None = None
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        m = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
        if m:
            try:
                data = json.loads(m.group(1))
            except json.JSONDecodeError:
                pass
        if data is None:
            m2 = re.search(r'\{.*\}', text, re.DOTALL)
            if m2:
                try:
                    data = json.loads(m2.group())
                except json.JSONDecodeError:
                    pass

    if not data or not isinstance(data, dict):
        print(f"[enrich_voc] JSON 解析失败, 原始返回: {text[:200]}")
        return EnrichResult(
            enriched_voc=original_voc + "\n\n【澄清补充】\n" + qa_text,
            changes=["LLM 返回解析失败，已简单拼接答案"],
        )

    enriched = (data.get("enriched_voc") or "").strip() or original_voc
    changes = [str(c).strip() for c in (data.get("changes") or []) if str(c).strip()]
    return EnrichResult(enriched_voc=enriched, changes=changes)
```

- [ ] **Step 2: 验证函数可导入**

运行：
```bash
python -c "from voc_analyzer import clarify_voc, enrich_voc, ClarifyQuestion, ClarifyResult, EnrichResult; print('import OK')"
```

预期输出：`import OK`

- [ ] **Step 3: 验证 `clarify_voc` 实际工作**

运行（需要 DEEPSEEK_API_KEY）：
```bash
python -c "from dotenv import load_dotenv; load_dotenv(); from voc_analyzer import clarify_voc; r = clarify_voc('锂电池胶带，要求耐高温耐电解液'); print(f'analysis: {r[\"analysis\"]}'); print(f'questions: {len(r[\"questions\"])}'); [print(f'  {q[\"id\"]}: {q[\"question\"]} -> {q[\"options\"]}') for q in r['questions']]"
```

预期输出：分析 1-2 句话 + 3-5 道选择题，每题 2-4 个选项。

---

## Task 2: 后端 — `main.py` 新增两个端点

**Files:**
- Modify: `d:\coding_is_fun\AI_CHEMIST_SKILL_2\webapp\backend\main.py`

- [ ] **Step 1: 修改 import 行**

定位到 `main.py` 第 40 行：
```python
from voc_analyzer import analyze_voc_to_strategies  # noqa: E402
```

改为：
```python
from voc_analyzer import (  # noqa: E402
    analyze_voc_to_strategies,
    clarify_voc,
    enrich_voc,
)
```

- [ ] **Step 2: 新增数据模型**

在 `AnalyzeVocRequest` 类定义之后（约第 67 行后），新增：

```python
class ClarifyVocRequest(BaseModel):
    voc: str
    num_questions: int = 4


class EnrichVocRequest(BaseModel):
    original_voc: str
    questions: list[dict]
    answers: dict[str, str]
```

- [ ] **Step 3: 新增 `/api/clarify-voc` 端点**

在 `/api/analyze-voc` 端点之后（约第 119 行后），新增：

```python
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
```

- [ ] **Step 4: 验证端点可访问**

确保后端已重启（--reload 会自动重载），运行：
```bash
python -c "import urllib.request, json; r = urllib.request.urlopen(urllib.request.Request('http://localhost:8001/api/clarify-voc', data=json.dumps({'voc':'锂电池胶带','num_questions':3}).encode(), headers={'Content-Type':'application/json'}), timeout=30); d = json.loads(r.read()); print(f'questions: {len(d[\"questions\"])}, analysis: {d[\"analysis\"][:50]}')"
```

预期输出：`questions: 3, analysis: ...`

---

## Task 3: 前端 — `types.ts` 新增接口

**Files:**
- Modify: `d:\coding_is_fun\AI_CHEMIST_SKILL_2\webapp\frontend\src\types.ts`

- [ ] **Step 1: 在 `types.ts` 末尾新增 3 个接口**

在文件末尾（`AnalyzeVocResponse` 接口之后）追加：

```typescript
/** 单道澄清问题 */
export interface ClarifyQuestion {
  id: string
  question: string
  options: string[]
  allow_custom: boolean
}

/** /api/clarify-voc 的响应 */
export interface ClarifyVocResponse {
  questions: ClarifyQuestion[]
  analysis: string
  warning?: string
}

/** /api/enrich-voc 的响应 */
export interface EnrichVocResponse {
  enriched_voc: string
  changes: string[]
}
```

- [ ] **Step 2: 验证类型无错误**

运行：
```bash
cd webapp/frontend && npx tsc --noEmit
```

预期：无错误（或只有与本次改动无关的已有错误）。

---

## Task 4: 前端 — `InputStep.tsx` 新增 clarify 和 enriched 阶段

**Files:**
- Modify: `d:\coding_is_fun\AI_CHEMIST_SKILL_2\webapp\frontend\src\components\InputStep.tsx`

这是最大的改动。分几个小步骤。

- [ ] **Step 1: 修改 import，新增类型导入**

定位到 `InputStep.tsx` 第 2 行：
```typescript
import type { Patent, SearchResponse, SearchStrategy, AnalyzeVocResponse } from '../types'
```

改为：
```typescript
import type { Patent, SearchResponse, SearchStrategy, AnalyzeVocResponse, ClarifyQuestion, ClarifyVocResponse, EnrichVocResponse } from '../types'
```

- [ ] **Step 2: 扩展 phase 状态机 + 新增 state**

定位到第 64 行附近：
```typescript
  // 阶段：'input' 输入VOC → 'keywords' AI生成关键词供确认 → 检索
  const [phase, setPhase] = useState<'input' | 'keywords'>('input')
  const [analyzing, setAnalyzing] = useState(false)
  const [searching, setSearching] = useState(false)
  const [error, setError] = useState('')
  const [strategies, setStrategies] = useState<SearchStrategy[]>([])
  const [patentNum, setPatentNum] = useState<number>(20)
  const [sampleVocs, setSampleVocs] = useState<string[]>(() => pickRandomVocs(VOC_POOL, 10))
```

改为：
```typescript
  // 阶段：'input' 输入VOC → 'clarify' 回答选择题 → 'enriched' 确认增强VOC → 'keywords' AI生成关键词供确认 → 检索
  const [phase, setPhase] = useState<'input' | 'clarify' | 'enriched' | 'keywords'>('input')
  const [analyzing, setAnalyzing] = useState(false)
  const [searching, setSearching] = useState(false)
  const [clarifying, setClarifying] = useState(false)
  const [enriching, setEnriching] = useState(false)
  const [error, setError] = useState('')
  const [strategies, setStrategies] = useState<SearchStrategy[]>([])
  const [patentNum, setPatentNum] = useState<number>(20)
  const [sampleVocs, setSampleVocs] = useState<string[]>(() => pickRandomVocs(VOC_POOL, 10))
  // 澄清环节状态
  const [clarifyQuestions, setClarifyQuestions] = useState<ClarifyQuestion[]>([])
  const [clarifyAnalysis, setClarifyAnalysis] = useState('')
  const [clarifyAnswers, setClarifyAnswers] = useState<Record<string, string>>({})
  const [enrichedVoc, setEnrichedVoc] = useState('')
  const [enrichChanges, setEnrichChanges] = useState<string[]>([])
```

- [ ] **Step 3: 新增 `handleClarify` 函数（触发澄清）**

在 `handleAnalyze` 函数之前（约第 72 行前），新增：

```typescript
  // 触发 VOC 澄清：调 /api/clarify-voc 生成选择题
  async function handleClarify() {
    if (!voc.trim()) {
      setError('请输入 VOC')
      return
    }
    setClarifying(true)
    setError('')
    try {
      const resp = await fetch('/api/clarify-voc', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ voc, num_questions: 4 }),
      })
      if (!resp.ok) throw new Error(`澄清失败: ${resp.status}`)
      const data: ClarifyVocResponse = await resp.json()
      if (data.questions.length === 0) {
        // 澄清失败，直接进入关键词生成
        setClarifying(false)
        handleAnalyze()
        return
      }
      setClarifyQuestions(data.questions)
      setClarifyAnalysis(data.analysis || '')
      setClarifyAnswers({})
      setPhase('clarify')
    } catch (e) {
      setError(e instanceof Error ? e.message : '澄清出错，已跳过')
      // 失败时直接进入关键词生成
      handleAnalyze()
    }
    setClarifying(false)
  }

  // 选择某题的某个选项
  function selectAnswer(qid: string, option: string) {
    setClarifyAnswers((prev) => ({ ...prev, [qid]: option }))
  }

  // 选择"以上都不是"并输入自定义答案
  function setCustomAnswer(qid: string, text: string) {
    setClarifyAnswers((prev) => ({ ...prev, [qid]: `custom:${text}` }))
  }

  // 提交澄清答案，生成增强 VOC
  async function handleEnrich() {
    setEnriching(true)
    setError('')
    try {
      const resp = await fetch('/api/enrich-voc', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          original_voc: voc,
          questions: clarifyQuestions,
          answers: clarifyAnswers,
        }),
      })
      if (!resp.ok) throw new Error(`增强失败: ${resp.status}`)
      const data: EnrichVocResponse = await resp.json()
      setEnrichedVoc(data.enriched_voc || voc)
      setEnrichChanges(data.changes || [])
      setPhase('enriched')
    } catch (e) {
      setError(e instanceof Error ? e.message : '增强出错')
      // 失败时用原 VOC 直接进入关键词生成
      handleAnalyze()
    }
    setEnriching(false)
  }

  // 确认增强 VOC，进入关键词生成
  function confirmEnriched() {
    setVoc(enrichedVoc)
    setPhase('keywords')
    // 自动触发关键词生成
    setTimeout(() => handleAnalyze(), 0)
  }

  // 从 enriched 返回 clarify 重新答
  function backToClarify() {
    setPhase('clarify')
  }
```

- [ ] **Step 4: 修改 `handleAnalyze` 使其可被内部调用**

定位到 `handleAnalyze` 函数（约第 73-109 行），把开头的 `if (!voc.trim())` 检查保留，但确保它不会在 `handleClarify` 失败时重复 setError。当前实现已 OK，无需改动。

- [ ] **Step 5: 修改"AI 生成检索关键词"按钮，改为先触发澄清**

定位到第 220-234 行：
```typescript
      {phase === 'input' && (
        <button
          className="primary-btn"
          onClick={handleAnalyze}
          disabled={analyzing}
        >
          {analyzing ? (
            <>
              <span className="spinner" /> AI 分析 VOC 生成检索关键词...
            </>
          ) : (
            'AI 生成检索关键词 →'
          )}
        </button>
      )}
```

改为：
```typescript
      {phase === 'input' && (
        <button
          className="primary-btn"
          onClick={handleClarify}
          disabled={clarifying || analyzing}
        >
          {clarifying ? (
            <>
              <span className="spinner" /> AI 分析 VOC 生成澄清问题...
            </>
          ) : analyzing ? (
            <>
              <span className="spinner" /> AI 分析 VOC 生成检索关键词...
            </>
          ) : (
            'AI 澄清 VOC →'
          )}
        </button>
      )}
```

- [ ] **Step 6: 新增 clarify 阶段 UI**

在 `keywords` 阶段的 `{/* 关键词确认/修改阶段 */}` 注释之前（约第 236 行前），插入：

```typescript
      {/* VOC 澄清阶段：回答选择题 */}
      {phase === 'clarify' && (
        <div className="clarify-panel">
          <div className="clarify-header">
            <h2 className="clarify-title">AI 发现以下信息需要明确</h2>
            {clarifyAnalysis && (
              <p className="clarify-analysis">{clarifyAnalysis}</p>
            )}
            <div className="clarify-original-voc">
              <span className="clarify-label">原始 VOC：</span>
              {voc}
            </div>
          </div>

          <div className="clarify-questions">
            {clarifyQuestions.map((q, qi) => (
              <div key={q.id} className="clarify-question-card">
                <div className="clarify-question-title">
                  {qi + 1}. {q.question}
                </div>
                <div className="clarify-options">
                  {q.options.map((opt) => (
                    <label key={opt} className="clarify-option">
                      <input
                        type="radio"
                        name={q.id}
                        checked={clarifyAnswers[q.id] === opt}
                        onChange={() => selectAnswer(q.id, opt)}
                      />
                      <span>{opt}</span>
                    </label>
                  ))}
                  {q.allow_custom && (
                    <label className="clarify-option">
                      <input
                        type="radio"
                        name={q.id}
                        checked={clarifyAnswers[q.id]?.startsWith('custom:') || false}
                        onChange={() => setCustomAnswer(q.id, '')}
                      />
                      <span>以上都不是</span>
                    </label>
                  )}
                  {q.allow_custom && clarifyAnswers[q.id]?.startsWith('custom:') && (
                    <input
                      type="text"
                      className="clarify-custom-input"
                      placeholder="请输入您的答案..."
                      value={clarifyAnswers[q.id].replace(/^custom:/, '')}
                      onChange={(e) => setCustomAnswer(q.id, e.target.value)}
                    />
                  )}
                </div>
              </div>
            ))}
          </div>

          {error && <div className="error-banner">{error}</div>}

          <div className="clarify-actions">
            <button
              className="ghost-btn"
              onClick={() => { setPhase('input') }}
              type="button"
            >
              ← 返回修改 VOC
            </button>
            <button
              className="ghost-btn"
              onClick={() => { handleAnalyze() }}
              type="button"
            >
              跳过澄清，直接生成关键词
            </button>
            <button
              className="primary-btn"
              onClick={handleEnrich}
              disabled={enriching}
            >
              {enriching ? (
                <>
                  <span className="spinner" /> 生成增强 VOC...
                </>
              ) : (
                '提交答案，生成增强 VOC →'
              )}
            </button>
          </div>
        </div>
      )}

      {/* 增强 VOC 确认阶段 */}
      {phase === 'enriched' && (
        <div className="enriched-panel">
          <div className="enriched-header">
            <h2 className="enriched-title">增强版 VOC</h2>
            <p className="enriched-hint">
              以下是根据您的回答补充完善的 VOC，可编辑后确认。
            </p>
          </div>

          {enrichChanges.length > 0 && (
            <div className="enrich-changes">
              <div className="enrich-changes-title">本次补充/修正：</div>
              <ul>
                {enrichChanges.map((c, i) => (
                  <li key={i}>✓ {c}</li>
                ))}
              </ul>
            </div>
          )}

          <textarea
            className="voc-input enriched-voc-input"
            value={enrichedVoc}
            onChange={(e) => setEnrichedVoc(e.target.value)}
            rows={10}
          />

          <div className="enriched-actions">
            <button className="ghost-btn" onClick={backToClarify} type="button">
              ← 返回修改答案
            </button>
            <button
              className="primary-btn"
              onClick={confirmEnriched}
              disabled={analyzing}
            >
              {analyzing ? (
                <>
                  <span className="spinner" /> AI 生成检索关键词...
                </>
              ) : (
                '确认，生成检索关键词 →'
              )}
            </button>
          </div>
        </div>
      )}
```

- [ ] **Step 7: 验证前端编译通过**

运行：
```bash
cd webapp/frontend && npx tsc --noEmit
```

预期：无新增错误。

---

## Task 5: 前端 — `styles.css` 新增样式

**Files:**
- Modify: `d:\coding_is_fun\AI_CHEMIST_SKILL_2\webapp\frontend\src\styles.css`

- [ ] **Step 1: 在 `styles.css` 末尾追加新样式**

```css
/* === VOC 澄清环节 === */
.clarify-panel {
  margin-top: 24px;
}

.clarify-header {
  margin-bottom: 20px;
}

.clarify-title {
  font-size: 20px;
  font-weight: 600;
  margin: 0 0 8px 0;
  color: var(--text-primary, #1a1a1a);
}

.clarify-analysis {
  font-size: 14px;
  color: var(--text-secondary, #666);
  margin: 0 0 12px 0;
  padding: 10px 14px;
  background: var(--bg-secondary, #f5f5f5);
  border-left: 3px solid var(--accent, #2E5C8A);
  border-radius: 4px;
}

.clarify-original-voc {
  font-size: 13px;
  color: var(--text-tertiary, #999);
  padding: 10px 14px;
  background: var(--bg-tertiary, #fafafa);
  border-radius: 6px;
  line-height: 1.6;
}

.clarify-label {
  font-weight: 600;
  color: var(--text-secondary, #666);
}

.clarify-questions {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 20px;
}

.clarify-question-card {
  padding: 16px 18px;
  background: var(--bg-secondary, #f9f9f9);
  border: 1px solid var(--border, #e5e5e5);
  border-radius: 8px;
}

.clarify-question-title {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 12px;
  color: var(--text-primary, #1a1a1a);
}

.clarify-options {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.clarify-option {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.15s;
}

.clarify-option:hover {
  background: var(--bg-hover, #f0f0f0);
}

.clarify-option input[type="radio"] {
  cursor: pointer;
  accent-color: var(--accent, #2E5C8A);
}

.clarify-custom-input {
  margin-top: 4px;
  margin-left: 26px;
  padding: 8px 10px;
  border: 1px solid var(--border, #d5d5d5);
  border-radius: 6px;
  font-size: 14px;
  font-family: inherit;
  width: calc(100% - 26px);
}

.clarify-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  align-items: center;
}

/* === 增强 VOC 确认 === */
.enriched-panel {
  margin-top: 24px;
}

.enriched-header {
  margin-bottom: 16px;
}

.enriched-title {
  font-size: 20px;
  font-weight: 600;
  margin: 0 0 6px 0;
  color: var(--text-primary, #1a1a1a);
}

.enriched-hint {
  font-size: 14px;
  color: var(--text-secondary, #666);
  margin: 0;
}

.enrich-changes {
  margin-bottom: 16px;
  padding: 12px 16px;
  background: var(--bg-success, #f0fdf4);
  border: 1px solid var(--border-success, #bbf7d0);
  border-radius: 8px;
}

.enrich-changes-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-success, #15803d);
  margin-bottom: 6px;
}

.enrich-changes ul {
  margin: 0;
  padding-left: 20px;
  font-size: 13px;
  color: var(--text-success, #15803d);
  line-height: 1.7;
}

.enriched-voc-input {
  font-size: 14px;
  line-height: 1.7;
  min-height: 200px;
}

.enriched-actions {
  display: flex;
  gap: 12px;
  margin-top: 16px;
  align-items: center;
}
```

- [ ] **Step 2: 验证样式无语法错误**

运行：
```bash
cd webapp/frontend && npx tsc --noEmit
```

预期：无错误（CSS 不参与 TS 检查，但确保没有破坏构建）。

---

## Task 6: 端到端验证

**Files:** 无文件改动，仅验证

- [ ] **Step 1: 确保后端和前端服务在运行**

后端：`http://localhost:8001`（uvicorn --reload 会自动重载）
前端：`http://localhost:5173`（vite 会自动热重载）

- [ ] **Step 2: 验证 `/api/clarify-voc` 端点**

运行：
```bash
python -c "import urllib.request, json; req = urllib.request.Request('http://localhost:8001/api/clarify-voc', data=json.dumps({'voc':'锂电池胶带，要求耐高温耐电解液','num_questions':3}).encode(), headers={'Content-Type':'application/json'}); r = urllib.request.urlopen(req, timeout=30); d = json.loads(r.read()); print(f'questions: {len(d[\"questions\"])}'); print(f'analysis: {d[\"analysis\"]}'); [print(f'  {q[\"id\"]}: {q[\"question\"]} -> {q[\"options\"]}') for q in d['questions']]"
```

预期：返回 3 道选择题 + 分析文本。

- [ ] **Step 3: 验证 `/api/enrich-voc` 端点**

运行（用上一步的问题和模拟答案）：
```bash
python -c "import urllib.request, json; req = urllib.request.Request('http://localhost:8001/api/enrich-voc', data=json.dumps({'original_voc':'锂电池胶带，要求耐高温耐电解液','questions':[{'id':'q1','question':'应用场景','options':['动力电池','储能电池']}],'answers':{'q1':'动力电池'}}).encode(), headers={'Content-Type':'application/json'}); r = urllib.request.urlopen(req, timeout=30); d = json.loads(r.read()); print(f'enriched: {d[\"enriched_voc\"][:200]}'); print(f'changes: {d[\"changes\"]}')"
```

预期：返回增强版 VOC（含"动力电池"信息）+ 变更摘要。

- [ ] **Step 4: 前端手动验证**

打开 http://localhost:5173，输入一个模糊 VOC（如"锂电池胶带"），点击"AI 澄清 VOC"按钮：
1. 应看到 3-5 道选择题
2. 选择答案后点"提交答案，生成增强 VOC"
3. 应看到增强版 VOC + 变更摘要
4. 点"确认，生成检索关键词"应进入关键词确认阶段
5. 测试"跳过澄清，直接生成关键词"应直接进入关键词阶段
6. 测试"返回修改 VOC"应回到输入阶段

- [ ] **Step 5: 验证降级**

临时停止后端（Ctrl+C），在前端点"AI 澄清 VOC"：
- 应显示错误提示
- 应自动跳过到关键词生成阶段（用原 VOC）

---

## 完成标准

- [ ] `/api/clarify-voc` 返回 3-5 道有意义的选择题
- [ ] `/api/enrich-voc` 返回包含答案信息的增强版 VOC
- [ ] 前端 input → clarify → enriched → keywords 流程跑通
- [ ] "跳过澄清"按钮直接进入 keywords 阶段
- [ ] LLM 失败时降级到用原 VOC
- [ ] 无 TypeScript 编译错误
