# 专利全文获取：代理访问 Google Patents

**日期**: 2026-06-21
**状态**: 已批准，待实施
**方案**: A（最小改动，代理 + 降级）

## 问题陈述

当前系统在分析专利时，`fetch_patent_detail` 因 Google Patents 503 + EPO 403，只能回退到 Google Scholar 的 ~180 字摘要。而两份 skill（`rd-portfolio-rd-intelligence` 和 `patent-xy-extraction-skill`）的 workflow 要求从专利的 Examples/Tables/Test methods 段抽取 X-Y 关系（证据等级 Level 3+），摘要无法提供这些内容。

**后果**：报告 18 章中至少 5 章（6 专利技术抽取、7 测试方法对比、8 X-Y 综合、11 实验组合、12 DOE 细节）必为空或空话。`_report_check.txt` 已实证这一点。

## 根因

用户机器上有 Clash 代理（端口 7890），但 `patent_search.py` 的 `httpx.Client` 未配置代理，导致直连 Google Patents 被 503。

## 解决方案

让 `patent_search.py` 的所有 `httpx.Client` 调用通过本地代理访问 Google Patents，拿到专利全文（Claims + Description + Examples）。

## 设计细节

### 1. 代理配置

在 `patent_search.py` 顶部新增：

```python
_PATENT_PROXY = os.environ.get("PATENT_PROXY", "http://127.0.0.1:7890")
```

- 默认 `http://127.0.0.1:7890`（Clash 默认端口）
- 通过 `PATENT_PROXY` 环境变量可覆盖
- 设为空字符串则禁用代理（直连模式）

### 2. 改动范围

给以下函数中的 `httpx.Client(...)` 调用添加 `proxy=_PATENT_PROXY` 参数：

| 函数 | 作用 | 备注 |
|------|------|------|
| `search_google_patents` | Google Patents 搜索 | 主搜索源 |
| `fetch_patent_detail` 路径1 | Google Patents 全文页 | 拿 Claims+Description |
| `fetch_patent_detail` 路径2 | EPO Espacenet | 通常 403，保持一致 |
| `search_google_scholar` | Google Scholar 兜底 | 走代理更稳定 |
| `search_epo_ops` | EPO OPS API | 保持一致 |

### 3. 降级逻辑（不变）

```
search_by_strategies:
  Google Patents (代理) → 成功则用
  ↓ 失败
  Google Scholar (代理) → 兜底摘要

fetch_patent_detail:
  Google Patents 全文 (代理) → [Claims]+[Description]
  ↓ 失败
  EPO Espacenet (代理) → 通常 403
  ↓ 失败
  Google Scholar → [Abstract] 兜底
```

代理未开启时，行为与当前完全一致。

### 4. 不在本次范围

- LLM `max_tokens=8192` 上限问题（验证报告是否被截断后再处理）
- 本地缓存（方案 B）
- 数据充分性标注（方案 C）
- `prompt_builder` 截断逻辑调整（已有 `_truncate_detail` 保护）

## 验证方案

1. **代理连通性**：`search_google_patents` 走代理返回 200 + 真实结果
2. **全文抓取**：`fetch_patent_detail` 走代理返回含 `[Claims]` + `[Description]` 的 detail_text
3. **降级**：临时清空 `PATENT_PROXY`，确认回退到 Scholar 摘要
4. **端到端**：用真实 VOC 跑完整流程，确认报告 6/7/8 章不再空白

## 风险

- **代理未开启**：用户忘记开 Clash → 行为退化为当前状态（Scholar 摘要），不会崩溃
- **代理速率**：测试显示每篇 ~2.2s，20 篇 ~44s，可接受
- **prompt 超长**：`_truncate_detail` 已有按专利数分配 Description 预算（1500-5000 字符）的保护
