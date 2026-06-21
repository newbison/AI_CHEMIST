# VOC 澄清环节：单轮选择题 + 增强版 VOC

**日期**: 2026-06-21
**状态**: 已批准，待实施
**方案**: A（单轮澄清 + 增强版 VOC）

## 问题陈述

用户输入 VOC 时经常信息不充分甚至有矛盾（如"耐高温"但没给温度、"耐电解液"但没说电解液成分）。当前系统直接用原始 VOC 生成检索策略，导致：
1. 检索策略基于模糊信息，精准度不足
2. 后续报告的 CTQ 矩阵、DOE 设计缺乏关键约束数值
3. 用户对自己 VOC 的问题无感知

## 解决方案

在 VOC 输入和检索策略生成之间，插入一个澄清环节：
1. LLM 分析 VOC，找出信息缺口和矛盾，生成 3-5 道单选题
2. 用户作答（可跳过）
3. LLM 合并答案生成增强版 VOC
4. 用户确认增强版 VOC 后，进入检索策略生成

## 设计细节

### 1. 用户流程

```
输入 VOC
  ↓ [AI 澄清 VOC]
回答 3-5 道选择题（可跳过）
  ↓ [提交答案]
确认增强版 VOC（可编辑）
  ↓ [确认并生成关键词]
确认搜索策略（现有流程）
  ↓ [确认并检索]
专利列表
```

前端 `phase` 状态机从 `'input' | 'keywords'` 扩展为 `'input' | 'clarify' | 'enriched' | 'keywords'`。

### 2. 后端 API

#### `POST /api/clarify-voc` — 生成澄清问题

**请求**:
```python
class ClarifyVocRequest(BaseModel):
    voc: str
    num_questions: int = 4  # 默认 4，范围 3-5
```

**响应**:
```python
class ClarifyQuestion(BaseModel):
    id: str               # "q1", "q2", ...
    question: str         # "该胶带的目标应用场景是？"
    options: list[str]    # ["动力电池电芯", "储能电池", "消费电子"]
    allow_custom: bool    # True = 允许"以上都不是"+自定义输入

class ClarifyVocResponse(BaseModel):
    questions: list[ClarifyQuestion]
    analysis: str         # LLM 对 VOC 的简要分析（发现的缺口/矛盾）
```

**LLM Prompt**（生成问题）:
```
你是材料科学研发需求分析专家。分析下面的客户需求(VOC)，找出信息缺口和潜在矛盾，
生成 {num_questions} 道单选题帮助用户明确需求。

VOC:
{voc}

要求：
1. 聚焦最关键的信息缺口：应用场景、性能指标数值、约束条件、目标基材/体系、失效机理
2. 每题 2-4 个选项，选项要具体（如"85°C/72h"而非"高温"）
3. 选项要覆盖常见情况，避免都能选/都不能选
4. 不要问 VOC 里已经明确的信息
5. 如发现 VOC 里有矛盾（如"耐高温"但没给温度），优先问矛盾点

只返回 JSON：
{
  "analysis": "对 VOC 的简要分析（发现的缺口/矛盾，1-2句话）",
  "questions": [
    {"id": "q1", "question": "题干", "options": ["选项A", "选项B", "选项C"], "allow_custom": true}
  ]
}
```

**调用参数**: `temperature=0.3, max_tokens=2048`（需要一定创造性但不要发散）

#### `POST /api/enrich-voc` — 根据答案生成增强版 VOC

**请求**:
```python
class EnrichVocRequest(BaseModel):
    original_voc: str
    questions: list[dict]     # 原问题列表（含 id/question/options）
    answers: dict[str, str]   # {q1: "动力电池电芯", q2: "custom:85°C/72h"}
```

**响应**:
```python
class EnrichVocResponse(BaseModel):
    enriched_voc: str     # 合并后的增强版 VOC
    changes: list[str]    # ["补充了应用场景：动力电池电芯", "明确了温度范围：85°C/72h"]
```

**LLM Prompt**（生成增强 VOC）:
```
你是材料科学研发需求分析专家。根据用户的原始 VOC 和澄清答案，生成一个增强版 VOC。

原始 VOC:
{original_voc}

澄清问答:
Q1: {question}
A1: {answer}
...

要求：
1. 保留原始 VOC 的所有信息
2. 把答案中的新信息自然融入（不要简单拼接）
3. 用专业但清晰的语言重写，结构化呈现（产品/材料/性能/约束/目标）
4. 标注哪些是新增信息（用【补充】前缀）
5. 如发现答案与原 VOC 矛盾，以答案为准并标注【修正】

只返回 JSON：
{
  "enriched_voc": "增强版 VOC 全文",
  "changes": ["补充了应用场景：动力电池电芯", "明确了温度范围：85°C/72h"]
}
```

**调用参数**: `temperature=0.2, max_tokens=2048`（忠实合并，不要发挥）

### 3. 前端 UI

#### clarify 阶段

- 顶部：原 VOC 只读展示（灰色背景）
- 中部：LLM 分析摘要（1-2 句话，提示发现了哪些缺口）
- 主体：3-5 道选择题卡片，每题：
  - 题干
  - 2-4 个单选选项（radio button）
  - "以上都不是"选项 + 可选文本框（当 `allow_custom=true` 时显示）
- 底部按钮：
  - "跳过澄清，直接生成关键词"（次要按钮，ghost 样式）
  - "提交答案，生成增强 VOC"（主要按钮）

#### enriched 阶段

- 顶部：原 VOC 只读展示（灰色背景，小字）
- 中部：变更摘要（`changes` 列表，绿色 ✓ 图标）
- 主体：增强版 VOC 文本框（可编辑）
- 底部按钮：
  - "返回修改答案"（次要按钮）
  - "确认，生成关键词"（主要按钮）

### 4. 降级策略

- `/api/clarify-voc` 失败（LLM 报错/超时）→ 前端显示提示"澄清服务暂时不可用，直接生成关键词"，自动跳过到 keywords 阶段（用原 VOC）
- `/api/enrich-voc` 失败 → 用原 VOC + 答案简单拼接作为增强 VOC（前端本地处理：`原VOC + "\n\n澄清补充：\n" + 答案列表`）
- 用户点"跳过澄清" → 直接用原 VOC 进入 keywords 阶段
- LLM 返回的 JSON 解析失败 → 同上降级

### 5. 数据模型

#### 前端 types.ts 新增

```typescript
export interface ClarifyQuestion {
  id: string
  question: string
  options: string[]
  allow_custom: boolean
}

export interface ClarifyVocResponse {
  questions: ClarifyQuestion[]
  analysis: string
}

export interface EnrichVocResponse {
  enriched_voc: string
  changes: string[]
}
```

### 6. 改动范围

| 文件 | 改动 |
|------|------|
| `webapp/backend/voc_analyzer.py` | 新增 `clarify_voc()` 和 `enrich_voc()` 两个函数 |
| `webapp/backend/main.py` | 新增 `/api/clarify-voc` 和 `/api/enrich-voc` 两个端点 + 数据模型 |
| `webapp/frontend/src/types.ts` | 新增 `ClarifyQuestion`、`ClarifyVocResponse`、`EnrichVocResponse` 接口 |
| `webapp/frontend/src/components/InputStep.tsx` | 新增 `clarify` 和 `enriched` 两个阶段 + 相关 UI |
| `webapp/frontend/src/styles.css` | 新增选择题卡片、变更摘要等样式 |

### 7. 不在本次范围

- 多轮对话式澄清（方案 B）
- VOC 质量评分
- VOC 模板保存/加载
- 历史记录
- VOC 文件上传

## 验证方案

1. **clarify-voc 端点**：输入模糊 VOC（如"锂电池胶带"），确认返回 3-5 道有意义的选择题
2. **enrich-voc 端点**：输入 VOC + 答案，确认返回的增强 VOC 包含答案信息且标注【补充】
3. **降级**：临时禁用 LLM，确认前端跳过澄清直接进入 keywords
4. **跳过**：点"跳过澄清"，确认直接用原 VOC 进入 keywords
5. **端到端**：完整跑一遍 input → clarify → enriched → keywords → search 流程

## 风险

- **LLM 问题质量**：问题可能太泛或与 VOC 无关。通过 prompt 约束 + 选项具体化要求缓解
- **增强 VOC 偏离原意**：LLM 可能过度改写。通过 `temperature=0.2` + "保留原始 VOC 所有信息"约束
- **延迟**：两次额外 LLM 调用（clarify ~3s + enrich ~3s），总共增加 ~6s。可接受
