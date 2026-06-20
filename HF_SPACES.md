# Hugging Face Spaces 免费部署指南

## 为什么 HF Spaces？

- **完全免费**，不是"试用额度用完即停"
- 不会自动休眠（可以设 keep-alive）
- 支持 Docker，Python + Node.js 一把梭
- 16GB RAM，足够跑 AI CHEMIST

限制：构建时间需 < 10 分钟（首次可能需 2-3 次重试才能装上所有依赖），CPU only（没 GPU，但我们不需要）。

---

## 第 1 步：在 HF 创建 Space

1. 打开 [huggingface.co/new-space](https://huggingface.co/new-space)
2. 填表：

| 字段 | 值 |
|------|-----|
| Space name | `ai-chemist` |
| License | `mit` |
| **Space SDK** | **Docker**（关键！不是 Gradio/Streamlit） |
| Docker Template | `Blank` |

3. 点击 **「Create Space」**

此时 HF 会给你一个空仓库，CLI 地址类似：
```
https://huggingface.co/spaces/<你的用户名>/ai-chemist
```

---

## 第 2 步：推送代码到 HF Space

在终端执行：

```bash
cd d:/coding_is_fun/AI_CHEMIST_SKILL_2

# 添加 HF Space 作为第二个 remote
git remote add hf https://huggingface.co/spaces/<你的用户名>/ai-chemist

# 推送到 HF（强制，因为 HF 空仓库有初始 commit）
git push hf master --force
```

> 把 `<你的用户名>` 换成你的 Hugging Face 用户名。比如 `https://huggingface.co/spaces/zhangsan/ai-chemist`

---

## 第 3 步：设置 API Key

1. 打开你的 Space 页面 → **Settings** 标签
2. 找到 **「Repository secrets」**（不是 Environment Variables）
3. 添加：

| Secret name | Value |
|-------------|-------|
| `DEEPSEEK_API_KEY` | `sk-你的key` |

4. 点 Save → Space 自动重启

> 不要填在公开的 Environment Variables 里，那样别人能看到！一定要填在 **Secrets** 里。

---

## 第 4 步：等待构建

1. 切到 **「Builder」** 标签看构建进度
2. 首次构建约 8-12 分钟（下载 Python + Node.js + 依赖）
3. 如果超时失败（>10min），直接点 **「Rebuild」**——之前下载的层会被缓存，第二次快很多
4. Builder 显示绿色的 **「Built」** 就完成了

---

## 第 5 步：访问

打开 `https://huggingface.co/spaces/<你的用户名>/ai-chemist`

或者直接使用 HF 给的嵌入 URL（在 Settings 里可以找到）。

---

## 防止休眠（可选）

HF Spaces 在长时间无请求后可能休眠。可以让 UptimeRobot 每分钟 ping 一次：

1. 打开 [uptimerobot.com](https://uptimerobot.com)（免费注册）
2. Add Monitor → HTTP(s) → URL 填 `https://<用户名>-ai-chemist.hf.space/api/health`
3. 监控间隔选 **5 分钟**（免费版限制）

这样 Space 永远不会休眠。

---

## 更新部署

每次改完代码推送即可：

```bash
git push hf master
```

HF 自动重建。

---

## 速度优化

如果中国访问 HF 慢，可以：

1. 用 Cloudflare Tunnel 给 HF Space 套个自己的域名（免费）
2. 或者直接在代码里加个 nginx 反代（HF Space 不支持，但可以在另一个 VPS 上做）
