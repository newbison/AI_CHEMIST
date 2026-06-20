# R&D 智能报告生成器（Web 版）

在网页端输入 VOC，自动检索专利并生成完整 R&D 智能报告。

## 架构

```
webapp/
├── backend/          # FastAPI 后端
│   ├── main.py              # API 路由（/search, /generate, /health）
│   ├── patent_search.py     # 专利检索（Google Patents → freepatentonline → 中国专利）
│   ├── llm_client.py        # DeepSeek 调用（OpenAI 兼容）
│   ├── prompt_builder.py    # 加载 skill 文件构建 system prompt
│   └── requirements.txt
└── frontend/         # React + Vite 前端
    └── src/
        ├── App.tsx
        ├── components/      # InputStep / PatentsStep / ReportStep / Header
        └── styles.css
```

后端会自动加载上一级的两个 skill 目录（`rd-portfolio-rd-intelligence` 和 `patent-xy-extraction-skill`）的所有 workflow/rubric/template 作为 LLM 的 system prompt。

## 专利检索策略

按优先级回退：
1. **Google Patents**（`xhr/query` JSON 端点）— 优先 US 专利，不足则扩全球
2. **freepatentonline** — HTML 解析兜底
3. **中国专利** — Google Patents 全球结果中过滤 CN

## 快速开始

### 1. 配置 DeepSeek API key

```bash
# 在项目根目录（AI_CHEMIST_SKILL_2/）创建 .env
copy .env.example .env
# 编辑 .env，填入你的 DEEPSEEK_API_KEY
```

### 2. 启动后端

```bash
cd webapp/backend
pip install -r requirements.txt
python main.py
# 后端运行在 http://127.0.0.1:8001
```

### 3. 启动前端

```bash
cd webapp/frontend
npm install
npm run dev
# 前端运行在 http://localhost:5173
```

### 4. 使用

打开 http://localhost:5173
1. 输入 VOC（或点击"填入示例 VOC"）
2. 点击"检索专利"→ 系统自动检索并返回候选列表
3. 勾选要纳入的专利（默认前 8 篇）
4. 点击"生成报告"→ 报告流式输出
5. 完成后可下载 .md 文件

## 依赖

- Python 3.10+
- Node.js 18+
- DeepSeek API key
