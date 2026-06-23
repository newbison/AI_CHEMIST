# Changelog

## [v2.0] — 2026-06-23

### 🚀 Model Upgrade: deepseek-chat (V3) → deepseek-v4-pro

- **`deepseek-chat` deprecated 2026-07-24** — preemptive migration to `deepseek-v4-pro`
- 1M context window (8× V3's 128K), 384K max output tokens (47× V3's 8K)
- All 17 model references across 8 backend files updated
- `MAX_TOKENS_PER_CALL`: 8192 → 65536
- Added `extra_body={"thinking": {"type": "disabled"}}` to all 10 `response_format`/ChatCompletion sites — V4 Pro's default thinking mode contaminates structured JSON/code output

### ✨ VOC Scout + Deep Search System

- **VOC Scout** (`voc_scout.py` + `ScoutStep.tsx`): interactive 2-3 round tech landscape exploration
  - Market share search before patent search (bilingual CN/EN)
  - Confidence scoring (★★★/★★☆/★☆☆), contradiction detection, source labeling ([P]/[T]/[A]/[C]/[D]/[E])
- **Deep Search** (`deep_search.py`): Map-Reduce patent analysis pipeline
  - Pre-screen → 10-way parallel Map → Reduce
  - 3-pass iterative search: company-targeted → keyword+IPC sweep → new-term re-search
  - Convergence detection, FTO assessment, CTQ comparison table
  - Pre-screen: expanded from "last 5 years" → "from 2000 onwards" (expired patents are valuable, zero FTO risk)
- **SSE real-time progress**: per-patent progress streaming during Map-Reduce (`/api/deep-search/map-reduce`)
- New API endpoints: `/api/voc-scout/round1`, `/round2`, `/output`; `/api/deep-search/start`, `/prescreen`, `/map-reduce`

### 🤖 Report Auto-Continuation

- `llm_client.py`: detects `finish_reason="length"` on streaming chunks, auto-sends continuation requests
- Up to 3 continuations chained until natural stop — fixes reports truncating at ~section 7/18
- Seamless to end users (continuation pause ~5-10s between calls)

### 🧪 DOE: 1 Round → 2-3 Rounds

- System prompt (`prompt_builder.py`): mandatory multi-round DOE structure
  - Round 1: Factor Screening (fractional factorial, narrow 5-10 X → 2-4 dominant levers)
  - Round 2: Response Surface Optimization (CCD/Box-Behnken, find optimal formulation window)
  - Round 3: Confirmation Run (3-5 replicates at optimum, verify predictions)
- Report template (`final_report_template.md`): 18 → 19 sections with dedicated DOE round details
- Workflow (`07_experiment_portfolio.md`): multi-round DOE structure documented

### 📄 Patent Text Extraction: Increased Limits

- Abstract: 2,000 → **unlimited** (full text)
- Claims: 4,000 → **8,000** chars
- Description: 6,000 → **16,000** chars
- Inventors: 10 → **20** names
- V3 limits were a context-window constraint; V4 Pro's 1M window removes the need for aggressive truncation

### 🎨 PPT Export Fix

- `ppt_designer.py`: added `extra_body={"thinking": {"type": "disabled"}}` — thinking tokens were corrupting PptxGenJS code generation
- `max_tokens`: 16384 → 32768 (larger scripts for multi-slide decks)
- Fixed duplicate `writeFile` check in validation

### 📁 Report Filename: Project Name

- Downloads now use report title/VOC as filename (e.g. `PVDF粘结剂专利分析报告_2026-06-23.pptx`)
- Backend: RFC 5987 `Content-Disposition` encoding for Chinese filenames (fixes `UnicodeEncodeError` on latin-1)

### 🎨 UI Improvements

- VOC examples: 12 random → 6 random, bigger cards (12px→14px font, 3-column grid, 5-line preview)
- VOC language sync: examples re-pick from pool when UI language changes
- CTQ button: shows patent count inline, clear message when no patents available
- Dark-theme CSS variables for ScoutStep

### 📚 Documentation

- README.md: VOC Scout, Deep Search, API endpoints, V4 Pro badges, updated project structure
- `docs/specs/voc-scout-spec.md`: full 18-section specification
- `CHANGELOG.md`: this file

---

## [v1.x] — 2026-06-20 and earlier

See git history for pre-V4 changes including:
- 6-level patent search fallback (Google Patents → USPTO → EPO → WIPO → Scholar → CN → LLM → Cache)
- PptxGenJS PPT export pipeline
- SPC Platform integration (closed-loop R&D: FORGE AI → DOE → SPC analysis → FORGE AI refinement)
- 9-step R&D intelligence workflow
- X-Y extraction skill with evidence grading
