# 上传文档分析功能实施计划

## 任务清单

### Task 1: 添加依赖
- 在 `requirements.txt` 添加 `pdfplumber>=0.10.0`
- 运行 `pip install pdfplumber`

### Task 2: 后端 - doc_analyzer.py
- 创建 `webapp/backend/doc_analyzer.py`
- 实现 `extract_text_from_pdf(file_bytes) -> str`
- 实现 `extract_text_from_docx(file_bytes) -> str`
- 实现 `analyze_document(text, doc_name) -> str`
- 三重 JSON 解析兜底 + 降级逻辑

### Task 3: 后端 - main.py
- 新增 `UploadDocRequest` 数据模型
- 新增 `POST /api/upload-doc` 端点
- 修改 `GenerateRequest` 添加 `doc_analysis` 字段
- 在 `/api/generate` 中传递 `doc_analysis` 到 `build_user_prompt`

### Task 4: 后端 - prompt_builder.py
- `build_user_prompt()` 新增可选参数 `doc_analysis: str | None = None`
- 在 VOC 之后、专利之前插入文档分析内容

### Task 5: 前端 - types.ts
- 新增 `UploadDocResponse` 接口

### Task 6: 前端 - DocumentStep.tsx
- 新增组件：文件上传区 + 状态管理
- 支持拖拽和点击上传
- 显示分析进度和结果预览

### Task 7: 前端 - App.tsx
- 新增 state：`docAnalysis`
- 流程调整：确认专利 → DocumentStep → 生成报告

### Task 8: 前端 - styles.css
- 新增 DocumentStep 相关样式

### Task 9: 端到端测试
- 启动后端
- 上传测试 PDF/DOCX
- 验证分析结果融入报告
