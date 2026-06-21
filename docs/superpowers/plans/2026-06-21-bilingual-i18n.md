# Bilingual App (EN/中文) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an EN/中文 language toggle to the FORGE AI webapp. All UI text switches languages. Generated reports (Word/PPTX/Markdown) follow the selected language.

**Architecture:** One translation file (`i18n.ts`) maps every UI string to `{en, zh}`. A `lang` state in `App.tsx` propagates to all components via props. Backend endpoints that generate content accept a `language` parameter. No new dependencies. No database.

**Tech Stack:** TypeScript (React 18), Python (FastAPI)

---

## File Map

| File | Role |
|------|------|
| `webapp/frontend/src/i18n.ts` | **New.** Every UI string in `{en, zh}` pairs. Single source of truth. |
| `webapp/frontend/src/App.tsx` | `lang` state + pass to all children + pass to Header |
| `webapp/frontend/src/components/Header.tsx` | Language toggle button (EN / 中文) |
| `webapp/frontend/src/components/InputStep.tsx` | All hardcoded Chinese → `T.xxx[lang]` |
| `webapp/frontend/src/components/ExploreStep.tsx` | All hardcoded English → `T.xxx[lang]` |
| `webapp/frontend/src/components/PatentsStep.tsx` | All hardcoded text → `T.xxx[lang]` |
| `webapp/frontend/src/components/ReportStep.tsx` | All hardcoded text → `T.xxx[lang]` |
| `webapp/frontend/src/components/DocumentStep.tsx` | All hardcoded text → `T.xxx[lang]` |
| `webapp/backend/main.py` | Add `language` to `GenerateRequest`, `ExportDocxRequest`, `ExportPptxRequest` |
| `webapp/backend/prompt_builder.py` | `build_system_prompt(lang)` — Chinese system prompt for `zh`, English for `en` |

---

### Task 1: Create Translation File

**Files:**
- Create: `webapp/frontend/src/i18n.ts`

- [ ] **Step 1: Write the translation file**

Create `webapp/frontend/src/i18n.ts`:

```typescript
export type Lang = 'en' | 'zh'

export const T = {
  // Header
  headerBack: { en: '← Back', zh: '← 返回' },
  headerHome: { en: '🏠', zh: '🏠' },
  headerTitle: { en: 'FORGE AI', zh: 'FORGE AI' },

  // Home page hero
  homeTitle: { en: 'FORGE AI', zh: 'FORGE AI' },
  homeTagline: { en: 'Revolutionize Your Innovation Process', zh: '革新您的创新流程' },
  homeDesc: {
    en: 'FORGE AI reads your research question, searches 6 global patent databases, deep-reads every patent (Abstract + Claims + Description), extracts X-Y relationships with evidence grading, maps competitors and white space, designs your 1st and 2nd DOE, and generates a complete R&D report — in minutes, not days.',
    zh: 'FORGE AI 读取您的研究问题，搜索 6 大全球专利数据库，逐篇深度阅读（摘要 + 权利要求 + 详细描述），以证据分级提取 X-Y 关系，绘制竞争格局和空白区域，设计第 1 和第 2 轮 DOE，并生成完整的 R&D 报告——几分钟，而不是几天。'
  },
  homeCap1: { en: '🌍 6-Source Patent Search', zh: '🌍 6 源专利检索' },
  homeCap2: { en: '🧬 X-Y Extraction', zh: '🧬 X-Y 关系抽取' },
  homeCap3: { en: '🎯 Competitor Intel', zh: '🎯 竞品情报' },
  homeCap4: { en: '🧪 DOE Design', zh: '🧪 DOE 实验设计' },
  homeCap5: { en: '📊 Auto-Generated Report', zh: '📊 自动生成报告' },

  // Entry cards
  entryCard1Title: { en: 'I have a research question', zh: '我有研究问题' },
  entryCard1Desc: { en: 'Enter your VOC and start the analysis pipeline', zh: '输入您的 VOC，启动分析流程' },
  entryCard2Title: { en: 'I need fresh ideas', zh: '我需要创新灵感' },
  entryCard2Desc: { en: 'AI generates research questions from your product and industry', zh: 'AI 根据您的产品和行业生成研究问题' },

  // VOC examples
  vocExamplesLabel: { en: 'Materials Science VOC Examples (12 random, click to try)', zh: '材料科学 VOC 示例（随机 12 个，点击试用）' },
  vocExamplesTag: { en: 'Examples', zh: '示例' },
  vocExamplesRefresh: { en: '↻ Refresh examples', zh: '↻ 换一批示例' },

  // VOC input
  vocLabel: { en: 'VOC', zh: 'VOC' },
  vocPlaceholder: {
    en: 'Describe the customer\'s material/product performance, process, and application requirements...',
    zh: '描述客户对材料/产品的性能、工艺、应用场景需求...'
  },
  vocAnalyzeBtn: {
    en: 'AI Generate Search Keywords →',
    zh: 'AI 生成检索关键词 →'
  },
  vocAnalyzing: {
    en: 'AI is analyzing VOC and generating keywords...',
    zh: 'AI 分析 VOC 生成检索关键词...'
  },

  // Clarify phase
  clarifyTitle: { en: 'Refine Your VOC', zh: '细化您的 VOC' },
  clarifySub: { en: 'Answer a few questions to make your research question more precise.', zh: '回答几个问题，让您的研究问题更精准。' },
  clarifyAnalysis: { en: 'AI Analysis', zh: 'AI 分析' },
  clarifyOriginalVOC: { en: 'Original VOC', zh: '原始 VOC' },
  clarifySubmit: { en: 'Submit Answers →', zh: '提交答案 →' },
  clarifyBack: { en: '← Back to VOC input', zh: '← 返回 VOC 输入' },
  clarifySkipping: { en: 'Skipping...', zh: '跳过中...' },
  clarifySkip: { en: 'Skip (use original VOC)', zh: '跳过（使用原始 VOC）' },

  // Enrich phase
  enrichTitle: { en: 'Enhanced VOC', zh: '增强版 VOC' },
  enrichSub: { en: 'Your VOC has been enriched with your answers. Edit if needed, then confirm.', zh: '以下是根据您的回答补充完善的 VOC，可编辑后确认。' },
  enrichChangesTitle: { en: 'Changes made:', zh: '本次补充/修正：' },
  enrichBack: { en: '← Back to answers', zh: '← 返回修改答案' },
  enrichConfirm: { en: 'Confirm, Generate Keywords →', zh: '确认，生成检索关键词 →' },

  // Keywords phase
  keywordsTitle: { en: 'Search Strategies', zh: '检索策略' },
  keywordsSub: { en: 'AI-generated search strategies. Edit or remove before searching.', zh: 'AI 生成的检索策略，可直接修改或删除后确认检索。' },
  keywordsAdd: { en: '+ Add custom strategy', zh: '+ 添加自定义策略' },
  keywordsBack: { en: '← Regenerate', zh: '← 重新生成' },
  keywordsSearch: { en: 'Confirm & Search Patents →', zh: '确认并检索专利 →' },
  keywordsSearching: { en: 'Searching patents...', zh: '检索专利中...' },

  // Patent count selector
  patentCountLabel: { en: 'Count', zh: '数量' },
  patentCountDesc: { en: 'Number of patents to retrieve', zh: '检索专利数量' },
  patentCountHint: { en: 'More patents = wider coverage, slightly longer search time. 20 is enough for most cases.', zh: '更多专利 = 更广的覆盖范围，但检索时间略长。默认 20 篇已足够大多数场景。' },

  // Explore phase
  exploreTitle: { en: 'Explore VOC Ideas', zh: '探索 VOC 创意' },
  exploreSub: {
    en: 'Describe your product and industry context. AI will generate 12 research questions — pick one to analyze.',
    zh: '描述您的产品和行业背景。AI 将生成 12 个研究问题——选一个来分析。'
  },
  exploreProductLabel: { en: 'Product', zh: '产品' },
  exploreProductPlaceholder: {
    en: 'e.g., UV-curable hard coats, Ti alloys for implants, PSA tapes for batteries...',
    zh: '例如：UV 固化硬质涂层、Ti 合金植入物、电池用 PSA 胶带...'
  },
  exploreContextLabel: { en: 'Context', zh: '背景' },
  exploreContextPlaceholder: {
    en: 'e.g., Our formulation yellows after 2 years. Competitor X launched a 5-year weatherable version.',
    zh: '例如：我们的配方 2 年后会发黄。竞争对手 X 推出了 5 年耐候版本。'
  },
  exploreDirectionLabel: { en: 'Direction', zh: '方向' },
  exploreDirAll: { en: 'All directions', zh: '所有方向' },
  exploreDirNextGen: { en: 'Next-gen performance', zh: '下一代性能' },
  exploreDirCostDown: { en: 'Cost-down', zh: '降本' },
  exploreDirAdjacent: { en: 'Adjacent markets', zh: '邻近市场' },
  exploreGenerate: { en: 'Generate 12 VOC Ideas →', zh: '生成 12 个 VOC 创意 →' },
  exploreGenerating: { en: 'AI is generating research ideas...', zh: 'AI 正在生成研究创意...' },
  exploreBack: { en: '← Back', zh: '← 返回' },
  exploreResultsTitle: {
    en: '12 Research Ideas for',
    zh: '12 个研究创意 —'
  },
  exploreResultsSub: {
    en: 'Click one to use it as your VOC and start analysis.',
    zh: '点击一个即可作为 VOC 开始分析。'
  },
  exploreRegenerate: { en: '🔄 Regenerate 12 Ideas', zh: '🔄 重新生成 12 个' },
  exploreTryDifferent: { en: '← Try a different product', zh: '← 换一个产品' },
  exploreErrorEmpty: {
    en: 'Please enter a product category',
    zh: '请输入产品类别'
  },

  // Patents page
  patentsTitle: { en: 'Confirm Selected Patents', zh: '确认入选专利' },
  patentsSub: {
    en: 'Found patents. Top 8 pre-selected. Check the ones to include in the report.',
    zh: '共检索到专利，已默认选择前 8 篇。请勾选要纳入报告的专利。'
  },
  patentsVocLabel: { en: 'VOC Summary', zh: 'VOC 摘要' },
  patentsStrategiesTitle: {
    en: 'AI decomposed into search angles:',
    zh: 'AI 从 VOC 拆解的搜索角度：'
  },
  patentsSelectTop8: { en: '⭐ Select Top 8 (Recommended)', zh: '⭐ 选前8篇（推荐）' },
  patentsTop8Selected: { en: '✅ Top 8 Selected', zh: '✅ 已选前8篇' },
  patentsSelectAll: { en: '☑ Select All', zh: '☑ 全选' },
  patentsAllSelected: { en: '✅ All Selected', zh: '✅ 已全选' },
  patentsClear: { en: '✕ Clear', zh: '✕ 清空' },
  patentsSelected: { en: 'Selected', zh: '已选' },
  patentsGenerate: { en: 'Generate Report', zh: '生成报告' },
  patentsBack: { en: '← Back to Edit VOC', zh: '← 返回修改 VOC' },
  patentsHome: { en: '🏠 Home', zh: '🏠 返回主页' },
  patentsSourceReal: { en: '✓ Real Search', zh: '✓ 真实检索' },
  patentsSourceAI: { en: '⚠ AI Generated · Unverified', zh: '⚠ AI生成·未核实' },
  patentsSourceUnknown: { en: 'Unknown Source', zh: '未知来源' },
  patentsViewOriginal: { en: 'View Original ↗', zh: '查看原文 ↗' },

  // Report page
  reportTitle: { en: 'R&D Intelligence Report', zh: 'R&D 智能报告' },
  reportBasedOn: { en: 'Based on', zh: '基于' },
  reportPatents: { en: 'patents', zh: '篇专利' },
  reportGenerating: { en: 'Generating...', zh: '生成中...' },
  reportDone: { en: 'Generation Complete', zh: '生成完成' },
  reportFailed: { en: 'Generation Failed', zh: '生成失败' },
  reportDownloadPpt: { en: 'Download PPT (AI-Designed)', zh: '下载 PPT (AI设计)' },
  reportDownloadWord: { en: 'Download Word', zh: '下载 Word' },
  reportDownloadMd: { en: 'Download .md', zh: '下载 .md' },
  reportBack: { en: '← Back to Patents', zh: '← 返回选专利' },
  reportHome: { en: '🏠 Home', zh: '🏠 返回主页' },
  reportLoading: { en: 'Calling DeepSeek to generate report, please wait...', zh: '正在调用 DeepSeek 生成报告，请稍候...' },
  reportLoadingHint: {
    en: 'Large prompt processing may take 1-3 minutes. Report will stream out paragraph by paragraph.',
    zh: '大 prompt 处理可能需要 1-3 分钟，报告将逐段流式输出。'
  },

  // Progress stages
  progressDetailSkipped: { en: 'Patent detail sources unreachable, using existing abstracts', zh: '专利详情源不可达，使用已有摘要' },
  progressDetail: { en: 'Fetching patent details', zh: '抓取专利详情' },
  progressLLMCalling: { en: 'Calling DeepSeek to generate report', zh: '调用 DeepSeek 生成报告' },

  // Document upload
  docTitle: { en: 'Upload a Document', zh: '上传文档' },
  docSub: { en: 'Upload a PDF or Word file for AI analysis.', zh: '上传 PDF 或 Word 文件，AI 将分析其中的技术内容。' },
  docDropText: { en: 'Drag & drop a PDF or Word file here', zh: '拖拽 PDF 或 Word 文件到此处' },
  docDropOr: { en: 'or', zh: '或' },
  docDropBrowse: { en: 'browse files', zh: '选择文件' },
  docDropFormats: { en: 'Supports PDF and Word (.docx) · Max 10MB', zh: '支持 PDF 和 Word (.docx) · 最大 10MB' },
  docRemove: { en: '✕ Remove', zh: '✕ 移除' },
  docUpload: { en: 'Upload & Analyze →', zh: '上传并分析 →' },
  docUploading: { en: 'Analyzing...', zh: '分析中...' },
  docAnalysisTitle: { en: 'AI Analysis Result', zh: 'AI 分析结果' },
  docBack: { en: '← Back', zh: '← 返回' },
  docHome: { en: '🏠 Home', zh: '🏠 返回主页' },

  // Generic
  errorBanner: { en: 'Error', zh: '错误' },
  spinner: { en: 'Loading...', zh: '加载中...' },

  // Step labels
  stepInput: { en: 'VOC Input', zh: 'VOC 输入' },
  stepPatents: { en: 'Patent Confirm', zh: '专利确认' },
  stepReport: { en: 'Report', zh: '报告生成' },
  stepDocument: { en: 'Document', zh: '文档上传' },
}

export type TranslationKey = keyof typeof T
```

- [ ] **Step 2: Verify TypeScript compiles**

Run: `cd webapp/frontend && npx tsc --noEmit`
Expected: no errors

- [ ] **Step 3: Commit**

```bash
git add webapp/frontend/src/i18n.ts
git commit -m "feat: add i18n translation file with all UI strings (EN/ZH)"
```

---

### Task 2: Add Language State to App + Header Toggle

**Files:**
- Modify: `webapp/frontend/src/App.tsx`
- Modify: `webapp/frontend/src/components/Header.tsx`

- [ ] **Step 1: Add `lang` state to App.tsx**

Read current `App.tsx`. Replace the state section (near the top):

```tsx
import { useState } from 'react'
import type { Step, SearchStrategy } from './types'
import type { Lang } from './i18n'
import InputStep from './components/InputStep'
import PatentsStep from './components/PatentsStep'
import ReportStep from './components/ReportStep'
import Header from './components/Header'
import './styles.css'

export default function App() {
  const [step, setStep] = useState<Step>('input')
  const [lang, setLang] = useState<Lang>('en')
  const [voc, setVoc] = useState('')
  ...
```

- [ ] **Step 2: Pass `lang`, `setLang` to Header**

Find `<Header step={step} ... />`. Replace with:

```tsx
<Header
  step={step}
  lang={lang}
  setLang={setLang}
  onBack={/* existing code unchanged */}
  onHome={/* existing code unchanged */}
/>
```

- [ ] **Step 3: Pass `lang` to all step components**

Add `lang={lang}` to every step component:

```tsx
<InputStep lang={lang} voc={voc} setVoc={setVoc} ... />
<PatentsStep lang={lang} ... />
<ReportStep lang={lang} ... />
<DocumentStep lang={lang} ... />
```

- [ ] **Step 4: Update Header to show language toggle**

Read current `Header.tsx`. Replace with:

```tsx
import type { Step } from '../types'
import type { Lang } from '../i18n'

export default function Header({
  step,
  lang,
  setLang,
  onBack,
  onHome,
}: {
  step: Step
  lang: Lang
  setLang: (l: Lang) => void
  onBack?: () => void
  onHome?: () => void
}) {
  // ... existing code ...

  return (
    <header className="header">
      <div className="header-inner">
        <div className="header-left">
          {/* existing back/home buttons */}
          ...
        </div>
        <nav className="steps">
          {/* existing steps */}
        </nav>
        <div className="header-lang">
          <button
            className={`header-lang-btn ${lang === 'en' ? 'active' : ''}`}
            onClick={() => setLang('en')}
          >
            EN
          </button>
          <button
            className={`header-lang-btn ${lang === 'zh' ? 'active' : ''}`}
            onClick={() => setLang('zh')}
          >
            中文
          </button>
        </div>
      </div>
    </header>
  )
}
```

- [ ] **Step 5: Add CSS for language toggle**

Append to `styles.css`:

```css
.header-lang {
  display: flex;
  gap: 2px;
  margin-left: auto;
}

.header-lang-btn {
  padding: 3px 8px;
  border: 1px solid var(--border);
  border-radius: 4px;
  font-size: 11px;
  color: var(--text-dim);
  transition: all 0.15s;
}
.header-lang-btn:hover {
  border-color: var(--accent);
  color: var(--text);
}
.header-lang-btn.active {
  border-color: var(--accent);
  color: var(--text);
  background: rgba(88,166,255,0.1);
}
```

- [ ] **Step 6: Verify build**

Run: `cd webapp/frontend && npx tsc --noEmit`
Expected: no errors (or only `lang` prop errors for components not yet updated — these are fixed in Tasks 3-4)

- [ ] **Step 7: Commit**

```bash
git add webapp/frontend/src/App.tsx webapp/frontend/src/components/Header.tsx webapp/frontend/src/styles.css
git commit -m "feat: add lang state to App + EN/中文 toggle in Header"
```

---

### Task 3: Internationalize All Components

**Files:**
- Modify: `webapp/frontend/src/components/InputStep.tsx`
- Modify: `webapp/frontend/src/components/ExploreStep.tsx`
- Modify: `webapp/frontend/src/components/PatentsStep.tsx`
- Modify: `webapp/frontend/src/components/ReportStep.tsx`
- Modify: `webapp/frontend/src/components/DocumentStep.tsx`

- [ ] **Step 1: Add `lang` prop and import `T` to every component**

Every component:
- Add `lang: Lang` to its props interface
- Import `{ T }` from `'../i18n'`
- Replace every hardcoded UI string with `T.xxx[lang]`

**InputStep.tsx changes:**

Add `lang,` to props destructuring. Replace strings:

| Old | New |
|-----|-----|
| `材料科学 VOC 示例（随机 12 个，点击试用）` | `T.vocExamplesLabel[lang]` |
| `示例` (tag) | `T.vocExamplesTag[lang]` |
| `↻ 换一批示例` | `T.vocExamplesRefresh[lang]` |
| `VOC` (label tag) | `T.vocLabel[lang]` |
| `描述客户对材料/产品的性能、工艺、应用场景需求...` | `T.vocPlaceholder[lang]` |
| `AI 生成检索关键词 →` | `T.vocAnalyzeBtn[lang]` |
| `AI 分析 VOC 生成检索关键词...` | `T.vocAnalyzing[lang]` |
| All home hero text | `T.homeTitle[lang]`, etc. |
| All entry card text | `T.entryCard1Title[lang]`, etc. |
| All clarify/enrich/keywords text | `T.clarifyTitle[lang]`, etc. |
| Patent count selector text | `T.patentCountLabel[lang]`, etc. |

**ExploreStep.tsx changes:**

| Old | New |
|-----|-----|
| `'Explore VOC Ideas'` | `T.exploreTitle[lang]` |
| `'Product Category'` | `T.exploreProductLabel[lang]` |
| All placeholder text | `T.exploreProductPlaceholder[lang]`, etc. |
| `'Generate 12 VOC Ideas →'` | `T.exploreGenerate[lang]` |
| `'AI is generating research ideas...'` | `T.exploreGenerating[lang]` |
| Results header/sub | `T.exploreResultsTitle[lang]`, etc. |
| Regenerate / back buttons | `T.exploreRegenerate[lang]`, etc. |
| Error messages | `T.exploreErrorEmpty[lang]` |

**PatentsStep.tsx changes:**

| Old | New |
|-----|-----|
| `'确认入选专利'` | `T.patentsTitle[lang]` |
| `'共检索到...'` | `T.patentsSub[lang]` |
| `'VOC 摘要:'` | `T.patentsVocLabel[lang]` |
| All button text (select, clear, etc.) | `T.patentsSelectTop8[lang]`, etc. |
| Source badges | `T.patentsSourceReal[lang]`, etc. |
| `'查看原文 ↗'` | `T.patentsViewOriginal[lang]` |

**ReportStep.tsx changes:**

| Old | New |
|-----|-----|
| `'R&D 智能报告'` | `T.reportTitle[lang]` |
| All status text | `T.reportGenerating[lang]`, etc. |
| Download button text | `T.reportDownloadPpt[lang]`, etc. |
| Back/Home buttons | `T.reportBack[lang]`, etc. |
| Progress stages | `T.progressDetailSkipped[lang]`, etc. |

**DocumentStep.tsx changes:**

| Old | New |
|-----|-----|
| All UI text | Corresponding `T.docXxx[lang]` keys |

- [ ] **Step 2: Verify build**

Run: `cd webapp/frontend && npx tsc --noEmit`
Expected: no errors

- [ ] **Step 3: Commit**

```bash
git add webapp/frontend/src/components/
git commit -m "feat: internationalize all components with i18n keys"
```

---

### Task 4: Backend — Pass Language to Report Generation

**Files:**
- Modify: `webapp/backend/main.py`
- Modify: `webapp/backend/prompt_builder.py`

- [ ] **Step 1: Add `language` to request models**

In `main.py`, update `GenerateRequest`, `ExportDocxRequest`, `ExportPptxRequest`:

```python
class GenerateRequest(BaseModel):
    voc: str
    patents: list[dict]
    fetch_details: bool = True
    doc_analysis: str | None = None
    language: str = "en"  # "en" or "zh"


class ExportDocxRequest(BaseModel):
    report: str
    filename: str | None = None
    title: str | None = None
    language: str = "en"


class ExportPptxRequest(BaseModel):
    report: str
    filename: str | None = None
    title: str | None = None
    language: str = "en"
```

- [ ] **Step 2: Pass language to prompt builder**

In `generate_report()`, pass `language` to `build_system_prompt`:

```python
system_prompt = build_system_prompt(req.language)
```

Also update `build_user_prompt` call if needed.

- [ ] **Step 3: Update prompt_builder.py**

Replace `build_system_prompt()` with language-aware version:

```python
def build_system_prompt(language: str = "en") -> str:
    if language == "zh":
        return (
            "# 你的角色\n\n"
            "你是一个 R&D 智能报告生成器..."
            # (existing Chinese system prompt)
            "- **保持输出语言一致**：用中文撰写报告正文，"
            "英文仅用于专有名词（如专利号、公司名、技术术语）"
        )
    else:
        return (
            "# Your Role\n\n"
            "You are an R&D intelligence report generator..."
            "- **Maintain consistent output language**: write the report in English, "
            "use Chinese/other languages only for proper nouns (patent numbers, company names, technical terms)"
        )
```

- [ ] **Step 4: Add English system prompt**

Write a proper English version of the system prompt:

```python
EN_SYSTEM_PROMPT = (
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
```

- [ ] **Step 5: Verify backend loads**

Run: `cd webapp/backend && python -c "from main import app; print('OK')"`
Expected: `OK`

- [ ] **Step 6: Commit**

```bash
git add webapp/backend/main.py webapp/backend/prompt_builder.py
git commit -m "feat: add language parameter to backend for bilingual reports"
```

---

### Task 5: End-to-End Verification

- [ ] **Step 1: Start backend + frontend**

```bash
# Terminal 1
cd webapp/backend && python main.py

# Terminal 2
cd webapp/frontend && npm run dev
```

- [ ] **Step 2: Test language toggle**

1. Open `http://localhost:5173` → page loads in English with `EN` highlighted
2. Click `中文` → all UI text switches to Chinese
3. Enter a VOC, go through the full pipeline
4. Generate a report → verify report language matches UI language

- [ ] **Step 3: Test bilingual report generation**

1. Switch to `EN` → generate report → verify report is in English
2. Switch to `中文` → generate report → verify report is in Chinese

- [ ] **Step 4: Commit any fixes**

```bash
git add -A
git commit -m "fix: bilingual QA fixes"
```
