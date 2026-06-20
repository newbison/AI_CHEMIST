<p align="right">
  <a href="README.md">English</a> · <b>中文</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-0.110-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black" alt="React">
  <img src="https://img.shields.io/badge/DeepSeek-V3-4F46E5?style=for-the-badge&logo=openai&logoColor=white" alt="DeepSeek">
  <img src="https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker">
  <img src="https://img.shields.io/badge/PptxGenJS-Powered-FF6B6B?style=for-the-badge&logo=javascript&logoColor=white" alt="PptxGenJS">
</p>

<h1 align="center">⚒️ FORGE AI</h1>
<h3 align="center">The AI-Native R&D Platform — Built by a Chemist, for Materials Scientists & Chemists</h3>

<p align="center">
  <b>输入一句 VOC → 全球专利检索 → AI 逐篇分析 → 一份完整的 R&D 智能报告</b><br>
  包含 X-Y 关系矩阵、矛盾矩阵、DOE 实验设计、风险筛查、组合复制指南<br>
  一键导出 Markdown · Word · <b>AI 设计的 PPT</b>
</p>

---

## 🎯 为什么你需要 FORGE AI？

作为材料科学家或研发工程师，你面对这样的困境：

> *"客户想要一种在电解液中长期浸泡不脱落的胶带。市面上有哪些相关专利？它们的方案是什么？哪些可以借鉴？我应该如何设计实验来验证？"*

传统流程：手动搜索专利（2天）→ 阅读筛选（3天）→ 整理分析（2天）→ 写报告（1天）= **8 天**

**FORGE AI：5 分钟。**

```
  ┌──────────┐     ┌─────────────────┐     ┌──────────────────┐     ┌─────────────┐
  │          │     │                 │     │                  │     │             │
  │   VOC    │ ──▶ │  全球专利检索    │ ──▶ │  AI 逐篇分析      │ ──▶ │  智能报告    │
  │ 客户需求  │     │  6 源自动回退   │     │  抽取 X-Y 关系    │     │  .md .docx  │
  │          │     │                 │     │                  │     │  .pptx      │
  └──────────┘     └─────────────────┘     └──────────────────┘     └─────────────┘
                         │                          │
                         ▼                          ▼
              ┌─────────────────┐     ┌──────────────────────────┐
              │ Google Patents  │     │ 每篇专利提取 10K+ 字符    │
              │ USPTO · EPO     │     │ Abstract · Claims · Desc │
              │ WIPO · Scholar  │     │ 发明人 · 受让人 · 层级标注 │
              └─────────────────┘     └──────────────────────────┘
```

---

## ✨ 功能亮点

### 🌍 全球专利检索 — 无需科学上网

6 级自动回退，Google 被墙时无缝切换到 EPO / WIPO / Google Scholar

| 数据源 | 覆盖范围 | 国内可达 |
|--------|----------|----------|
| Google Patents | 全球 | ⚠️ 需 VPN |
| USPTO PatentsView | 美国 | ✅ |
| EPO Espacenet | 欧洲/全球 | ✅ |
| WIPO Patentscope | 全球 (PCT) | ✅ |
| Google Scholar | 全球学术 | ✅ 常可通 |
| DeepSeek LLM | 训练知识 | ✅ 永远可用 |

每次搜索 20-50 篇，全选或精选前 8 篇。**不是编造的专利号**，每篇都有可追溯的原文链接。

### 🧬 深度专利分析 — 不只是摘要

逐篇抓取专利 **完整文本**（Abstract + Claims + Description，每篇 ~10,000 字符）：

- **X-Y 关系抽取**：从专利中提取 材料/组分/工艺参数 (X) → 性能/效果 (Y) 的因果关系
- **6 级证据层级**：区分 [事实] 专利披露 / [抽取] AI 规范化 / [推断] AI 推断 / [假设] R&D 假设 / [DOE] 实验建议
- **跨专利横向比较**：不同专利的技术方案差异、性能优劣、适用场景对比
- **矛盾矩阵**：识别专利中隐含的技术矛盾（如 粘接力 ↑ vs 耐电解液 ↓）

### 📊 完整 R&D 报告 — 9 步工作流

```
01 项目摄入 → 02 VOC→CTQ → 03 证据挖掘 → 04 专利抽取
→ 05 X-Y 综合 → 06 风险筛查 → 07 DOE 实验设计
→ 08 后实验学习 → 09 组合复制
```

每份报告包含：
- 🎯 **专利优先级列表**：0-50 分评分，附排序理由
- 🧩 **X 字典 / Y 字典**：所有材料参数和性能指标的结构化索引
- 🔀 **X-Y 关系矩阵**：因果关系汇总表
- ⚠️ **风险筛查**：技术可行性 + 专利侵权风险提示（非法律意见）
- 🧪 **DOE 实验组合**：基于专利发现的实验方案建议

### 🎨 AI 设计 PPT — 告别丑陋默认模板

10 种配色方案，4 种字体配对，自动为你的报告生成专业演示文稿：

| 配色 | 适用场景 |
|------|----------|
| Midnight Executive | 正式技术汇报 |
| Forest & Moss | 环保/可持续发展 |
| Ocean Depths | 化学/材料 |
| Sunset Innovation | 创新/创业路演 |
| Coral Energy | 电池/能源 |
| Arctic Professional | 医疗/生物材料 |

---

## 🚀 快速开始

### 前提条件

- Python 3.10+
- Node.js 18+
- DeepSeek API Key（[免费注册](https://platform.deepseek.com/api_keys)，~¥8/100次）

### 第 1 步：克隆 & 配置

```bash
git clone https://github.com/newbison/AI_CHEMIST.git
cd AI_CHEMIST

# 配置 API Key
echo "DEEPSEEK_API_KEY=sk-你的key" > .env
```

### 第 2 步：启动后端

```bash
cd webapp/backend
pip install -r requirements.txt
python main.py
# → 后端运行在 http://localhost:8001
```

### 第 3 步：启动前端

```bash
cd webapp/frontend
npm install
npm run dev
# → 前端运行在 http://localhost:5173
```

打开浏览器访问 `http://localhost:5173`，输入你的 VOC，点击搜索。

---

## 📦 输出格式

| 格式 | 特点 | 生成方式 |
|------|------|----------|
| **.md** | 纯文本，可直接粘贴到飞书/Notion | 直接下载 |
| **.docx** | Word 文档，中文字体优化 | Python 渲染 |
| **.pptx** | AI 设计的演示文稿，高颜值 | PptxGenJS + DeepSeek |

---

## 🐳 Docker 部署

```bash
docker build -t ai-chemist .
docker run -p 8001:8001 -e DEEPSEEK_API_KEY=sk-你的key ai-chemist
```

浏览器打开 `http://localhost:8001`（Docker 内置了生产构建的前端）。

支持一键部署到：
- [Zeabur](ZEABUR.md)（支付宝支付，~$5/月）
- [Hugging Face Spaces](HF_SPACES.md)（完全免费）

---

## 🏗️ 技术栈

| 层 | 技术 |
|----|------|
| **AI 模型** | DeepSeek-Chat (V3) — OpenAI 兼容协议 |
| **后端** | FastAPI + Uvicorn — 异步 SSE 流式输出 |
| **前端** | React 18 + TypeScript + Vite |
| **专利搜索** | httpx 多源并发 + HTML/XML 解析 |
| **Word 导出** | python-docx |
| **PPT 导出** | PptxGenJS (Node.js 子进程) + python-pptx (回退) |
| **容器化** | Docker — Python 3.11 + Node.js 22 多语言镜像 |
| **部署** | Zeabur / Hugging Face Spaces / 任意支持 Docker 的平台 |

---

## 📁 项目结构

```
FORGE_AI/
├── webapp/
│   ├── backend/           # FastAPI 后端
│   │   ├── main.py             # API 路由 (health/search/generate/export)
│   │   ├── patent_search.py    # 6 级回退全球专利检索
│   │   ├── prompt_builder.py   # System/User prompt 构建
│   │   ├── llm_client.py       # DeepSeek SSE 流式客户端
│   │   ├── pptx_export.py      # PPTX 生成 (PptxGenJS + python-pptx)
│   │   └── docx_export.py      # Word 导出
│   └── frontend/           # React + TypeScript 前端
│       └── src/
│           └── components/     # InputStep → PatentsStep → ReportStep
├── rd-portfolio-rd-intelligence/  # 编排器 Skill (9 步 workflow)
├── patent-xy-extraction-skill/    # 抽取器 Skill (10-pass X-Y 提取)
├── ppt-design-skill/              # PPT 设计 Skill (PptxGenJS)
├── Dockerfile                     # 多语言 Docker 镜像
├── ZEABUR.md                      # Zeabur 部署指南
└── HF_SPACES.md                   # Hugging Face 部署指南
```

---

## 🔧 可选配置

| 环境变量 | 说明 | 默认值 |
|----------|------|--------|
| `DEEPSEEK_API_KEY` | DeepSeek API 密钥 | **必需** |
| `DEEPSEEK_MODEL` | 模型名称 | `deepseek-chat` |
| `DEEPSEEK_BASE_URL` | API 地址 | `https://api.deepseek.com` |
| `EPO_OPS_KEY` | EPO 专利 API Key（可选，提升搜索质量） | — |
| `EPO_OPS_SECRET` | EPO 专利 API Secret | — |
| `PATENTS_ALLOW_LLM_FALLBACK` | 允许 LLM 生成专利号（不得已时） | `0` |
| `SERVE_STATIC` | 后端托管前端静态文件 | `0` (开发) / `1` (生产) |

---

## 🤝 贡献

欢迎提 Issue 和 PR！项目目标：

- [ ] 支持更多 LLM（Claude、GPT-4、Qwen）
- [ ] 专利全文 PDF 下载
- [ ] 多语言报告（English / 中文 / 日本語）
- [ ] 实验数据回填（后实验学习闭环）

---

## 📄 License

MIT © 2025 AI CHEMIST

---

<p align="center">
  <sub>Built by a chemist, for materials scientists & chemists.</sub>
</p>
