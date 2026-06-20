# Zeabur 部署指南 — AI CHEMIST

## 架构

```
GitHub 仓库 (AI_CHEMIST)
    │
    └── Dockerfile   →  Zeabur 自动检测，构建 Docker 镜像
                         ├── Python 3.11  (FastAPI + uvicorn)
                         ├── Node.js 22   (PptxGenJS 生成 .pptx)
                         ├── React/Vite   (前端构建 → 静态文件)
                         └── ppt-design-skill/  (LLM 设计规范)
```

**一个服务搞定一切**：后端服务同时运行 API 和托管前端静态文件（`SERVE_STATIC=1`）。

---

## 第 1 步：确保 API Key 安全

你的 `DEEPSEEK_API_KEY` **绝对不能**出现在代码或 GitHub 上。

确认 `.gitignore` 中已包含：
```
.env
.env.local
.env.production
```

如果你之前曾把 key 提交到 git，立即去 [DeepSeek 后台](https://platform.deepseek.com/api_keys) **重置密钥**。

---

## 第 2 步：推送到 GitHub

```bash
cd d:/coding_is_fun/AI_CHEMIST_SKILL_2

# 提交所有更改
git add .
git commit -m "feat: PptxGenJS PPT generation + Dockerfile for Zeabur deployment"

# 推送到 GitHub
git push origin master
```

---

## 第 3 步：注册 Zeabur

1. 打开 [zeabur.com](https://zeabur.com)
2. 点击「Sign Up」注册账号
3. 选择「Sign in with GitHub」，授权 Zeabur 访问你的仓库
4. Zeabur 支持**支付宝**支付，无需美国信用卡

---

## 第 4 步：创建服务

1. 进入 Zeabur 控制台，点击 **「Create Project」**
2. 项目名填 `ai-chemist`，点创建
3. 在项目中点击 **「Add Service」**
4. 选择 **「Deploy from GitHub」**
5. 选择仓库 `AI_CHEMIST`
6. Zeabur 会**自动检测到 Dockerfile**，服务类型显示为 Docker
7. 确认以下配置：

| 配置项 | 值 |
|--------|-----|
| **Root Directory** | `.`（仓库根目录） |
| **Branch** | `master` |
| **Service Name** | `ai-chemist`（默认即可） |

8. 点击 **「Deploy」**

构建大约需要 3-5 分钟（首次需要下载依赖）。

---

## 第 5 步：设置环境变量（最重要！）

构建完成后需要设置 API key：

1. 点击服务 → **「Environment Variables」**
2. 添加：

| 变量名 | 值 | 说明 |
|--------|-----|------|
| `DEEPSEEK_API_KEY` | `sk-xxxxxxxxxxxxxxxx` | 你的 DeepSeek API 密钥 |
| `DEEPSEEK_MODEL` | `deepseek-chat` | （可选）模型名 |
| `DEEPSEEK_BASE_URL` | `https://api.deepseek.com` | （可选）API 地址 |

3. 点击 **「Save」** → 服务自动重启

---

## 第 6 步：配置域名

1. 点击服务 → **「Domain」**
2. Zeabur 会生成一个免费子域名：`ai-chemist.zeabur.app`
3. 你也可以绑定自己的域名（可选）
4. HTTPS 自动配置，无需任何操作

---

## 第 7 步：测试

打开浏览器访问 `https://ai-chemist.zeabur.app`（或你的域名）

测试清单：
- [ ] 首页能正常加载（React 前端）
- [ ] 输入 VOC → 点击检索 → 返回专利列表
- [ ] 选择专利 → 生成报告 → 流式输出正常
- [ ] 下载 .docx → 中文正常
- [ ] 下载 .pptx → 中文正常、设计美观（PptxGenJS 生成）
- [ ] 访问 `/api/health` → `{"status":"ok","deepseek_key_set":true}`

---

## 费用预估

| 项目 | 月费 |
|------|------|
| Zeabur 服务器（最小配置 512MB） | **$0 ~ $5** |
| 域名（Zeabur 免费子域名） | **免费** |
| DeepSeek API（按量） | **~¥8-40/月**（取决于使用频率） |

> **省钱技巧**：Zeabur 新用户有 $5 免费额度，够用 1-2 个月。

---

## 故障排查

### 构建失败
1. 看 Zeabur 的构建日志
2. 常见原因：网络超时 → 重新触发 Deploy
3. 磁盘不足 → 检查 `.dockerignore` 是否排除了 `node_modules`

### 服务启动后 502
1. 检查环境变量 `DEEPSEEK_API_KEY` 是否设置
2. 看 Zeabur 日志：`Runtime` → `Logs`
3. 确保端口是 8001（Dockerfile 中已配置）

### PPT 生成失败
1. 检查 Node.js 是否安装：Zeabur 日志中应显示 node 版本
2. 检查 pptxgenjs 是否安装
3. 回退机制：PptxGenJS 失败会自动使用 python-pptx

### 中国网络访问慢
- Zeabur 服务器在海外，中国访问可能有延迟
- 可考虑绑定 CDN（Cloudflare 免费）

---

## 更新部署

每次推送代码到 GitHub `master` 分支，Zeabur 会**自动重新构建和部署**。

```bash
git add .
git commit -m "描述你的更改"
git push origin master
```

无需手动操作 Zeabur 控制台。
