# 上传文档分析功能设计

## 需求概述

在专利分析流程中，允许用户上传 PDF/Word 文件作为背景参考资料。系统自动提取文本、调用 LLM 生成技术分析，分析结果自动注入报告的"研究背景"章节，无需用户二次确认。

## 用户流程

```
主页
  ↓
VOC 输入 → AI 澄清 → 生成关键词（现有流程）
  ↓
专利检索 → 确认入选专利（现有流程）
  ↓
【新增】上传文档分析（可选，可跳过）
  ↓
生成报告（分析结果自动融入报告）
```

## 技术方案

### 后端

#### 1. 新增 `doc_analyzer.py` 模块

**依赖**：`pdfplumber`（需添加到 requirements.txt）

**函数**：
- `extract_text_from_pdf(file_bytes) -> str`：提取 PDF 文本
- `extract_text_from_docx(file_bytes) -> str`：提取 Word 文本
- `analyze_document(text: str, doc_name: str) -> str`：调用 DeepSeek LLM 生成通用技术文档分析

**LLM 分析 prompt**：
```
你是一个技术文档分析专家。请对以下文档进行深度分析，提取并总结：

1. **技术要点**：文档涉及的核心技术/材料/工艺
2. **应用场景**：文档描述的应用领域和使用条件
3. **主要结论**：文档的主要发现、结论或技术效果
4. **关键数据**：具体的技术参数、数值、配方范围（如有）
5. **创新点**：与现有技术相比的独特之处（如有）

请用中文回答，结构清晰，数据具体。不要泛泛而谈。
```

#### 2. 新增 API 端点

**`POST /api/upload-doc`**
- 请求：`multipart/form-data`（`file`: 文件，`doc_name`: 文件名，可选）
- 响应：`{"analysis": str, "doc_name": str, "text_preview": str}`
- 文件大小限制：10MB
- 支持格式：`.pdf`, `.docx`

**`POST /api/generate`** 修改
- 请求新增可选字段：`doc_analysis: str | None`
- 分析结果拼接到 user prompt 的"研究背景"章节前

#### 3. 修改 `prompt_builder.py`

```python
def build_user_prompt(
    voc: str,
    patents: list[dict],
    doc_analysis: str | None = None  # 新增
) -> str:
    # 在 VOC 之后、专利之前插入：
    if doc_analysis:
        parts.append(f"# 用户上传的参考资料分析\n\n{doc_analysis}\n")
```

### 前端

#### 1. 新增 `DocumentStep.tsx` 组件

**UI 元素**：
- 文件上传区（拖拽 + 点击上传）
- 支持 PDF/DOCX，显示文件大小和名称
- 上传后显示"正在分析..."状态
- 分析完成后显示结果预览（可折叠展开）
- 底部按钮：「跳过此步」→「确认并继续生成报告」

**状态**：
- `uploading`: boolean
- `analyzing`: boolean
- `analysis`: string | null
- `error`: string | null

#### 2. 修改 `App.tsx`

新增 state：
```typescript
const [docAnalysis, setDocAnalysis] = useState<string | null>(null)
```

流程调整：确认专利 → DocumentStep（可跳过）→ 生成报告

#### 3. 修改 `types.ts`

```typescript
export interface UploadDocResponse {
  analysis: string
  doc_name: string
  text_preview: string
}
```

### 错误处理

- **文件过大**：返回 413 错误，提示"文件超过 10MB 限制"
- **格式不支持**：返回 400 错误，提示"仅支持 PDF 和 Word 文件"
- **文本提取失败**：返回分析失败，提示用户尝试其他文件
- **LLM 分析失败**：返回错误，允许用户跳过此步

### 降级策略

- 文本提取失败 → 提示用户，询问是否跳过
- LLM 分析失败 → 提示用户，询问是否跳过
- 用户始终可选择跳过，不阻塞主流程

## 文件变更清单

| 文件 | 变更 |
|------|------|
| `requirements.txt` | 添加 `pdfplumber>=0.10.0` |
| `doc_analyzer.py` | 新增（文本提取 + LLM 分析） |
| `main.py` | 新增 `/api/upload-doc` 端点，修改 `/api/generate` |
| `prompt_builder.py` | `build_user_prompt()` 新增 `doc_analysis` 参数 |
| `DocumentStep.tsx` | 新增（文件上传 + 分析组件） |
| `App.tsx` | 新增 state 和流程节点 |
| `types.ts` | 新增 `UploadDocResponse` 接口 |
| `styles.css` | 新增 DocumentStep 样式 |

## 实施顺序

1. 添加依赖，安装 pdfplumber
2. 后端：doc_analyzer.py + 端点 + prompt_builder 修改
3. 前端：types.ts + DocumentStep.tsx + App.tsx + styles.css
4. 端到端测试
